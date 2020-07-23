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
            return True
        return jsonfilter.match_all(self.filters, data)


def get_token(base_url):
    token = CONF.wecube_platform.token
    if not CONF.wecube_platform.use_token:
        token = cache.get(WECUBE_TOKEN)
        if not cache.validate(token):
            token = requests.post(base_url + '/auth/v1/api/login',
                              json={"username":CONF.wecube_platform.username,
                                    "password":CONF.wecube_platform.password}).json()['data'][1]['token']
            cache.set(WECUBE_TOKEN, token)
    return token


def wecmdb_ci_getter(expr_data, is_backref, guids, ci_mapping):
    base_url = CONF.wecube_platform.base_url
    token = get_token(base_url)
    data = {
        'filters': expr_data['filters']
    }
    # build json filters
    if guids is not None:
        if is_backref:
            data['filters'].append({'name': expr_data['backref_attribute'] + '.guid', 'operator': 'in', 'value': guids})
        else:
            data['filters'].append({'name': 'guid', 'operator': 'in', 'value': guids})
    ci_data_key = 'wecmdb/ci-types/%(ci)s' % {'ci': ci_mapping[expr_data['ci']]}
    results = cache.get(ci_data_key, exipres=30)
    if not cache.validate(results):
        LOG.debug('wecmdb_ci_getter POST /wecmdb/ui/v2/ci-types/%s/ci-data/query' % expr_data['ci'])
        LOG.debug('wecmdb_ci_getter     filters: %s', data)
        resp = requests.post(base_url + '/wecmdb/ui/v2/ci-types/%s/ci-data/query' % ci_mapping[expr_data['ci']],
                      json={},
                      headers={'Authorization': 'Bearer ' + token})
        results = resp.json()['data']['contents']
        LOG.debug('wecmdb_ci_getter get %s result(all) length: %s' % (expr_data['ci'], len(results)))
        cache.set(ci_data_key, results)
    results = [ret for ret in results if jsonfilter.match_all(data['filters'], ret['data'])]
    LOG.debug('wecmdb_ci_getter get %s result(filter) length: %s' % (expr_data['ci'], len(results)))
    return results


class WeCMDBScope(object):

    def __init__(self, expr):
        self.expression = expr

    def is_match(self, data):
        '''
        check if wecmdb data(from expression) contains any item from data 
        :param data: [{...}]
        '''
        if data is None:
            return True
        # TODO: fix this, get ci mapping from api
        ci_mapping = {
            'host_resource_instance': '32',
            'resource_set': '29',
            'deploy_environment': '3',
            'app_instance': '50',
            'unit': '48',
            'subsys': '47',
            'app_system': '46',
            }
        input_guids = [d['data']['guid'] for d in data]
        input_ci_id = None
        if input_guids:
            # NOTICE: may be bug, assume all data is the same ci type
            input_ci_id = str(int(input_guids[0].split('_')[0]))
            try:
                expr_groups = expression.expr_parse(self.expression)
            except ValueError as e:
                LOG.exception(e)
            else:
                expect_ci_id = ci_mapping[expr_groups[-1]['data']['ci']]
                # only if input ci type == expr result ci type
                if input_ci_id == expect_ci_id:
                    results = expression.expr_query(self.expression, wecmdb_ci_getter, ci_mapping)
                    expr_guids = [d['data']['guid'] for d in results]
                    if set(input_guids) & set(expr_guids):
                        return True
                else:
                    LOG.debug('input ci(%s) is not the same as expression require(%s), passthrough...', input_ci_id, expect_ci_id)
        return False
