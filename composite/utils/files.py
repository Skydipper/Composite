"""Utility functions"""
import json
import os
import datetime
import logging

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)


def load_config_json(name):
    json_path = os.path.abspath(os.path.join(BASE_DIR, 'microservice')) + '/' + name + '.json'
    with open(json_path) as data_file:
        info = json.load(data_file)
    return info


def delete_old_files(path="/opt/composite/tmp_imgs/"):
    """Delete old image files if necessary (>5min old)"""
    flist = os.listdir(path)
    now = datetime.datetime.now().timestamp()
    if len(flist) > 0:
        for file in flist:
            tmp = os.path.getmtime(f'{path}{file}')
            logging.info( f'[Utilities] Removing {path}{file} {tmp}')
            if (now - tmp) > (60 * 5): # 5 min delay on erasure
                print(f'Erasing {path}{file}')
                os.remove(f'{path}{file}')
        return None
    else:
        return None