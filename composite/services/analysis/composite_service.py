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
        try:
            features = geojson.get('features')
 #           region = [ee.Geometry(feature['geometry']) for feature in features][0]
            region = ee.Geometry({
                'type': 'Polygon',
                'coordinates': [get_clip_vertex_list(geojson)]
            })
            logging.info(f'\n[COMPOSITE SERVICE] DATE RANGE 1: {date_range}')
            if not date_range:
                date_range = CompositeService.get_last_3months()
            else:
                date_range = date_range[1:-1].split(',')
            logging.info(f'\n[COMPOSITE SERVICE] DATE RANGE 2: {date_range}')
            sat_img = CompositeService.get_sat_img(instrument, region, date_range, cloudscore_thresh)
            image = sat_img.visualize(**band_viz)
            tmp_thumb = image.getThumbUrl({'dimensions': thumb_size})
            tmp_tile = CompositeService.get_image_url(image)
            result_dic = {'thumb_url': tmp_thumb,
                            'tile_url': tmp_tile}
            logging.error(f'[Composite Service]: result_dic {result_dic}')
            if get_dem:
                dem_img = ee.Image('JAXA/ALOS/AW3D30_V1_1').select('AVE').clip(region)
                #getThumbUrl({'region':region, 'dimensions':thumb_size,\
                #        'min':-479, 'max':8859.0})
                dem_url = dem_img.getThumbUrl({'dimensions':thumb_size, 'min':-479, 'max':8859.0})
                result_dic['dem'] = dem_url
            return result_dic
        except Exception as error:
            logging.error(str(error))
            raise CompositeError(message='Error in composite imaging')

    @staticmethod
    def get_last_3months():
        date_weeks_ago = datetime.now() - timedelta(weeks=21)
        date_weeks_ago = date_weeks_ago.strftime("%Y-%m-%d")
        return [date_weeks_ago, datetime.today().strftime('%Y-%m-%d')]


    @staticmethod
    def get_sat_img(instrument, region, date_range, cloudscore_thresh):
        if(instrument == 'landsat'):
            sat_img = ee.ImageCollection("LANDSAT/LC08/C01/T1_TOA").filter(ee.Filter.lte('CLOUD_COVER', cloudscore_thresh))
        else:
            sat_img = ee.ImageCollection('COPERNICUS/S2').filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', cloudscore_thresh))
        sat_img = sat_img.filterBounds(region).filterDate(date_range[0].strip(), date_range[1].strip())\
                    .median().clip(region)
        if(instrument == 'sentinel'):
            sat_img = sat_img.divide(100*100)
        return sat_img

    @staticmethod
    def get_image_url(source):
        """
        Returns a tile url for image
        """
        d = source.getMapId()
        base_url = 'https://earthengine.googleapis.com'
        url = (base_url + '/map/' + d['mapid'] + '/{z}/{x}/{y}?token=' + d['token'])
        return url
