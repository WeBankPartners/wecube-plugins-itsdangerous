# coding=utf-8
from tests import box_data

from wecube_plugins_itsdangerous.apps.processor import api


def test():
    data = {
        'serviceName': 'qcloud/vm(resource)/action',
        'inputParams': {
            'name': 'destroy'
        },  # , 'script_type': 'shell'
        'scripts': [{
            'content': box_data.script_shell
        }],
        'entityInstances': [{
            'data': {
                'guid': '0032_0000000023'
            }
        }, {
            'data': {
                'guid': '0032_0000000024'
            }
        }]
    }
    assert len(api.Box().check(data, box_data.nocmdb_boxes, handover_match_params=[])) == 7
    assert len(api.Box().check(data, box_data.nocmdb_boxes, handover_match_params=[])) == 7
    data = {
        'serviceName': 'qcloud/vm(resource)/action',
        'inputParams': {
            'name': 'destroy'
        },  # , 'script_type': 'sql'
        'scripts': [{
            'content': box_data.script_sql
        }],
        'entityInstances': [{
            'data': {
                'guid': '0032_0000000023'
            }
        }, {
            'data': {
                'guid': '0032_0000000024'
            }
        }]
    }
    assert len(api.Box().check(data, box_data.nocmdb_boxes, handover_match_params=[])) == 3
    data = {
        'serviceName': 'qcloud/vm(resource)/action',
        'inputParams': {},  # , 'script_type': 'shell'
        'scripts': [{
            'content': box_data.script_shell
        }],
        'entityInstances': [{
            'data': {
                'guid': '0032_0000000025'
            }
        }, {
            'data': {
                'guid': '0032_0000000024'
            }
        }]
    }
    assert len(api.Box().check(data, box_data.nocmdb_boxes, handover_match_params=[])) == 6
