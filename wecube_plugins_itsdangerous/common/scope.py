# coding=utf-8

from __future__ import absolute_import

import logging
import datetime

from talos.common import cache
from talos.core import config

from wecube_plugins_itsdangerous.common import expression
from wecube_plugins_itsdangerous.common import jsonfilter
from wecube_plugins_itsdangerous.common import utils

CONF = config.CONF
LOG = logging.getLogger(__name__)
WECUBE_TOKEN = 'wecube_platform_token'


class JsonScope(object):
    def __init__(self, expr):
        self.filters = expression.expr_filter_parse(expr)

    def is_match(self, data):
        '''
        check if data match all filters(from expression)
        :param data: dict
        '''
        if data is None:
            return False
        return jsonfilter.match_all(self.filters, data)


def get_wecube_token(base_url):
    token = CONF.wecube.token
    if not CONF.wecube.use_token:
        token = cache.get(WECUBE_TOKEN)
        if not cache.validate(token):
            token = utils.RestfulJson.post(base_url + '/auth/v1/api/login',
                                           json={
                                               "username": CONF.wecube.username,
                                               "password": CONF.wecube.password
                                           }).json()['data'][1]['token']
            cache.set(WECUBE_TOKEN, token)
    return token


def wecube_expr_query(expr):
    base_url = CONF.wecube.base_url
    token = get_wecube_token(base_url)
    cache_key = 'wecube/expr/%s' % expr
    results = cache.get(cache_key, exipres=3)
    if not cache.validate(results):
        LOG.debug('wecube_expr_query POST /platform/v1/data-model/dme/integrated-query with %s' % expr)
        cost_start = datetime.datetime.now()
        resp = utils.RestfulJson.post(base_url + '/platform/v1/data-model/dme/integrated-query',
                                      json={
                                          'dataModelExpression': expr,
                                          'filters': []
                                      },
                                      headers={'Authorization': 'Bearer ' + token})
        cost_end = datetime.datetime.now()
        LOG.debug('wecube_expr_query time cost %s' % (cost_end - cost_start))
        results = resp['data'] or []
        cache.set(cache_key, results)
    LOG.debug('wecube_expr_query result length: %s' % len(results))
    return results


class WeCubeScope(object):
    def __init__(self, expr):
        self.expression = expr

    def is_match(self, data):
        '''
        check if wecube data(from expression) contains any item from data 
        :param data: [{...}]
        '''
        if data is None:
            return False
        # NOTE: (roy) change this if instance structure changed
        input_guids = [d['id'] for d in data]
        if input_guids:
            try:
                expression.expr_parse(self.expression)
            except ValueError as e:
                LOG.exception(e)
            else:
                results = wecube_expr_query(self.expression)
                expr_guids = [d['id'] for d in results]
                if set(input_guids) & set(expr_guids):
                    return True
        return False