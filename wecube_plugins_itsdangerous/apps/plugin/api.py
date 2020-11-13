# coding=utf-8

from __future__ import absolute_import

import glob
import hashlib
import logging
import os
import os.path
import tempfile

import requests
from talos.core import config, utils
from talos.core.i18n import _
from talos.db import crud
from talos.utils import scoped_globals
from wecube_plugins_itsdangerous.apps.processor import api as processor_api
from wecube_plugins_itsdangerous.common import exceptions, s3
from wecube_plugins_itsdangerous.common import utils as plugin_utils
from wecube_plugins_itsdangerous.db import validator as my_validator
from wecube_plugins_itsdangerous.db import resource

LOG = logging.getLogger(__name__)
CONF = config.CONF


def download_from_url(dir_path, url, random_name=False):
    filename = url.rsplit('/', 1)[-1]
    if random_name:
        filename = '%s_%s' % (utils.generate_uuid(), filename)
    filepath = os.path.join(dir_path, filename)
    if url.startswith(CONF.wecube.server):
        # nexus url
        token = CONF.wecube_platform.token or scoped_globals.GLOBALS.request.auth_token
        resp = requests.get(url, headers={'Authorization': 'Bearer ' + token}, stream=True)
        chunk_size = 1024 * 1024
        stream = resp.raw
        chunk = stream.read(chunk_size)
        with open(filepath, 'wb') as f:
            while chunk:
                f.write(chunk)
                chunk = stream.read(chunk_size)
    else:
        client = s3.S3Downloader(url)
        client.download_file(filepath, CONF.wecube_platform.s3.access_key, CONF.wecube_platform.s3.secret_key)
    return filepath, filename


def ensure_url_cached(url):
    cache_dir = CONF.pakcage_cache_dir
    filename = url.rsplit('/', 1)[-1]
    new_filename = hashlib.sha1(url.encode()).hexdigest() + '-' + filename
    cached_file_path = os.path.join(cache_dir, new_filename)
    with plugin_utils.lock(new_filename, timeout=300) as locked:
        if locked:
            if os.path.exists(cached_file_path):
                LOG.info('using cache: %s for package: %s', cached_file_path, url)
            else:
                with tempfile.TemporaryDirectory() as download_path:
                    LOG.info('download from: %s for pakcage: %s', url, url)
                    filepath = download_from_url(download_path, url)
                    LOG.info('download complete')
                    os.rename(filepath, cached_file_path)
        else:
            raise OSError(_('failed to acquire lock, package cache may not be available'))
    return cached_file_path, filename


class ServiceScript(resource.ServiceScript):
    def get_contents(self, service, plugin_param):
        def _file_extension_supported(extensions, filename):
            for e in extensions:
                if filename.endswith(e):
                    return True
            return False

        # [{"type": None/"sql"/"shell", "content": "...", "name": "additional name info"}]
        scripts = []
        script_locations = self.list(filters={'service': service})
        if len(script_locations) == 0:
            return scripts
        script_location = script_locations[0]
        content_type = script_location['content_type']
        # if content_field present, use it
        if script_location['content_field']:
            content = utils.get_item(plugin_param, script_location['content_field'])
            if content:
                scripts.append({'type': content_type, 'content': content, 'name': None})
        # if endpoint_field present, download from endpoint(s3/artifacts url from platform)
        if script_location['endpoint_field']:
            endpoint_url = utils.get_item(plugin_param, script_location['endpoint_field'])
            filepath, filename = ensure_url_cached(endpoint_url)
            packed_extensions = [
                '.zip', '.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2', '.tar.xz', '.txz', '.jar', '.war', '.apk'
            ]
            shell_extension = '.sh'
            sql_extension = '.sql'
            if _file_extension_supported(packed_extensions, filepath):
                unzip_path = filepath + '__unpack'
                plugin_utils.unpack_file(filepath, unzip_path)
                for name in glob.glob(os.path.join(unzip_path, '**/*' + shell_extension), recursive=True):
                    if not os.path.isfile(name):
                        continue
                    with open(name, 'r') as f:
                        scripts.append({'type': 'shell', 'content': f.read(), 'name': name[len(unzip_path) + 1:]})
                for name in glob.glob(os.path.join(unzip_path, '**/*' + sql_extension), recursive=True):
                    if not os.path.isfile(name):
                        continue
                    with open(name, 'r') as f:
                        scripts.append({'type': 'sql', 'content': f.read(), 'name': name[len(unzip_path) + 1:]})
            elif filepath.endswith(shell_extension):
                with open(filepath, 'r') as f:
                    scripts.append({'type': 'shell', 'content': f.read(), 'name': filename})
            elif filepath.endswith(sql_extension):
                with open(filepath, 'r') as f:
                    scripts.append({'type': 'sql', 'content': f.read(), 'name': filename})
        return scripts


class Box(object):
    data_rules = [
        crud.ColumnValidator(field='requestId',
                             rule=my_validator.LengthValidator(0, 63),
                             validate_on=['check:O'],
                             nullable=True),
        crud.ColumnValidator(field='operator',
                             rule=my_validator.LengthValidator(0, 63),
                             validate_on=['check:O'],
                             nullable=True),
        crud.ColumnValidator(field='serviceName',
                             rule=my_validator.LengthValidator(1, 255),
                             validate_on=['check:M'],
                             nullable=False),
        crud.ColumnValidator(field='servicePath',
                             rule=my_validator.LengthValidator(0, 255),
                             validate_on=['check:O'],
                             nullable=True),
        crud.ColumnValidator(field='entityInstances',
                             rule=my_validator.TypeValidator(list),
                             validate_on=['check:M'],
                             nullable=False),
        crud.ColumnValidator(field='inputs',
                             rule=my_validator.TypeValidator(list),
                             validate_on=['check:M'],
                             nullable=False),
    ]

    def check(self, data):
        '''
        input data:
        {
            "requestId": "request-001",  //仅异步调用需要用到
            "operator": "admin",  //操作人
            "serviceName": "a/b(c)/d"
            "servicePath": "a/b/run"
            "entityInstances": [{"guid": "xxx_xxxxxx"}]
            "inputs": [
                {"callbackParameter": "", "xml define prop": xxx},
                {},
                {}
            ]
        }
        '''
        results = []
        box = processor_api.Box()
        clean_data = crud.ColumnValidator.get_clean_data(self.data_rules, data, 'check')
        service = clean_data['serviceName']
        entity_instances = clean_data['entityInstances']
        input_params = clean_data['inputs']
        for input_param in input_params:
            detect_data = {
                'serviceName': service,
                'servicePath': clean_data['servicePath'],
                'inputParams': input_param,
                'scripts': ServiceScript().get_contents(service, input_param),
                'entityInstances': entity_instances
            }
            input_results = box.check(detect_data)
            results.append({'is_danger': True if len(input_results) > 0 else False, 'details': input_results})
        return results
