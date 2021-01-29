# coding=utf-8
"""
wecube_plugins_itsdangerous.common.wecube
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

本模块提供项目WeCube Client（Proxy）

"""
import logging
import base64
import random

from talos.common import cache
from talos.core import config
from talos.core.i18n import _
from talos.core import utils as talos_utils
from talos.utils import scoped_globals
from wecube_plugins_itsdangerous.common import exceptions
from wecube_plugins_itsdangerous.common import utils

LOG = logging.getLogger(__name__)
CONF = config.CONF
TOKEN_KEY = 'itsdangerous_subsystem_token'


def get_wecube_token(base_url=None):
    base_url = base_url or CONF.wecube.base_url
    token = talos_utils.get_attr(scoped_globals.GLOBALS, 'request.auth_token') or CONF.wecube.token
    return token


def encrypt(message, rsa_key):
    import M2Crypto.RSA
    template = '''-----BEGIN PRIVATE KEY-----
%s
-----END PRIVATE KEY-----'''
    key_pem = template % rsa_key
    privat_key = M2Crypto.RSA.load_key_string(key_pem.encode())
    ciphertext = privat_key.private_encrypt(message.encode(), M2Crypto.RSA.pkcs1_padding)
    encrypted_message = base64.b64encode(ciphertext).decode()
    return encrypted_message


class WeCubeClient(object):
    """WeCube Client"""
    def __init__(self, server, token=None):
        self.server = server.rstrip('/')
        self.token = token or get_wecube_token(self.server)

    def build_headers(self):
        return {'Authorization': 'Bearer ' + self.token}

    def check_response(self, resp_json):
        if resp_json['status'] != 'OK':
            # 当创建/更新条目错误，且仅有一个错误时，返回内部错误信息
            if isinstance(resp_json.get('data', None), list) and len(resp_json['data']) == 1:
                if 'message' in resp_json['data'][0]:
                    raise exceptions.PluginError(message=resp_json['data'][0]['message'])
            raise exceptions.PluginError(message=resp_json['message'])

    def login_subsystem(self, set_self=True):
        '''client = WeCubeClient('http://ip:port', None)
           token = client.login_subsystem()
           # use your access token
        '''
        sequence = 'abcdefghijklmnopqrstuvwxyz1234567890'
        nonce = ''.join(random.choices(sequence, k=4))
        url = self.server + '/auth/v1/api/login'
        password = encrypt('%s:%s' % (CONF.wecube.sub_system_code, nonce), CONF.wecube.sub_system_key)
        data = {
            "password": password,
            "username": CONF.wecube.sub_system_code,
            "nonce": nonce,
            "clientType": "SUB_SYSTEM"
        }
        resp_json = self.post(url, data)
        for token in resp_json['data']:
            if token['tokenType'] == 'accessToken':
                if set_self:
                    self.token = token['token']
                return token['token']

    def get(self, url, param=None):
        LOG.info('GET %s', url)
        LOG.debug('Request: query - %s, data - None', str(param))
        resp_json = utils.RestfulJson.get(url, headers=self.build_headers(), params=param)
        LOG.debug('Response: %s', str(resp_json))
        self.check_response(resp_json)
        return resp_json

    def post(self, url, data, param=None):
        LOG.info('POST %s', url)
        LOG.debug('Request: query - %s, data - %s', str(param), str(data))
        resp_json = utils.RestfulJson.post(url, headers=self.build_headers(), params=param, json=data)
        LOG.debug('Response: %s', str(resp_json))
        self.check_response(resp_json)
        return resp_json

    def update(self, url_path, data):
        url = self.server + url_path
        return self.post(url, data)

    def retrieve(self, url_path):
        url = self.server + url_path
        return self.get(url)
