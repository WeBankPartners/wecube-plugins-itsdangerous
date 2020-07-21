# coding=utf-8
import pytest

from wecube_plugins_itsdangerous.common import clisimulator


def test_cli_rm():
    rm = [
        {'name': 'force', 'shortcut': '-f,--force', 'action': 'store_true'},
        {'name': 'recursive', 'shortcut': '-r,-R,--recursive', 'action': 'store_true'},
        {'name': 'help', 'shortcut': '--help', 'action': 'store_true'},
        {'name': 'version', 'shortcut': '--version', 'action': 'store_true'},
        {'name': 'path', 'repeatable': '*'},
    ]
    rm_filters = [
        {'name': 'force', 'operator': 'set'},
        {'name': 'recursive', 'operator': 'set'},
        {'name': 'help', 'operator': 'notset'},
        {'name': 'version', 'operator': 'notset'},
        {'name': 'path', 'operator': 'ilike', 'value': '*'},
    ]
    rm_filters2 = [
        {'name': 'force', 'operator': 'set'},
        {'name': 'recursive', 'operator': 'set'},
        {'name': 'help', 'operator': 'notset'},
        {'name': 'version', 'operator': 'notset'},
        {'name': 'path', 'operator': 'notset'},
    ]
    s = clisimulator.Simulator(rm)
    cmds = [
        '-f -v -r /tmp/*',
        '-fr /tmp/*',
        '-f --help -r /tmp/*',
        '-f --version -r /tmp/*',
        '-f -abcde -r /tmp/*',
        '-rf /tmp/*',
        '-rf -f -r',
        '-rf -f -r /tmp/* /ppp'
            ]
    rm_filters_expected = [True, True, False, False, True, True, False, True]
    rm_filters2_expected = [False, False, False, False, False, False, True, False]
    for i, c in enumerate(cmds):
        ret = s.check(c.split(), rm_filters)
        assert ret is rm_filters_expected[i]
    for i, c in enumerate(cmds):
        ret = s.check(c.split(), rm_filters2)
        assert ret is rm_filters2_expected[i]
