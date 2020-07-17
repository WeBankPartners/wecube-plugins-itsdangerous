# coding=utf-8
"""
wecube_plugins_itsdangerous.common.clisimulator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

本模块提供cli命令行模拟器

"""
import argparse
import json

from talos.core import utils


class Simulator(object):

    def __init__(self, args):
        self.args = args
        self.parser = self._prepare()
    
    def _prepare(self):
        # arg example:
        # name: required
        # shortcut: None(default)/'-a, -b'
        # convert_int:  None(default)/int
        # action: store(default)/store_true/store_false/count/append
        # repeatable: None(default)/?/+/*/num
        parser = argparse.ArgumentParser(add_help=False)
        for arg in self.args:
            prepare_args = [s.strip() for s in (arg.get('shortcut', None) or '').split(',') if s.strip()]
            prepare_kwargs = {}
            if not prepare_args:
                prepare_args.append(arg['name'])
            else:
                prepare_kwargs = {'dest': arg['name']}
            prepare_kwargs['action'] = arg.get('action', 'store')
            if prepare_kwargs['action'] not in ('store_true', 'store_false'):
                prepare_kwargs['type'] = (int if arg.get('convert', None) else str)
                prepare_kwargs['nargs'] = arg.get('repeatable', None)
                
            parser.add_argument(*prepare_args, 
                                **prepare_kwargs)
        return parser
    
    def check(self, input_args, filters, parser=None):
        parser = parser or self.parser
        space = parser.parse_known_args(input_args)
        result = True
        for _filter in filters:
            val = getattr(space[0], _filter['name'])
            if _filter['operator'] == 'set':
                if val:
                    result = result and True
                else:
                    result = result and False
            elif _filter['operator'] == 'notset':
                if val:
                    result = result and False
                else:
                    result = result and True
            elif _filter['operator'] == 'ilike':
                if utils.is_list_type(val):
                    every_rets = []
                    for v in val:
                        if _filter['value'] in v:
                            every_rets.append(True)
                        else:
                            every_rets.append(False)
                    if True in every_rets:
                        result = result and True
                    else:
                        result = result and False
                else:
                    if _filter['value'] in val:
                        result = result and True
                    else:
                        result = result and False
            elif _filter['operator'] == 'eq':
                if utils.is_list_type(val):
                    every_rets = []
                    for v in val:
                        if _filter['value'] == v:
                            every_rets.append(True)
                        else:
                            every_rets.append(False)
                    if True in every_rets:
                        result = result and True
                    else:
                        result = result and False
                else:
                    if _filter['value'] in val:
                        result = result and True
                    else:
                        result = result and False
            else:
                # TODO: other operator
                pass
        return result
