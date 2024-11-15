# coding=utf-8

from __future__ import absolute_import

from wecube_plugins_itsdangerous.apps.processor import controller


def add_routes(api):
    # policy
    api.add_route('/itsdangerous/ui/v1/policies', controller.CollectionPolicy())
    api.add_route('/itsdangerous/ui/v1/policies/{rid}', controller.ItemPolicy())
    # rule
    api.add_route('/itsdangerous/ui/v1/rules', controller.CollectionRule())
    api.add_route('/itsdangerous/ui/v1/rules/{rid}', controller.ItemRule())
    # matchparam
    api.add_route('/itsdangerous/ui/v1/matchparams', controller.CollectionMatchParam())
    api.add_route('/itsdangerous/ui/v1/matchparams/{rid}', controller.ItemMatchParam())
    api.add_route('/itsdangerous/ui/v1/matchparams/{rid}/args', controller.ItemMatchParamArgs())
    # subject
    api.add_route('/itsdangerous/ui/v1/subjects', controller.CollectionSubject())
    api.add_route('/itsdangerous/ui/v1/subjects/{rid}', controller.ItemSubject())
    # target
    api.add_route('/itsdangerous/ui/v1/targets', controller.CollectionTarget())
    api.add_route('/itsdangerous/ui/v1/targets/{rid}', controller.ItemTarget())
    # service script
    api.add_route('/itsdangerous/ui/v1/service-scripts', controller.CollectionServiceScript())
    api.add_route('/itsdangerous/ui/v1/service-scripts/{rid}', controller.ItemServiceScript())
    # box
    api.add_route('/itsdangerous/ui/v1/boxes', controller.CollectionBox())
    api.add_route('/itsdangerous/ui/v1/boxes/{rid}', controller.ItemBox())
    api.add_route('/itsdangerous/ui/v1/boxes/{rid}/run', controller.BoxRun())
    # batch execution detection for platform batch & workflow
    api.add_route('/itsdangerous/v1/batch_execution_detection', controller.PluginCheck())
    # script detection for terminal plugin[Need to manually assemble the scripts field]
    api.add_route('/itsdangerous/v1/detection', controller.ScriptCheck())
    # service
    api.add_route('/itsdangerous/v1/platform/services', controller.WecubeService())
    # service param
    api.add_route('/itsdangerous/v1/platform/service-attributes', controller.WecubeServiceAttribute())
