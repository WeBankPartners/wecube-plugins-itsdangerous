# coding=utf-8

from __future__ import absolute_import

from wecube_plugins_itsdangerous.apps.processor import controller


def add_routes(api):
    api.add_route('/itsdangerous/ui/v1/boxes', controller.CollectionBox())
    api.add_route('/itsdangerous/ui/v1/boxes/{rid}', controller.ItemBox())
