# coding=utf-8

from __future__ import absolute_import

from wecube_plugins_itsdangerous.apps.plugin import controller


def add_routes(api):
    # plugin box
    api.add_route('/itsdangerous/v1/batch_execution_detection', controller.ControllerBox())
