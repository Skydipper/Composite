import logging
import ee
from shapely.geometry import shape, GeometryCollection


def get_clip_vertex_list(geojson):
    """
    Take a geojson object and return a list of geometry vertices that ee can use as an argument to get thumbs
    """
    tmp_poly = []
    s = GeometryCollection([shape(feature["geometry"]).buffer(0) for feature in geojson.get('features')])
    simple = s[0].simplify(tolerance=0.01, preserve_topology=True)
    try:
        for x, y in zip(simple.exterior.coords.xy[0], simple.exterior.coords.xy[1]):
                                tmp_poly.append([x, y])
    except:
        for x, y in zip(simple[0].exterior.coords.xy[0], simple[0].exterior.coords.xy[1]):
                        tmp_poly.append([x, y])
    return tmp_poly

def get_region(geom):
    """Take a valid geojson object, iterate over all features in that object.
        Build up a list of EE Polygons, and finally return an EE Feature
        collection. New as of 19th Sep 2017 (needed to fix a bug where the old
        function ignored multipolys)
    """
    polygons = []
    for feature in geom.get('features'):
        shape_type = feature.get('geometry').get('type')
        coordinates = feature.get('geometry').get('coordinates')
        if shape_type == 'MultiPolygon':
            polygons.append(ee.Geometry.MultiPolygon(coordinates))
        elif shape_type == 'Polygon':
            polygons.append(ee.Geometry.Polygon(coordinates))
        else:
            pass
    return ee.FeatureCollection(polygons)
