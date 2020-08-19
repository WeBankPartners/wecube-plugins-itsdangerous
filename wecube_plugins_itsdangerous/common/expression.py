# coding=utf-8
"""
wecube_plugins_itsdangerous.common.expression
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

本模块提供WeCube通用表达式解析

"""
import json
import re

from talos.core import utils

R_SINGLE_FILTER = re.compile('\{([_a-zA-Z][_a-zA-Z0-9.]*)\s+([a-zA-Z]+)\s+([^}]+)\}')
R_SEG_EXPRESSION = re.compile(
    '(?:\(([_a-zA-Z][_a-zA-Z0-9]*)\))?(?:([_a-zA-Z][_a-zA-Z0-9]*):)?([_a-zA-Z][_a-zA-Z0-9]*)((?:\{[_a-zA-Z][_a-zA-Z0-9.]*\s+[a-zA-Z]+\s+.*\}){1,30})?(?:\.([_a-zA-Z][_a-zA-Z0-9]*))?$'
)


def _expr_op_finder(expr):
    '''
    find all indexes of operators
    :param expr: expression
    '''
    results = []
    ops = ['~', '>', '->', '<-']
    for el in ops:
        index = expr.find(el)
        if index != -1:
            if el == '>' and expr[index - 1] == '-':
                # ignore it, we will find it when op = '->'
                pass
            else:
                results.append({'op': el, 'index': index})
        while index != -1:
            index = expr.find(el, index + len(el))
            if index != -1:
                if el == '>' and expr[index - 1] == '-':
                    # ignore it, we will find it when op = '->'
                    pass
                else:
                    results.append({'op': el, 'index': index})
    results.sort(key=lambda x: x['index'])
    return results


def _expr_split(expr, indexes):
    '''
    split expr according to indexes
    :param expr: expression
    :param indexes: result of _expr_op_finder
    '''
    results = []
    start = 0
    for el in indexes:
        results.append({'type': 'expr', 'value': expr[start:el['index']], 'data': None})
        results.append({'type': 'op', 'value': el['op'], 'data': None})
        start = el['index'] + len(el['op'])
    results.append({'type': 'expr', 'value': expr[start:], 'data': None})
    return results


def expr_filter_parse(expr_filter):
    '''
    parse filter to dict, eg. "{key1 op val1}{...}"
    :param expr_filter: filter expression
    '''
    results = []
    if len(expr_filter) > 0:
        index = 0
        while index < len(expr_filter):
            res = R_SINGLE_FILTER.match(expr_filter, index)
            if res:
                filter_name = res.groups()[0]
                filter_op = res.groups()[1]
                filter_val = res.groups()[2]
                if filter_op == 'is':
                    filter_op = 'null'
                    filter_val = None
                elif filter_op == 'isnot':
                    filter_op = 'notNull'
                    filter_val = None
                elif filter_op == 'in':
                    # TODO: fix this, replace is not good enough
                    filter_val = json.loads(filter_val[1:-1].replace("'", '"'))
                elif (filter_val.startswith("'") and filter_val.endswith("'")) or (filter_val.startswith('"')
                                                                                   and filter_val.endswith('"')):
                    # string
                    filter_val = filter_val[1:-1]
                else:
                    # number
                    filter_val = int(filter_val)

                results.append({'name': filter_name, 'operator': filter_op, 'value': filter_val})
                index = res.end()
            else:
                index = len(expr_filter)
    return results


def expr_seg_parse(expr):
    '''
    parse a segment of expression to dict, eg. "(attr)[plugin:]ci[{key op value}*][.attr]" into
    {
        'backref_attribute': '', 
        'plugin': '', 
        'ci': '', 
        'filters': '', 
        'attribute': ''
    }
    :param expr_filter: expression
    '''
    res = R_SEG_EXPRESSION.match(expr)
    if (res):
        result = {
            'backref_attribute': res.groups()[0] or '',
            'plugin': res.groups()[1] or '',
            'ci': res.groups()[2] or '',
            'filters': res.groups()[3] or '',
            'attribute': res.groups()[4] or ''
        }
        result['filters'] = expr_filter_parse(result['filters'])
        return result
    raise ValueError('invalid expression: ' + expr)


