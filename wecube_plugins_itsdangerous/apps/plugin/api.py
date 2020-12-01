# coding=utf-8

from __future__ import absolute_import

import logging

from talos.core import config
from talos.db import crud
from wecube_plugins_itsdangerous.db import validator as my_validator

LOG = logging.getLogger(__name__)
CONF = config.CONF


class Box(object):
    data_rules = [
        crud.ColumnValidator(field='requestId',
                             rule=my_validator.LengthValidator(0, 63),
                             validate_on=['check:O'],
                             nullable=True),
        crud.ColumnValidator(field='operator',
                             rule=my_validator.LengthValidator(0, 63),
                             validate_on=['check:O'],
                             nullable=True),
        crud.ColumnValidator(field='serviceName',
                             rule=my_validator.LengthValidator(1, 255),
                             validate_on=['check:M'],
                             nullable=False),
        crud.ColumnValidator(field='servicePath',
                             rule=my_validator.LengthValidator(0, 255),
                             validate_on=['check:O'],
                             nullable=True),
        crud.ColumnValidator(field='entityInstances',
                             rule=my_validator.TypeValidator(list),
                             validate_on=['check:M'],
                             nullable=False),
        crud.ColumnValidator(field='inputs',
                             rule=my_validator.TypeValidator(list),
                             validate_on=['check:M'],
                             nullable=False),
    ]

    def check(self, data):
        '''
        input data:
        {
            "requestId": "request-001",  //仅异步调用需要用到
            "operator": "admin",  //操作人
            "serviceName": "a/b(c)/d"
            "servicePath": "a/b/run"
            "entityInstances": [{"id": "xxx_xxxxxx"}]
            "inputs": [
                {"callbackParameter": "", "xml define prop": xxx},
                {},
                {}
            ]
        }
        '''
        from wecube_plugins_itsdangerous.apps.processor import api as processor_api
        results = []
        box = processor_api.Box()
        clean_data = crud.ColumnValidator.get_clean_data(self.data_rules, data, 'check')
        service = clean_data['serviceName']
        entity_instances = clean_data['entityInstances']
        input_params = clean_data['inputs']
        for input_param in input_params:
            detect_data = {
                'serviceName': service,
                'servicePath': clean_data.get('servicePath', None),
                'inputParams': input_param,
                'scripts': processor_api.ServiceScript().get_contents(service, input_param),
                'entityInstances': entity_instances
            }
            input_results = box.check(detect_data)
            results.append({'is_danger': len(input_results) > 0, 'details': input_results})
        return results
