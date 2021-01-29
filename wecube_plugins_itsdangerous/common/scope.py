# coding=utf-8

from __future__ import absolute_import

import logging
import datetime

from talos.common import cache
from talos.core import config

from wecube_plugins_itsdangerous.common import expression
from wecube_plugins_itsdangerous.common import jsonfilter
from wecube_plugins_itsdangerous.common import utils
from wecube_plugins_itsdangerous.common import wecube

CONF = config.CONF
LOG = logging.getLogger(__name__)
TOKEN_KEY = 'itsdangerous_subsystem_token'


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


def wecube_expr_query(expr):
    base_url = CONF.wecube.base_url
    cache_key = 'wecube/expr/%s' % expr
    results = cache.get(cache_key, exipres=3)
    if not cache.validate(results):
        LOG.debug('wecube_expr_query with %s' % expr)
        cost_start = datetime.datetime.now()
        client = wecube.WeCubeClient(base_url)
        subsys_token = cache.get_or_create(TOKEN_KEY, client.login_subsystem, expires=600)
        client.token = subsys_token
        resp = client.post(base_url + '/platform/v1/data-model/dme/integrated-query', {
            'dataModelExpression': expr,
            'filters': []
        })
        cost_end = datetime.datetime.now()
        LOG.debug('wecube_expr_query time cost %s' % (cost_end - cost_start))
        results = resp['data'] or []
        cache.set(cache_key, results)
    LOG.debug('wecube_expr_query result length: %s' % len(results))
    return results


class WeCubeScope(object):
    def __init__(self, expr):
        self.expression = expr

    def is_match(self, data, expect_type=None):
        '''
        check if wecube data(from expression) contains any item from data 
        :param data: [{id: xxx}, {...}]
        '''
        data = data or []
        # NOTE: (roy) change this if instance structure changed
        input_guids = [d['id'] for d in data]
        if input_guids:
            try:
                expr_groups = expression.expr_parse(self.expression)
                # fast check for entity type match
                # eg. expect_type="wecmdb:host_instance" & last_ci_type="wecmdb:rdb_instance"
                # the result is always False
                last_ci_type = '%s:%s' % (expr_groups[-1]['data']['plugin'], expr_groups[-1]['data']['ci'])
                if expect_type and expect_type != last_ci_type:
                    return False
            except ValueError as e:
                LOG.exception(e)
            else:
                results = wecube_expr_query(self.expression)
                expr_guids = [d['id'] for d in results]
                if set(input_guids) & set(expr_guids):
                    return True
        return False