# coding=utf-8
import pytest

from wecube_plugins_itsdangerous.common import jsonfilter

data_list = [
    {
        'id': 1,
        'empty_string': '',
        'a': 11,
        'b': 12.3,
        'c': 'def1',
        'g': [14, 15],
        'h': ['16', '17']
    },
    {
        'id': 2,
        'empty_array': [],
        'a': 21,
        'b': 22.3,
        'c': 'def2',
        'g': [24, 25],
        'h': ['26', '27']
    },
    {
        'id': 3,
        'empty_object': {},
        'a': 31,
        'b': 32.3,
        'c': 'def3',
        'g': [34, 35],
        'h': ['36', '37']
    },
    {
        'id': 4,
        'a': 41,
        'b': 42.3,
        'c': 'deF4',
        'g': [44, 45],
        'h': ['46', '47']
    },
    {
        'id': 5,
        'a': 51,
        'b': 52.3,
        'c': 'deF5',
        'g': [54, 55],
        'h': ['56', '57']
    },
]


def get_match(filters, rows):
    results = []
    for r in rows:
        if jsonfilter.match_all(filters, r):
            results.append(r)
    return results


def test_filter_set():
    assert len(get_match([{'name': 'id', 'operator': 'set'}], data_list)) == 5
    assert len(get_match([{'name': 'id', 'operator': 'set', 'value': None}], data_list)) == 5
    assert len(get_match([{'name': 'id', 'operator': 'notset'}], data_list)) == 0
    assert len(get_match([{'name': 'id_not_exists', 'operator': 'notset'}], data_list)) == 5
    assert len(get_match([{'name': 'empty_string', 'operator': 'notset'}], data_list)) == 5
    assert len(get_match([{'name': 'empty_array', 'operator': 'notset'}], data_list)) == 5
    assert len(get_match([{'name': 'empty_object', 'operator': 'notset'}], data_list)) == 5


def test_filter_null():
    assert len(get_match([{'name': 'empty_string', 'operator': 'null', 'value': ''}], data_list)) == 4
    assert len(get_match([{'name': 'empty_array', 'operator': 'null', 'value': ''}], data_list)) == 4
    assert len(get_match([{'name': 'empty_object', 'operator': 'null', 'value': ''}], data_list)) == 4
    assert len(get_match([{'name': 'empty_object', 'operator': 'notnull', 'value': ''}], data_list)) == 1


def test_filter_like():
    assert len(get_match([{'name': 'c', 'operator': 'like', 'value': 'def'}], data_list)) == 3
    assert len(get_match([{'name': 'c', 'operator': 'like', 'value': 'deF'}], data_list)) == 2
    assert len(get_match([{'name': 'c', 'operator': 'ilike', 'value': 'deF'}], data_list)) == 5
    assert len(get_match([{'name': 'c', 'operator': 'ilike', 'value': 'Def'}], data_list)) == 5


def test_filter_eq():
    assert len(get_match([{'name': 'id', 'operator': 'eq', 'value': 2}], data_list)) == 1
    assert len(get_match([{'name': 'c', 'operator': 'eq', 'value': 'def1'}], data_list)) == 1
    assert len(get_match([{'name': 'g', 'operator': 'eq', 'value': 34}], data_list)) == 1
    assert get_match([{'name': 'g', 'operator': 'eq', 'value': 34}], data_list)[0]['id'] == 3
    assert len(get_match([{'name': 'h', 'operator': 'eq', 'value': '26'}], data_list)) == 1
    assert get_match([{'name': 'h', 'operator': 'eq', 'value': '27'}], data_list)[0]['id'] == 2


def test_filter_neq():
    assert len(get_match([{'name': 'id', 'operator': 'neq', 'value': 2}], data_list)) == 4
    assert len(get_match([{'name': 'g', 'operator': 'neq', 'value': 55}], data_list)) == 4
    assert len(get_match([{'name': 'h', 'operator': 'neq', 'value': '57'}], data_list)) == 4


def test_filter_gtlt():
    assert len(get_match([{'name': 'id', 'operator': 'gt', 'value': 3}], data_list)) == 2
    assert len(get_match([{'name': 'id', 'operator': 'gte', 'value': 3}], data_list)) == 3
    assert len(get_match([{'name': 'id', 'operator': 'lt', 'value': 2}], data_list)) == 1
    assert len(get_match([{'name': 'id', 'operator': 'lte', 'value': 3}], data_list)) == 3
    assert len(get_match([{'name': 'b', 'operator': 'gt', 'value': 52}], data_list)) == 1


def test_filter_regex():
    assert len(get_match([{'name': 'c', 'operator': 'regex', 'value': 'd[a-z0-9]+$'}], data_list)) == 3
    assert len(get_match([{'name': 'c', 'operator': 'regex', 'value': 'd[a-zA-Z0-9]+$'}], data_list)) == 5
    assert len(get_match([{'name': 'c', 'operator': 'iregex', 'value': 'd[a-z0-9]+$'}], data_list)) == 5
    assert len(get_match([{'name': 'h', 'operator': 'regex', 'value': '3\d'}], data_list)) == 1
    assert len(get_match([{'name': 'h', 'operator': 'iregex', 'value': '4\d'}], data_list)) == 1


def test_filter_regex():
    assert len(get_match([{'name': 'a', 'operator': 'in', 'value': [21, 51]}], data_list)) == 2
    assert len(get_match([{'name': 'id', 'operator': 'notin', 'value': [1, 2, 3, 4]}], data_list)) == 1
    assert len(get_match([{'name': 'id', 'operator': 'nin', 'value': [1, 2, 3, 4]}], data_list)) == 1
    assert len(get_match([{'name': 'c', 'operator': 'in', 'value': ['def3', 'deF4', 'nothing']}], data_list)) == 2