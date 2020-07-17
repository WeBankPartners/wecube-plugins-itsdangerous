# coding=utf-8

from __future__ import absolute_import

from talos.common.controller import CollectionController
from talos.common.controller import ItemController
from wecube_plugins_itsdangerous.apps.processor import api as processor_api


class CollectionPolicy(CollectionController):
    name = 'wecube_plugins_itsdangerous.processor.policy'
    resource = processor_api.Policy


class ItemPolicy(ItemController):
    name = 'wecube_plugins_itsdangerous.processor.policy'
    resource = processor_api.Policy


class CollectionSubject(CollectionController):
    name = 'wecube_plugins_itsdangerous.processor.subject'
    resource = processor_api.Subject


class ItemSubject(ItemController):
    name = 'wecube_plugins_itsdangerous.processor.subject'
    resource = processor_api.Subject
    

class CollectionBox(CollectionController):
    name = 'wecube_plugins_itsdangerous.processor.box'
    resource = processor_api.Box


class ItemBox(ItemController):
    name = 'wecube_plugins_itsdangerous.processor.box'
    resource = processor_api.Box
