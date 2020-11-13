# coding=utf-8
import logging

import pytest

from wecube_plugins_itsdangerous.common import expression, scope
from wecube_plugins_itsdangerous.common import exceptions

LOG = logging.getLogger(__name__)


def test_expression():
    expr1 = "cmdb:a{id eq '1'}{seq_num eq 2}{created_time is NULL}{name eq 'test'}{id in '['1', '2']'}.b_1->b.c>c~(c)d.e"
    ret = expression.expr_parse(expr1)
    assert len(ret) == 7
    assert ret[0]['type'] == 'expr'
    assert ret[0][
        'value'] == "cmdb:a{id eq '1'}{seq_num eq 2}{created_time is NULL}{name eq 'test'}{id in '['1', '2']'}.b_1"
    assert ret[0]['data']['plugin'] == 'cmdb'
    assert ret[0]['data']['ci'] == 'a'
    assert ret[0]['data']['backref_attribute'] == ''
    assert ret[0]['data']['attribute'] == 'b_1'
    assert ret[0]['data']['filters'] == [{
        'name': 'id',
        'operator': 'eq',
        'value': '1'
    }, {
        'name': 'seq_num',
        'operator': 'eq',
        'value': 2
    }, {
        'name': 'created_time',
        'operator': 'null',
        'value': None
    }, {
        'name': 'name',
        'operator': 'eq',
        'value': 'test'
    }, {
        'name': 'id',
        'operator': 'in',
        'value': ['1', '2']
    }]

    assert ret[1]['type'] == 'op'
    assert ret[1]['value'] == "->"
    assert ret[1]['data'] is None

    assert ret[2]['type'] == 'expr'
    assert ret[2]['value'] == "b.c"
    assert ret[2]['data']['plugin'] == ''
    assert ret[2]['data']['ci'] == 'b'
    assert ret[2]['data']['backref_attribute'] == ''
    assert ret[2]['data']['attribute'] == 'c'
    assert ret[2]['data']['filters'] == []

    assert ret[3]['type'] == 'op'
    assert ret[3]['value'] == ">"
    assert ret[3]['data'] is None

    assert ret[4]['type'] == 'expr'
    assert ret[4]['value'] == "c"
    assert ret[4]['data']['plugin'] == ''
    assert ret[4]['data']['ci'] == 'c'
    assert ret[4]['data']['backref_attribute'] == ''
    assert ret[4]['data']['attribute'] == ''
    assert ret[4]['data']['filters'] == []

    assert ret[5]['type'] == 'op'
    assert ret[5]['value'] == "~"
    assert ret[5]['data'] is None

    assert ret[6]['type'] == 'expr'
    assert ret[6]['value'] == "(c)d.e"
    assert ret[6]['data']['plugin'] == ''
    assert ret[6]['data']['ci'] == 'd'
    assert ret[6]['data']['backref_attribute'] == 'c'
    assert ret[6]['data']['attribute'] == 'e'
    assert ret[6]['data']['filters'] == []


def test_expression_advance():
    expr1 = "cmdb:a{id eq '1'}{obj.attr eq 2}"
    ret = expression.expr_parse(expr1)
    assert len(ret) == 1
    assert ret[0]['type'] == 'expr'
    assert ret[0]['value'] == "cmdb:a{id eq '1'}{obj.attr eq 2}"
    assert ret[0]['data']['plugin'] == 'cmdb'
    assert ret[0]['data']['ci'] == 'a'
    assert ret[0]['data']['backref_attribute'] == ''
    assert ret[0]['data']['attribute'] == ''
    assert ret[0]['data']['filters'] == [{
        'name': 'id',
        'operator': 'eq',
        'value': '1'
    }, {
        'name': 'obj.attr',
        'operator': 'eq',
        'value': 2
    }]


def test_expression_match(mocker):
    mocker.patch.object(scope,
                        'wecube_ci_getter',
                        return_value=[{
                            'data': {
                                'guid': '0032_0000000022',
                                'host_resource_instance': {
                                    'guid': '1'
                                }
                            }
                        }, {
                            'data': {
                                'guid': '0032_0000000023',
                                'host_resource_instance': {
                                    'guid': '1'
                                }
                            }
                        }])
    expr1 = "wecmdb:deploy_environment{guid eq '0003_0000000001'}~(deploy_environment)wecmdb:app_system~(app_system)wecmdb:subsys{key_name eq 'PRD_TaDEMO_CORE'}~(subsys)wecmdb:unit~(unit)wecmdb:app_instance.host_resource_instance>wecmdb:host_resource_instance"
    ret = expression.expr_match_input(expression.expr_parse(expr1), scope.wecube_ci_getter, [{
        'data': {
            'guid': '0003_0000000001'
        }
    }], None)
    LOG.info(ret)
    for env_guid, vals in ret.items():
        assert env_guid == '0003_0000000001'
        assert len(vals) == 2
        for v in vals:
            assert v['data']['guid'] in ['0032_0000000022', '0032_0000000023']


def test_expression_error():
    expr1 = "cmdb:a:b>c.d"
    expr2 = "cmdb:a{not filter}.b>b.c"
    with pytest.raises(exceptions.PluginError):
        expression.expr_parse(expr1)
        expression.expr_parse(expr2)
