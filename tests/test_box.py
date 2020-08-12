# coding=utf-8
from tests import box_data
from wecube_plugins_itsdangerous.apps.processor import api
from wecube_plugins_itsdangerous.server.wsgi_server import application


def test():
    data = {
        'serviceName': 'qcloud/vm(resource)/action',
        'inputParams': {
            'script': box_data.script_shell,
            'name': 'destroy'
        },  # , 'script_type': 'shell'
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
    assert len(api.Box().check(data, box_data.complex_boxes)) == 7
    assert len(api.Box().check(data, box_data.complex_boxes)) == 7
    data = {
        'serviceName': 'qcloud/vm(resource)/action',
        'inputParams': {
            'script': box_data.script_sql,
            'name': 'destroy'
        },  # , 'script_type': 'sql'
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
    assert len(api.Box().check(data, box_data.complex_boxes)) == 3
    data = {
        'serviceName': 'qcloud/vm(resource)/action',
        'inputParams': {
            'script': box_data.script_shell
        },  # , 'script_type': 'shell'
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
    assert len(api.Box().check(data, box_data.complex_boxes)) == 0
