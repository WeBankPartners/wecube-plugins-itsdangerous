# coding=utf-8

from __future__ import absolute_import

import logging
import requests

from talos.common import cache
from talos.core import config

from wecube_plugins_itsdangerous.common import expression
from wecube_plugins_itsdangerous.common import jsonfilter

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


def get_token(base_url):
    token = CONF.wecube_platform.token
    if not CONF.wecube_platform.use_token:
        token = cache.get(WECUBE_TOKEN)
        if not cache.validate(token):
            token = requests.post(base_url + '/auth/v1/api/login',
                                  json={
                                      "username": CONF.wecube_platform.username,
                                      "password": CONF.wecube_platform.password
                                  }).json()['data'][1]['token']
            cache.set(WECUBE_TOKEN, token)
    return token


def wecube_ci_getter(expr_data, is_backref, guids, ci_mapping=None):
    base_url = CONF.wecube_platform.base_url
    token = get_token(base_url)
    data = {'filters': expr_data['filters']}
    # build json filters
    if guids is not None:
        if is_backref:
            data['filters'].append({'name': expr_data['backref_attribute'], 'operator': 'in', 'value': guids})
        else:
            data['filters'].append({'name': 'id', 'operator': 'in', 'value': guids})
    ci_data_key = 'wecube/ci/%(ci)s' % {'ci': expr_data['ci']}
    results = cache.get(ci_data_key, exipres=3)
    if not cache.validate(results):
        LOG.debug('wecube_ci_getter POST /platform/v1/data-model/dme/integrated-query with %s' % expr_data['ci'])
        LOG.debug('wecube_ci_getter     filters: %s', data)
        resp = requests.post(base_url + '/platform/v1/data-model/dme/integrated-query',
                             json={
                                 'dataModelExpression': expr_data['expr'],
                                 'filters': []
                             },
                             headers={'Authorization': 'Bearer ' + token})
        results = resp.json()['data'] or []
        LOG.debug('wecube_ci_getter get %s result(all) length: %s' % (expr_data['ci'], len(results)))
        cache.set(ci_data_key, results)
    results = [ret for ret in results if jsonfilter.match_all(data['filters'], ret['data'])]
    LOG.debug('wecube_ci_getter get %s result(filter) length: %s' % (expr_data['ci'], len(results)))
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
        input_ci_id = None
        if input_guids:
            try:
                expr_groups = expression.expr_parse(self.expression)
            except ValueError as e:
                LOG.exception(e)
            else:
                results = expression.expr_query(self.expression, wecube_ci_getter, None)
                expr_guids = [d['id'] for d in results]
                if set(input_guids) & set(expr_guids):
                    return True
        return False