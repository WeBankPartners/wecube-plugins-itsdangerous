# coding=utf-8

from __future__ import absolute_import

import json
import logging
import re

from wecube_plugins_itsdangerous.common import clisimulator
from wecube_plugins_itsdangerous.common import reader

LOG = logging.getLogger(__name__)


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
        self.parsers = {}
        for match_param in arg_params.values():
            cli_param = match_param['params']
            simulators = self.parsers.setdefault(cli_param['name'], [])
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
                    r_filters = json.loads(rule['match_value'])
                    if cmd in self.parsers:
                        for sim in self.parsers[cmd]:
                            if sim.check(args, r_filters):
                                results.append({'lineno': lineno,
                                                'level': r_level,
                                                'content': ' '.join(tokens),
                                                'message': r_name
                                                })
        return results


class SqlDetector(object):

    def __init__(self, content, rules):
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
        self.content = content
        self.rules = rules
        self.reader = reader.FullTextReader

    def check(self):
        results = []
        stream = self.reader(self.content)
        for lineno, tokens in stream.iter():
            # empty statement passthrough
            if tokens not in ('', ';'):
                sql = tokens[0]
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


class LineTextDetector(FullTextDetector):

    def __init__(self, content, rules):
        self.content = content
        self.rules = rules
        self.reader = reader.LineReader
