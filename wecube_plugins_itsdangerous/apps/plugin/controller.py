# coding=utf-8

from __future__ import absolute_import

import falcon
from talos.common import controller

from wecube_plugins_itsdangerous.apps.plugin import api as plugin_api
from wecube_plugins_itsdangerous.db import resource


class ControllerBox(controller.Controller):
    allow_methods = ('POST', )

    def on_post(self, req, resp, **kwargs):
        self._validate_method(req)
        self._validate_data(req)
        resp.json = self.create(req, req.json, **kwargs)
        resp.status = falcon.HTTP_200

    def create(self, req, data):
        '''
        input data:
        {
            "requestId": "request-001",  //仅异步调用需要用到
            "operator": "admin",  //操作人
            "serviceName": "a/b(c)/d"
            "inputs": [  
                {"callbackParameter": "", "xml define prop": xxx},
                {},
                {}
            ]
        }
        
        output data:
        {
            "resultCode": "0",  //调用插件结果，"0"代表调用成功，"1"代表调用失败
            "resultMessage": "success",  //调用结果信息，一般用于调用失败时返回失败信息
            "results": {
                "outputs": [
                    {"callbackParameter": "", "errorCode": "", "errorMessage": "", "xml define prop": xxx},
                    {},
                    {}
                ]
            }
        }
        '''
        output_rets = plugin_api.Box().check(data)
        for idx, output in enumerate(output_rets):
            output['callbackParameter'] = data['inputs'][idx]['callbackParameter']
            output['errorCode'] = "0"
            output['errorMessage'] = "success"
        ret = {'resultCode': '0', 'resultMessage': 'success', 'results': {'outputs': output_rets}}
        return ret
