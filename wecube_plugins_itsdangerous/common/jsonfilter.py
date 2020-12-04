# coding=utf-8
"""
wecube_plugins_itsdangerous.common.jsonfilter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

本模块提供WeCube表达式扩展filter匹配

"""
import re

from talos.core import utils


def match_all(filters, data):
    '''
    check if data match all filters
    :param filters: [{xx eq xx}, {...}]
        field set     [no value]
        field notset  [no value]
        field null    [no value]
        field notnull [no value]
        field ilike   'string'
        field like    'string'
        field eq      int/float/'string'
        field ne      int/float/'string'
        field in      [v1, v2]
        field nin     [v1, v2]
        field regex   'expr'
        field iregex  'expr'
        field gt      int/float
        field gte     int/float
        field lt      int/float
        field lte     int/float
    :param data: {...}
    '''
    def _match_ilike(stores, value, value_cmp):
        if utils.is_list_type(value):
            tmp_result = False
            for v in value:
                if value_cmp.lower() in v.lower():
                    tmp_result = True
                    break
            stores.add(True) if tmp_result else stores.add(False)
        else:
            if not utils.is_string_type(value):
                stores.add(False)
            else:
                stores.add(True) if value_cmp.lower() in value.lower() else stores.add(False)

    def _match_like(stores, value, value_cmp):
        if utils.is_list_type(value):
            tmp_result = False
            for v in value:
                if value_cmp in v:
                    tmp_result = True
                    break
            stores.add(True) if tmp_result else stores.add(False)
        else:
            if not utils.is_string_type(value):
                stores.add(False)
            else:
                stores.add(True) if value_cmp in value else stores.add(False)

    def _match_eq(stores, value, value_cmp):
        if utils.is_list_type(value):
            tmp_result = False
            for v in value:
                if value_cmp == v:
                    tmp_result = True
                    break
            stores.add(True) if tmp_result else stores.add(False)
        else:
            stores.add(True) if value_cmp == value else stores.add(False)

    def _match_ne(stores, value, value_cmp):
        if utils.is_list_type(value):
            tmp_result = True
            if not value:
                tmp_result = value_cmp != value
            else:
                for v in value:
                    if value_cmp == v:
                        tmp_result = False
                        break
            stores.add(True) if tmp_result else stores.add(False)
        else:
            stores.add(True) if value_cmp != value else stores.add(False)

    def _match_in(stores, value, value_cmp):
        if utils.is_list_type(value):
            tmp_result = False
            for v in value:
                if v in value_cmp:
                    tmp_result = True
                    break
            stores.add(True) if tmp_result else stores.add(False)
        else:
            stores.add(True) if value in value_cmp else stores.add(False)

    def _match_nin(stores, value, value_cmp):
        if utils.is_list_type(value):
            tmp_result = True
            if not value:
                tmp_result = value not in value_cmp
            # every item in value not in value_cmp means true
            for v in value:
                if v in value_cmp:
                    tmp_result = False
                    break
            stores.add(True) if tmp_result else stores.add(False)
        else:
            stores.add(True) if value not in value_cmp else stores.add(False)

    def _match_regex(stores, value, value_cmp, ignore_case=False):
        flag = 0
        if ignore_case:
            flag = flag | re.IGNORECASE
        if utils.is_list_type(value):
            tmp_result = False
            for v in value:
                if re.search(value_cmp, v, flag):
                    tmp_result = True
                    break
            stores.add(True) if tmp_result else stores.add(False)
        else:
            if not utils.is_string_type(value):
                stores.add(False)
            else:
                stores.add(True) if re.search(value_cmp, value, flag) else stores.add(False)

    def _match_gt(stores, value, value_cmp):
        if isinstance(value, (int, float)):
            stores.add(True) if value > value_cmp else stores.add(False)
        else:
            stores.add(False)

    def _match_gte(stores, value, value_cmp):
        if isinstance(value, (int, float)):
            stores.add(True) if value >= value_cmp else stores.add(False)
        else:
            stores.add(False)

    def _match_lt(stores, value, value_cmp):
        if isinstance(value, (int, float)):
            stores.add(True) if value < value_cmp else stores.add(False)
        else:
            stores.add(False)

    def _match_lte(stores, value, value_cmp):
        if isinstance(value, (int, float)):
            stores.add(True) if value <= value_cmp else stores.add(False)
        else:
            stores.add(False)

    results = set([True])
    for _filter in filters:
        if False in results:
            break
        val = utils.get_item(data, _filter['name'])
        val_cmp = _filter.get('value', None)
        op = _filter['operator']
        if op == 'set':
            results.add(True) if val else results.add(False)
        elif op in ('notset', 'notSet'):
            results.add(False) if val else results.add(True)
        elif op == 'null':
            results.add(True) if val is None else results.add(False)
        elif op in ('notNull', 'notnull'):
            results.add(True) if val is not None else results.add(False)
        elif op == 'ilike':
            _match_ilike(results, val, val_cmp)
        elif op == 'like':
            _match_like(results, val, val_cmp)
        elif op == 'eq':
            _match_eq(results, val, val_cmp)
        elif op in ('ne', 'neq'):
            _match_ne(results, val, val_cmp)
        elif op == 'in':
            _match_in(results, val, val_cmp)
        elif op in ('nin', 'notin'):
            _match_nin(results, val, val_cmp)
        elif op == 'regex':
            _match_regex(results, val, val_cmp, ignore_case=False)
        elif op == 'iregex':
            _match_regex(results, val, val_cmp, ignore_case=True)
        elif op == 'gt':
            _match_gt(results, val, val_cmp)
        elif op == 'gte':
            _match_gte(results, val, val_cmp)
        elif op == 'lt':
            _match_lt(results, val, val_cmp)
        elif op == 'lte':
            _match_lte(results, val, val_cmp)
        else:
            # unregconize operator, ignore it
            results.add(False)
    if False in results or len(results) == 0:
        return False
    return True
