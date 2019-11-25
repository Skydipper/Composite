"""-"""
import os
from composite.utils.files import BASE_DIR, PROJECT_DIR

SETTINGS = {
    'logging': {
        'level': 'DEBUG'
    },
    'service': {
        'port': 4505
    },
    'gee': {
        'service_account': 'skydipper@skydipper-196010.iam.gserviceaccount.com',
        'privatekey_file': BASE_DIR + '/privatekey.json',
        'assets': {},
    }
}
