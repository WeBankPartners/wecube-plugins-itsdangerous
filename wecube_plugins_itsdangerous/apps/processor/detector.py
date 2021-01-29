# coding=utf-8

from __future__ import absolute_import

import json
import logging
import os.path
import re

from wecube_plugins_itsdangerous.common import expression
from wecube_plugins_itsdangerous.common import clisimulator
from wecube_plugins_itsdangerous.common import reader
from wecube_plugins_itsdangerous.common import scope

LOG = logging.getLogger(__name__)


class JsonFilterDetector(object):
    def __init__(self, content, rules):
        '''
        :param content: input params dict
        :param rules: [{db.model.rule}]
        '''
        self.content = content
        self.rules = rules
        self.reader = None

    def check(self):
        results = []
        lineno = (-1, -1)
        for rule in self.rules:
            if scope.JsonScope(rule['match_value']).is_match(self.content):
                results.append({
                    'lineno': lineno,
                    'level': rule['level'],
                    'content': rule['match_value'],
                    'message': rule['name']
                })
        return results


class BashCliDetector(object):
    def __init__(self, content, rules, handover_match_params=None):
        '''
        :param content: script content
        :param rules: [{db.model.rule}]
        '''
        self.content = content
        self.rules = rules
        self.reader = reader.ShellReader
        arg_params = {}
        for rule in rules:
            if rule['match_param']:
                arg_params[rule['match_param_id']] = rule['match_param']
        # map rule.match_param_id => cmd => args
        self.parsers = {}
        for match_param in arg_params.values():
            cli_param = match_param['params']
            m_param = self.parsers.setdefault(match_param['id'], {})
            m_param['name'] = cli_param['name']
            m_param['opt_strip_path'] = cli_param.get('opt_strip_path', False)
            m_param['simulator'] = clisimulator.Simulator(cli_param['args'])
        handover_match_params = handover_match_params or []
        # parse handover type of match_param
        self.handover_parsers = []
        for match_param in handover_match_params:
            cli_param = match_param['params']
            m_param = {}
            m_param['name'] = cli_param['name']
            m_param['opt_strip_path'] = cli_param.get('opt_strip_path', False)
            # m_param['simulator'] = clisimulator.Simulator(cli_param['args'])
            self.handover_parsers.append(m_param)

    def _command_equal(self, cmd, parser):
        if parser['opt_strip_path']:
            return parser['name'] == os.path.basename(cmd)
        return parser['name'] == cmd

    def _command_handover(self, tokens):
        cmd, args = tokens[0], tokens[1:]
        if len(args) >= 1:
            for parser in self.handover_parsers:
                if self._command_equal(cmd, parser):
                    return args
        return tokens

    def check(self):
        results = []
        stream = self.reader(self.content)
        for lineno, tokens in stream.iter():
            if tokens:
                origin_tokens = tokens
                tokens = self._command_handover(tokens)
                cmd, args = tokens[0], tokens[1:]
                for rule in self.rules:
                    r_name = rule['name']
                    r_level = rule['level']
                    r_filters = []
                    if rule['match_value'] and rule['match_value'].lstrip().startswith(
                            '[') and rule['match_value'].rstrip().endswith(']'):
                        r_filters = json.loads(rule['match_value'])
                    else:
                        r_filters = expression.expr_filter_parse(rule['match_value'])
                    if rule['match_param_id'] in self.parsers and self._command_equal(
                            cmd, self.parsers[rule['match_param_id']]):
                        parser = self.parsers[rule['match_param_id']]
                        sim = parser['simulator']
                        # command equal & empty filter means YES
                        if not r_filters:
                            results.append({
                                'lineno': lineno,
                                'level': r_level,
                                'content': ' '.join(origin_tokens),
                                'message': r_name
                            })
                        elif sim.check(args, r_filters):
                            results.append({
                                'lineno': lineno,
                                'level': r_level,
                                'content': ' '.join(origin_tokens),
                                'message': r_name
                            })
        return results


class SqlDetector(object):
    def __init__(self, content, rules):
        '''
        :param content: script content
        :param rules: [{db.model.rule}]
        '''
        self.content = content
        self.rules = rules
        self.reader = reader.SqlReader

    def check(self):
        results = []
        stream = self.reader(self.content)
        for lineno, tokens in stream.iter():
            # empty statement passthrough
            sql = tokens[0]
            if sql not in ('', ';'):
                for rule in self.rules:
                    r_name = rule['name']
                    r_level = rule['level']
                    r_filters = rule['match_value']
                    r_params = rule['match_param']['params'] if rule['match_param'] else {'flag': ''}
                    flag = 0
                    for f in [i.strip() for i in r_params['flag'].split('|') if i.strip()]:
                        append_flag = getattr(re, f, None)
                        if append_flag and isinstance(append_flag, int):
                            flag = flag | append_flag
                    if re.search(r_filters, sql, flags=flag):
                        results.append({'lineno': lineno, 'level': r_level, 'content': sql, 'message': r_name})
        return results


class FullTextDetector(object):
    def __init__(self, content, rules):
        '''
        :param content: script content
        :param rules: [{db.model.rule}]
        '''
        self.content = content
        self.rules = rules
        self.reader = reader.FullTextReader
        self.max_content_length = 128

    def check(self):
        results = []
        stream = self.reader(self.content)
        for lineno, tokens in stream.iter():
            # empty statement passthrough
            if tokens not in ('', ';'):
                text = tokens[0]
                for rule in self.rules:
                    r_name = rule['name']
                    r_level = rule['level']
                    r_filters = rule['match_value']
                    r_params = rule['match_param']['params'] if rule['match_param'] else {'flag': ''}
                    flag = 0
                    for f in [i.strip() for i in r_params['flag'].split('|') if i.strip()]:
                        append_flag = getattr(re, f, None)
                        if append_flag and isinstance(append_flag, int):
                            flag = flag | append_flag
                    dot_text = text[:self.max_content_length] if self.max_content_length else text
                    if len(text) > len(dot_text):
                        dot_text += '...'
                    if re.search(r_filters, text, flags=flag):
                        results.append({'lineno': lineno, 'level': r_level, 'content': dot_text, 'message': r_name})
        return results


class LineTextDetector(FullTextDetector):
    def __init__(self, content, rules):
        '''
        :param content: script content
        :param rules: [{db.model.rule}]
        '''
        self.content = content
        self.rules = rules
        self.reader = reader.LineReader
        self.max_content_length = None
