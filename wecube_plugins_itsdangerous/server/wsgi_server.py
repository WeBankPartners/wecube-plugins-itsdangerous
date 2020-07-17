# coding=utf-8
"""
wecube_plugins_itsdangerous.server.wsgi_server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

本模块提供wsgi启动能力

"""

from __future__ import absolute_import

import os
from talos.server import base
# from talos.core import config


# @config.intercept('db_password', 'other_password')
# def get_password(value, origin_value):
#     """value为上一个拦截器处理后的值（若此函数为第一个拦截器，等价于origin_value）
#        origin_value为原始配置文件的值
#        没有拦截的变量talos将自动使用原始值，因此定义一个拦截器是很关键的
#        函数处理后要求必须返回一个值
#     """
#     # 演示使用不安全的base64，请使用你认为安全的算法进行处理
#     return base64.b64decode(origin_value)


application = base.initialize_server('wecube_plugins_itsdangerous',
                                     os.environ.get('WECUBE_PLUGINS_ITSDANGEROUS_CONF', './etc/wecube_plugins_itsdangerous.conf'),
                                     conf_dir=os.environ.get('WECUBE_PLUGINS_ITSDANGEROUS_CONF_DIR', './etc/wecube_plugins_itsdangerous.conf.d'))
