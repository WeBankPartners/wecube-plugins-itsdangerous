# coding=utf-8

from __future__ import absolute_import

import json
import logging
import re

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
        lineno = -1
        for rule in self.rules:
            if scope.JsonScope(rule['match_value']).is_match(self.content):
                results.append({'lineno': lineno,
                                'level': rule['level'],
                                'content': rule['match_value'],
                                'message': rule['name']
                                })
        return results


class BashCliDetector(object):

    def __init__(self, content, rules):
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
            simulators = m_param.setdefault(cli_param['name'], [])
            simulators.append(clisimulator.Simulator(cli_param['args']))

    def check(self):
        results = []
        stream = self.reader(self.content)
        for lineno, tokens in stream.iter():
            if tokens:
                cmd, args = tokens[0], tokens[1:]
                for rule in self.rules:
                    r_name = rule['name']
                    r_level = rule['level']
                    if r_name.startswith('强制kill('):
                        pass
                    r_filters = json.loads(rule['match_value'])
                    if rule['match_param_id'] in self.parsers and cmd in self.parsers[rule['match_param_id']]:
                        for sim in self.parsers[rule['match_param_id']][cmd]:
                            if sim.check(args, r_filters):
                                results.append({'lineno': lineno,
                                                'level': r_level,
                                                'content': ' '.join(tokens),
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
                        results.append({'lineno': lineno,
                                        'level': r_level,
                                        'content': sql,
                                        'message': r_name
                                        })
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
                        results.append({'lineno': lineno,
                                        'level': r_level,
                                        'content': dot_text,
                                        'message': r_name
                                        })
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
