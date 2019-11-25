"""MIDDLEWARE"""

from flask import request
from functools import wraps
import json
import logging
from composite.errors import GeostoreNotFound
from composite.routes.api import error
from composite.services.area_service import AreaService
from composite.services.geostore_service import GeostoreService


def get_geo_by_hash(func):
    """Get geodata"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.method == 'GET':
            geostore = request.args.get('geostore')
            if not geostore:
                return error(status=400, detail='Geostore is required')
            try:
                d = GeostoreService.get(geostore)
            except GeostoreNotFound:
                return error(status=404, detail='Geostore not found')
        kwargs["geojson"] = d['geojson']
        return func(*args, **kwargs)
    return wrapper

def get_composite_params(func):
    """Get instrument"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.method in ['GET','POST']:
            instrument = request.args.get('instrument', False)
            if not instrument:
                instrument = 'landsat'
            date_range = request.args.get('date_range', False)
            thumb_size = request.args.get('thumb_size', False)
            if not thumb_size:
                thumb_size = [500, 500]
            band_viz = request.args.get('band_viz', False)
            if not band_viz:
                band_viz = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.4}
            else:
                band_viz = json.loads(band_viz)
            get_dem = request.args.get('get_dem', False)
            if get_dem and get_dem.lower() == 'true':
                get_dem = True
            else:
                get_dem = False
            cloudscore_thresh = request.args.get('cloudscore_thresh', False)
            if not cloudscore_thresh:
                cloudscore_thresh = 5
            else:
                cloudscore_thresh = int(cloudscore_thresh)
        logging.info(f"[Middleware] DATE RANGE: {date_range}")
        kwargs['get_dem'] = get_dem
        kwargs['thumb_size'] = thumb_size
        kwargs['date_range'] = date_range
        kwargs['instrument'] = instrument
        kwargs['band_viz'] = band_viz
        kwargs['cloudscore_thresh'] = cloudscore_thresh
        return func(*args, **kwargs)
    return wrapper
