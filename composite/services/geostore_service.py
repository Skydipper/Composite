"""Geostore SERVICE"""
from CTRegisterMicroserviceFlask import request_to_microservice
from composite.errors import GeostoreNotFound
import logging


class GeostoreService(object):
    """Helper class to return Geostore objects"""

    @staticmethod
    def execute(config):
        d={}
        try:
            response = request_to_microservice(config)
        except Exception as e:
            raise Exception(str(e))
        if response.get('errors'):
            error = response.get('errors')[0]
            if error.get('status') == 404:
                raise GeostoreNotFound(message='')
            else:
                raise Exception(error.get('detail'))
        geostore = response.get('data', None).get('attributes', None)
        d['geojson'] = geostore.get('geojson', None)
        d['area_ha'] = geostore.get('areaHa', None)
        d['bbox'] = geostore.get('bbox', None)
        return d

    @staticmethod
    def get(geostore):
        config = {
            'uri': '/geostore/' + geostore,
            'method': 'GET'
        }
        return GeostoreService.execute(config)
