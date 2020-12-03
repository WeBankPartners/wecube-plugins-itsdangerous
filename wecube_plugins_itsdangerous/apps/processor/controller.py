# coding=utf-8

from __future__ import absolute_import
from wecube_plugins_itsdangerous.apps.processor import api as processor_api
from wecube_plugins_itsdangerous.common import controller


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


class ItemMatchParamArgs(controller.Collection):
    name = 'wecube_plugins_itsdangerous.processor.matchparam.args'
    resource = processor_api.MatchParam

    def list(self, req, criteria, **kwargs):
        return self.make_resource(req).get_args(**kwargs)

    def count(self, req, criteria, results=None, **kwargs):
        results = results or []
        return len(results)


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


class CollectionServiceScript(controller.Collection):
    name = 'wecube_plugins_itsdangerous.processor.servicescript'
    resource = processor_api.ServiceScript


class ItemServiceScript(controller.Item):
    name = 'wecube_plugins_itsdangerous.processor.servicescript'
    resource = processor_api.ServiceScript


class CollectionBox(controller.Collection):
    name = 'wecube_plugins_itsdangerous.processor.box'
    resource = processor_api.BoxManage


class ItemBox(controller.Item):
    name = 'wecube_plugins_itsdangerous.processor.box'
    resource = processor_api.BoxManage


class BoxRun(controller.Controller):
    allow_methods = ('POST', )
    name = 'wecube_plugins_itsdangerous.processor.box.run'
    resource = processor_api.Box

    def create(self, req, data, **kwargs):
        return self.make_resource(req).simplerun(data, **kwargs)


class PluginCheck(controller.Controller):
    allow_methods = ('POST', )
    name = 'wecube_plugins_itsdangerous.processor.box.plugin_check'
    resource = processor_api.Box

    def create(self, req, data, **kwargs):
        return self.make_resource(req).plugin_check(data, **kwargs)


class WecubeService(controller.Collection):
    allow_methods = ('GET', )
    name = 'wecube_plugins_itsdangerous.processor.wecube.services'
    resource = processor_api.WecubeService

    def count(self, req, criteria, results=None, **kwargs):
        results = results or []
        return len(results)
