# coding=utf-8
"""
wecube_plugins_itsdangerous.common.clisimulator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

本模块提供cli命令行模拟器

"""
import argparse

from wecube_plugins_itsdangerous.common import jsonfilter


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
        # repeatable: None(default)/?/+/*/1/2/3...
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
        return jsonfilter.match_all(filters, vars(space[0]))
