# coding=utf-8

from __future__ import absolute_import

from wecube_plugins_itsdangerous.apps.plugin import controller


def add_routes(api):
    # plugin box[not use]
    api.add_route('/itsdangerous/v1/detection', controller.ControllerBox())
