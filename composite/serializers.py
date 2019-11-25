"""Serializers"""
import logging


def serialize_composite_output(analysis, type):
    """."""
    return {
        'id': None,
        'type': type,
        'attributes': {
            'thumb_url': analysis.get('thumb_url', None),
            'tile_url':analysis.get('tile_url', None),
            'dem':analysis.get('dem', None),
            'zonal_stats':analysis.get('zonal_stats', None)
        }
    }