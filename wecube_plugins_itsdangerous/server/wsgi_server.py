# coding=utf-8
"""
wecube_plugins_itsdangerous.server.wsgi_server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

本模块提供wsgi启动能力

"""

from __future__ import absolute_import

import os
import json
from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA
from talos.server import base
from talos.core import utils
from talos.core import config
from talos.middlewares import lazy_init
from talos.middlewares import json_translator
from talos.middlewares import limiter
from talos.middlewares import globalvars
from urllib.parse import quote_plus

from wecube_plugins_itsdangerous.common import utils as plugin_utils
from wecube_plugins_itsdangerous.middlewares import auth
from wecube_plugins_itsdangerous.middlewares import permission
from wecube_plugins_itsdangerous.middlewares import language

RSA_KEY_PATH = '/certs/rsa_key'


def decrypt_rsa(secret_key, encrypt_text):
    rsakey = RSA.importKey(secret_key)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    random_generator = Random.new().read
    text = cipher.decrypt(plugin_utils.b64decode_key(encrypt_text), random_generator)
    return text.decode('utf-8')


@config.intercept('db_username', 'db_hostip', 'db_hostport', 'db_schema', 'gateway_url', 's3_access_key',
                  's3_secret_key', 'jwt_signing_key', 'platform_timezone', 'sub_system_code', 'sub_system_key', 'log_level')
def get_env_value(value, origin_value):
    prefix = 'ENV@'
    encrypt_prefix = 'RSA@'
    if value.startswith(prefix):
        env_name = value[len(prefix):]
        new_value = os.getenv(env_name, default='')
        if new_value.startswith(encrypt_prefix):
            certs_path = RSA_KEY_PATH
            if os.path.exists(certs_path) and os.path.isfile(certs_path):
                with open(certs_path) as f:
                    new_value = decrypt_rsa(f.read(), new_value[len(encrypt_prefix):])
            else:
                raise ValueError('keys with "RSA@", but rsa_key file not exists')
        return new_value
    return value


@config.intercept('db_password')
def get_env_value(value, origin_value):
    prefix = 'ENV@'
    encrypt_prefix = 'RSA@'
    if value.startswith(prefix):
        env_name = value[len(prefix):]
        new_value = os.getenv(env_name, default='')
        if new_value.startswith(encrypt_prefix):
            certs_path = RSA_KEY_PATH
            if os.path.exists(certs_path) and os.path.isfile(certs_path):
                with open(certs_path) as f:
                    new_value = decrypt_rsa(f.read(), new_value[len(encrypt_prefix):])
            else:
                raise ValueError('keys with "RSA@", but rsa_key file not exists')
        new_value = quote_plus(new_value)
        return new_value
    value = quote_plus(value)
    return value


def error_serializer(req, resp, exception):
    representation = exception.to_dict()
    # replace code with internal application code
    if 'error_code' in representation:
        representation['code'] = representation.pop('error_code')
    representation['status'] = 'ERROR'
    representation['data'] = representation.get('data', None)
    representation['message'] = representation.pop('description', '')
    resp.body = json.dumps(representation, cls=utils.ComplexEncoder)
    resp.content_type = 'application/json'


application = base.initialize_server('wecube_plugins_itsdangerous',
                                     os.environ.get('WECUBE_PLUGINS_ITSDANGEROUS_CONF',
                                                    '/etc/itsdangerous/wecube_plugins_itsdangerous.conf'),
                                     conf_dir=os.environ.get('WECUBE_PLUGINS_ITSDANGEROUS_CONF_DIR',
                                                             '/etc/itsdangerous/wecube_plugins_itsdangerous.conf.d'),
                                     middlewares=[
                                         language.Language(),
                                         globalvars.GlobalVars(),
                                         json_translator.JSONTranslator(),
                                         lazy_init.LazyInit(limiter.Limiter),
                                         auth.JWTAuth(),
                                         permission.Permission()
                                     ],
                                     override_middlewares=True)
application.set_error_serializer(error_serializer)