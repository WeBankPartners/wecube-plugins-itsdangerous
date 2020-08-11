# coding=utf-8

from __future__ import absolute_import

from wecube_plugins_itsdangerous.common import controller
from wecube_plugins_itsdangerous.apps.processor import api as processor_api


class CollectionPolicy(controller.Collection):
    name = 'wecube_plugins_itsdangerous.processor.policy'
    resource = processor_api.Policy


class ItemPolicy(controller.Item):
    name = 'wecube_plugins_itsdangerous.processor.policy'
    resource = processor_api.Policy


class CollectionRule(controller.Collection):
    name = 'wecube_plugins_itsdangerous.processor.rule'
    resource = processor_api.Rule


class ItemRule(controller.Item):
    name = 'wecube_plugins_itsdangerous.processor.rule'
    resource = processor_api.Rule


class CollectionMatchParam(controller.Collection):
    name = 'wecube_plugins_itsdangerous.processor.matchparam'
    resource = processor_api.MatchParam


class ItemMatchParam(controller.Item):
    name = 'wecube_plugins_itsdangerous.processor.matchparam'
    resource = processor_api.MatchParam


class CollectionSubject(controller.Collection):
    name = 'wecube_plugins_itsdangerous.processor.subject'
    resource = processor_api.Subject


class ItemSubject(controller.Item):
    name = 'wecube_plugins_itsdangerous.processor.subject'
    resource = processor_api.Subject


class CollectionTarget(controller.Collection):
    name = 'wecube_plugins_itsdangerous.processor.target'
    resource = processor_api.Target


class ItemTarget(controller.Item):
    name = 'wecube_plugins_itsdangerous.processor.target'
    resource = processor_api.Target


class CollectionBox(controller.Collection):
    name = 'wecube_plugins_itsdangerous.processor.box'
    resource = processor_api.Box


class ItemBox(controller.Item):
    name = 'wecube_plugins_itsdangerous.processor.box'
    resource = processor_api.Box
