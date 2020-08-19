# coding=utf-8
import os
from talos.server import base

application = base.initialize_server('wecube_plugins_itsdangerous',
                                     os.environ.get('WECUBE_PLUGINS_ITSDANGEROUS_CONF', './tests/test.conf'),
                                     conf_dir=os.environ.get('WECUBE_PLUGINS_ITSDANGEROUS_CONF_DIR',
                                                             './tests/test.conf.d'))