def expr_parse(expr):
    '''
    parse an expression to dict
    :param expr: expression
    '''
    split_res = _expr_split(expr, _expr_op_finder(expr))
    for el in split_res:
        if el['type'] == 'expr':
            el['data'] = expr_seg_parse(el['value'])
    return split_res


def expr_match_input(expr_groups, ci_getter, input_data, ci_mapping):
    '''
    fetch data according to expression by specific source(input_data), see if there are any matches
    :param expr_groups: result of expr_parse()
    :param ci_getter: function (expr_data, is_backref, guids) => {}
    :param input_data: list of input ci
    
    ci_getter: 
    if is_backref
        ci[with filters][expr_data.backref_attrubute].guid in guids
    else 
        ci[with filters].guid in guids
    '''
    results = {}
    for el in input_data:
        is_backref = False
        guids = []
        cur_data = []
        for i in range(len(expr_groups)):
            expr = expr_groups[i]
            expr_data = expr['data']
            # user input_data
            if i == 0:
                if len(expr_data['attribute']) > 0:
                    guid = el['data'][expr_data['attribute']]['guid']
                else:
                    guid = el['data']['guid']
                if guid:
                    guids.append(guid)
                continue
            if expr['type'] == 'expr':
                # user ci, backref_attribute.guid in guids[if is_backref], filters
                if len(guids) == 0:
                    # can not find any data that match expression
                    cur_data = []
                    break
                cur_data = ci_getter(expr_data, is_backref, guids, ci_mapping)
                guids = []
                for j in range(len(cur_data)):
                    guid = ""
                    if len(expr_data['attribute']) > 0:
                        result_item = cur_data[j]['data'][expr_data['attribute']]
                        if utils.is_list_type(result_item):
                            guids.extend([i_result_item['guid'] for i_result_item in result_item])
                        else:
                            guid = result_item['guid']
                    else:
                        guid = cur_data[j]['data']['guid']
                    if guid:
                        guids.append(guid)
            elif expr['type'] == 'op':
                if expr['value'] == '>' or expr['value'] == '->':
                    is_backref = False
                elif expr['value'] == '~' or expr['value'] == '<-':
                    is_backref = True
        results[el['data']['guid']] = cur_data
    return results


def expr_query(expr, ci_getter, ci_mapping):
    '''
    fetch data according to expression
    :param expr: result of ()
    :param ci_getter: function (expr_data, is_backref, guids) => {}
    
    ci_getter: 
    if is_backref
        ci[with filters][expr_data.backref_attrubute].guid in guids
    else 
        ci[with filters].guid in guids
    '''
    results = []
    is_backref = False
    guids = None
    expr_origin = expr
    expr_groups = expr_parse(expr_origin)
    for i in range(len(expr_groups)):
        expr = expr_groups[i]
        expr_data = expr['data']
        if expr['type'] == 'expr':
            # user ci, backref_attribute.guid in guids[if is_backref], filters
            if guids is not None and len(guids) == 0:
                # can not find any data that match expression
                results = []
                break
            results = ci_getter(expr_data, is_backref, guids, ci_mapping)
            guids = []
            for j in range(len(results)):
                guid = ""
                if len(expr_data['attribute']) > 0:
                    result_item = results[j]['data'][expr_data['attribute']]
                    if utils.is_list_type(result_item):
                        guids.extend([i_result_item['guid'] for i_result_item in result_item])
                    else:
                        guid = result_item['guid']
                else:
                    guid = results[j]['data']['guid']
                if guid:
                    guids.append(guid)
        elif expr['type'] == 'op':
            if expr['value'] == '>' or expr['value'] == '->':
                is_backref = False
            elif expr['value'] == '~' or expr['value'] == '<-':
                is_backref = True
    return results
