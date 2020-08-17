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
    :param data: {...}
    '''
    results = set([True])
    for _filter in filters:
        val = utils.get_item(data, _filter['name'])
        if _filter['operator'] == 'set':
            results.add(True) if val else results.add(False)
        elif _filter['operator'] == 'notset':
            results.add(False) if val else results.add(True)
        elif _filter['operator'] == 'null':
            results.add(True) if val is None else results.add(False)
        elif _filter['operator'] == 'notNull':
            results.add(True) if val is not None else results.add(False)
        elif _filter['operator'] == 'ilike':
            if utils.is_list_type(val):
                tmp_result = False
                for v in val:
                    if _filter['value'].lower() in v.lower():
                        tmp_result = True
                        break
                results.add(True) if tmp_result else results.add(False)
            else:
                results.add(True) if _filter['value'].lower() in val.lower() else results.add(False)
        elif _filter['operator'] == 'like':
            if utils.is_list_type(val):
                tmp_result = False
                for v in val:
                    if _filter['value'] in v:
                        tmp_result = True
                        break
                results.add(True) if tmp_result else results.add(False)
            else:
                results.add(True) if _filter['value'] in val else results.add(False)
        elif _filter['operator'] == 'eq':
            if utils.is_list_type(val):
                tmp_result = False
                for v in val:
                    if _filter['value'] == v:
                        tmp_result = True
                        break
                results.add(True) if tmp_result else results.add(False)
            else:
                results.add(True) if _filter['value'] == val else results.add(False)
        elif _filter['operator'] == 'ne':
            if utils.is_list_type(val):
                tmp_result = True
                for v in val:
                    if _filter['value'] == v:
                        tmp_result = False
                        break
                results.add(True) if tmp_result else results.add(False)
            else:
                results.add(True) if _filter['value'] != val else results.add(False)
        elif _filter['operator'] == 'in':
            if utils.is_list_type(val):
                tmp_result = False
                for v in val:
                    if v in _filter['value']:
                        tmp_result = True
                        break
                results.add(True) if tmp_result else results.add(False)
            else:
                results.add(True) if val in _filter['value'] else results.add(False)
        elif _filter['operator'] == 'nin':
            if utils.is_list_type(val):
                results.add(False)
            else:
                results.add(True) if val not in _filter['value'] else results.add(False)
        elif _filter['operator'] in ('regex', 'iregex'):
            flag = 0
            if _filter['operator'] == 'iregex':
                flag = flag | re.IGNORECASE
            if utils.is_list_type(val):
                tmp_result = False
                for v in val:
                    if re.search(_filter['value'], v, flag):
                        tmp_result = True
                        break
                results.add(True) if tmp_result else results.add(False)
            else:
                results.add(True) if re.search(_filter['value'], val, flag) else results.add(False)
        # TODO: other operator
        else:
            # unregconize operator, ignore it
            results.add(False)
    if False in results or len(results) == 0:
        return False
    return True
