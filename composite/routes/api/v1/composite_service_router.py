"""Router for compositing"""
import logging
from flask import jsonify, Blueprint
import json
from composite.routes.api import error
from composite.services.analysis.composite_service import CompositeService
from composite.errors import CompositeError
from composite.serializers import serialize_composite_output
from composite.middleware import get_geo_by_hash, get_composite_params


composite_service_v1 = Blueprint('composite_service_v1', __name__)

def composite_maker(geojson, instrument, date_range, thumb_size, band_viz, get_dem, cloudscore_thresh):
    """
    Get a composite satellite image for a geostore id .
    """
    try:
        logging.info(f'\n[ROUTER] DATE RANGE 2 : {date_range}')
        data = CompositeService.get_composite_image(geojson=geojson, instrument=instrument,\
                                                    date_range=date_range, thumb_size=thumb_size, \
                                                    band_viz=band_viz, get_dem=get_dem,\
                                                    cloudscore_thresh=cloudscore_thresh)
        logging.info(f"[ROUTER]: Result {data}")
    except CompositeError as e:
        logging.error(f'[ROUTER]: {e.message}')
        return error(status=500, detail=e.message)
    return jsonify(serialize_composite_output(data, 'composite_service')), 200


@composite_service_v1.route('/', strict_slashes=False, methods=['GET'])
@get_geo_by_hash
@get_composite_params
def get_by_hash(geojson, instrument, date_range, thumb_size, band_viz, get_dem, cloudscore_thresh):
    """Get composite image for given geostore"""
    logging.info('[ROUTER]: Getting area by id hash')
    logging.info(f'\n[ROUTER] DATE RANGE 1: {date_range}')
    return composite_maker(geojson=geojson, instrument=instrument, date_range=date_range,
                             thumb_size=thumb_size, band_viz=band_viz, get_dem=get_dem,
                             cloudscore_thresh=cloudscore_thresh)