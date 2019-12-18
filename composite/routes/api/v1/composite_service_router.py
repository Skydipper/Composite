"""Router for compositing"""
import logging
from flask import jsonify, Blueprint, send_file, send_from_directory
import json
from composite.routes.api import error
from composite.services.analysis.composite_service import CompositeService
from composite.errors import CompositeError
from composite.serializers import serialize_composite_output
from composite.middleware import get_geo_by_hash, get_composite_params
from zipfile import ZipFile


composite_service_v1 = Blueprint('composite_service_v1', __name__)

def composite_maker(geojson, instrument, date_range, thumb_size, band_viz, get_dem, cloudscore_thresh,
                    bbox, get_files):
    """
    Get a composite satellite image for a geostore id .
    """
    try:
        logging.info(f'\n[ROUTER] DATE RANGE 2 : {date_range}')
        data = CompositeService.get_composite_image(geojson=geojson, instrument=instrument,
                                                    date_range=date_range, thumb_size=thumb_size,
                                                    band_viz=band_viz, get_dem=get_dem,
                                                    cloudscore_thresh=cloudscore_thresh, bbox=bbox,
                                                    get_files=get_files)
        logging.info(f"[ROUTER]: Result {data}")
    except CompositeError as e:
        logging.error(f'[ROUTER]: {e.message}')
        return error(status=500, detail=e.message)
    if get_files:
        try:
            zipFile = f"/opt/composite/tmp_imgs/{data.get('rand_string')}.zip"
            with ZipFile(zipFile, 'w') as zipObj:
                zipObj.write(data.get('surface_png'), arcname=f"{data.get('rand_string')}.png")
                zipObj.write(data.get('surface_png'), arcname=f"{data.get('rand_string')}.tif")
            return send_file(zipFile, attachment_filename='surface.zip')
            #return send_file(data.get('surface_png'), attachment_filename='surface.png')
            #return send_from_directory('/opt/composite/tmp_imgs/', data.get('surface_png'), 'surface.png')
        except Exception as e:
            return error(status=500, detail=e.message)
    else:
        return jsonify(serialize_composite_output(data, 'composite_service')), 200


@composite_service_v1.route('/', strict_slashes=False, methods=['GET'])
@get_geo_by_hash
@get_composite_params
def get_by_hash(geojson, instrument, date_range, thumb_size, band_viz, get_dem, cloudscore_thresh,
                 bbox, get_files):
    """Get composite image for given geostore"""
    logging.info('[ROUTER]: Getting area by id hash')
    logging.info(f'\n[ROUTER] DATE RANGE 1: {date_range}')
    logging.info(f'\n[ROUTER] get_files: {get_files}')
    return composite_maker(geojson=geojson, instrument=instrument, date_range=date_range,
                             thumb_size=thumb_size, band_viz=band_viz, get_dem=get_dem,
                             cloudscore_thresh=cloudscore_thresh, bbox=bbox, get_files=get_files)