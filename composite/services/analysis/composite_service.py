import logging
import json
import ee
from shapely.geometry import shape, GeometryCollection
from datetime import datetime, timedelta
from composite.errors import CompositeError
from composite.utils.geo import get_clip_vertex_list

class CompositeService(object):
    """Gets a geostore geometry as input and returns a composite, cloud-free image within the geometry bounds.
    Note that the URLs from Earth Engine expire every 3 days.
    """
    @staticmethod
    def get_composite_image(geojson, instrument, date_range, thumb_size,\
                        band_viz, get_dem, cloudscore_thresh):
        """blah"""
        logging.info(f"[COMPOSITE SERVICE]: Creating composite")
        logging.info(f"[COMPOSITE SERVICE] EE LIB {ee.__version__}")
        result_dic = {}
        try:
            features = geojson.get('features')
            region = [ee.Geometry(feature['geometry']) for feature in features][0]
            clip_region = ee.Geometry({'type': 'Polygon',
                                       'coordinates': [get_clip_vertex_list(geojson)]
                                   })
            if not date_range:
                dates = CompositeService.get_last_3months()
            dates = date_range[1:-1].split(',')
            logging.info(f"[COMPOSITE SERVICE] INSTRUMENT {instrument}")
            logging.info(f"[COMPOSITE SERVICE] Dates {dates}")
            if instrument.lower() == 'landsat':
                sat_img = ee.ImageCollection("LANDSAT/LC08/C01/T1_TOA").filter(ee.Filter.lte('CLOUD_COVER', cloudscore_thresh))
                sat_img = sat_img.filterDate(dates[0].strip(), dates[1].strip()).median()
                logging.info(f"[COMPOSITE SERVICE]: Sat image 1")
            elif instrument.lower() == 'sentinel':
                sat_img = ee.ImageCollection('COPERNICUS/S2').filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', cloudscore_thresh))
                sat_img = sat_img.filterBounds(region).filterDate(dates[0].strip(), dates[1].strip()).median()
                sat_img = sat_img.divide(100*100)
                logging.info(f"[COMPOSITE SERVICE]: Sat image 2")
            logging.info(f"[COMPOSITE SERVICE]: Sat image 3")
            image = sat_img.visualize(**band_viz)
            result_dic['thumb_url'] = image.getThumbUrl({'dimensions': thumb_size, 'region': region})
            result_dic['tile_url'] = CompositeService.get_image_url(image.clip(clip_region))
            if get_dem:
                dem_img = ee.Image('JAXA/ALOS/AW3D30_V1_1').select('AVE')
                dem_url = dem_img.getThumbUrl({'dimensions':thumb_size, 'min':-479, 'max':8859.0, 'region': region})
                result_dic['dem'] = dem_url
            return result_dic
        except Exception as error:
            logging.error(str(error))
            raise CompositeError(message=f'Error in composite imaging {error}')

    @staticmethod
    def get_last_3months():
        date_weeks_ago = datetime.now() - timedelta(weeks=21)
        date_weeks_ago = date_weeks_ago.strftime("%Y-%m-%d")
        return [date_weeks_ago, datetime.today().strftime('%Y-%m-%d')]

    @staticmethod
    def get_image_url(source):
        """
        Returns a tile url for image
        """
        d = source.getMapId()
        base_url = 'https://earthengine.googleapis.com'
        url = (base_url + '/map/' + d['mapid'] + '/{z}/{x}/{y}?token=' + d['token'])
        return url
