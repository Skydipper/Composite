import logging
import json
import random
import ee
from shapely.geometry import shape, GeometryCollection
from datetime import datetime, timedelta
from composite.errors import CompositeError
from composite.utils.geo import get_clip_vertex_list
from PIL import Image
import rasterio
import numpy as np
import requests

class CompositeService(object):
    """Gets a geostore geometry as input and returns a composite, cloud-free image within the geometry bounds.
    Note that the URLs from Earth Engine expire every 3 days.
    """
    @staticmethod
    def get_composite_image(geojson, instrument, date_range, thumb_size,\
                        band_viz, get_dem, cloudscore_thresh, bbox, get_files):
        """Main worker method for creating composites"""
        result_dic = {}
        try:
            features = geojson.get('features')
            region = [ee.Geometry(feature['geometry']) for feature in features][0]
            clip_region = ee.Geometry({'type': 'Polygon',
                                       'coordinates': [get_clip_vertex_list(geojson)]
                                   })
            clip_bbox = clip_region.bounds()
            geom_list = geojson.get('features')[0].get('geometry').get('coordinates')
            if not date_range:
                dates = CompositeService.get_last_3months()
            else:
                dates = date_range[1:-1].split(',')
            if instrument.lower() == 'landsat':
                sat_img = ee.ImageCollection("LANDSAT/LC08/C01/T1_TOA").filter(ee.Filter.lte('CLOUD_COVER', cloudscore_thresh))
                sat_img = sat_img.filterDate(dates[0].strip(), dates[1].strip()).median()
            elif instrument.lower() == 'sentinel':
                sat_img = ee.ImageCollection('COPERNICUS/S2').filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', cloudscore_thresh))
                sat_img = sat_img.filterBounds(region).filterDate(dates[0].strip(), dates[1].strip()).median()
                sat_img = sat_img.divide(100*100)
            image = sat_img.clip(clip_region).visualize(**band_viz)
            result_dic['thumb_url'] = image.getThumbUrl({'dimensions': thumb_size, 'region': geom_list})
            result_dic['tile_url'] = CompositeService.get_image_url(image)
            if get_dem:
                dem_img = ee.Image('JAXA/ALOS/AW3D30_V1_1').select('AVE').clip(clip_region)
                dem_url = dem_img.getThumbUrl({'dimensions':thumb_size, 'min':-479, 'max':8859.0, 'region': geom_list})
                result_dic['dem'] = dem_url
                if get_files:
                    pass
                else:
                    return result_dic
            if get_files:
                rand_string = str(random.getrandbits(12))
                surface = Image.open(requests.get(result_dic['thumb_url'], stream=True).raw)
                tmp_file = f"/opt/composite/tmp_imgs/{rand_string}.png"
                surface.save(tmp_file)
                if get_dem:
                    transform = rasterio.transform.from_bounds(*bbox, *thumb_size)
                    dem_array_band = np.array(Image.open(requests.get(result_dic['dem'], stream=True).raw))[:, :, 0]
                    dem_file = f'/opt/composite/tmp_imgs/{rand_string}.tif'
                    with rasterio.open(dem_file, 'w',
                                        driver='GTiff',
                                        dtype= rasterio.uint8,
                                        count= 1,
                                        width= thumb_size[0],
                                        height= thumb_size[1],
                                        transform= transform
                                    ) as dst:
                                        dst.write(dem_array_band, indexes=1)
                return {'surface_png': tmp_file, 'rand_string': rand_string, 'dem_tif': dem_file}
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
