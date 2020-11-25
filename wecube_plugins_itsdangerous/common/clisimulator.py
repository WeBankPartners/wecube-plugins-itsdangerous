# coding=utf-8
"""
wecube_plugins_itsdangerous.common.clisimulator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

本模块提供cli命令行模拟器

"""
import argparse
import logging

from wecube_plugins_itsdangerous.common import jsonfilter

LOG = logging.getLogger(__name__)


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
                prepare_kwargs['type'] = (int if arg.get('convert_int', None) else str)
                prepare_kwargs['nargs'] = arg.get('repeatable', None)

            parser.add_argument(*prepare_args, **prepare_kwargs)
        return parser

    def parse_known_args(self, parser, args=None, namespace=None):
        # make sure that args are mutable
        args = list(args)

        # default Namespace built from parser defaults
        if namespace is None:
            namespace = argparse.Namespace()

        # add any action defaults that aren't present
        for action in parser._actions:
            if action.dest is not argparse.SUPPRESS:
                if not hasattr(namespace, action.dest):
                    if action.default is not argparse.SUPPRESS:
                        setattr(namespace, action.dest, action.default)

        # add any parser defaults that aren't present
        for dest in parser._defaults:
            if not hasattr(namespace, dest):
                setattr(namespace, dest, parser._defaults[dest])

        # parse the arguments and exit if there are any errors
        try:
            namespace, args = parser._parse_known_args(args, namespace)
            if hasattr(namespace, argparse._UNRECOGNIZED_ARGS_ATTR):
                args.extend(getattr(namespace, argparse._UNRECOGNIZED_ARGS_ATTR))
                delattr(namespace, argparse._UNRECOGNIZED_ARGS_ATTR)
            return namespace, args
        except argparse.ArgumentError as e:
            LOG.error('exception raise when process argparse, try to ignore, input args: %s', args)
            LOG.exception(e)
            return namespace, args

    def check(self, input_args, filters, parser=None):
        parser = parser or self.parser
        space = self.parse_known_args(parser, input_args)
        return jsonfilter.match_all(filters, vars(space[0]))
