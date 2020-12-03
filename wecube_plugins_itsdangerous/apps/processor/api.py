# coding=utf-8

from __future__ import absolute_import

import glob
import hashlib
import json
import logging
import os
import os.path
import tempfile

import requests
from talos.common import cache
from talos.core import config, utils
from talos.core.i18n import _
from talos.db import crud
import texttable
from wecube_plugins_itsdangerous.apps.processor import detector
from wecube_plugins_itsdangerous.common import exceptions, reader, s3, scope, wecube
from wecube_plugins_itsdangerous.common import utils as plugin_utils
from wecube_plugins_itsdangerous.db import resource
from wecube_plugins_itsdangerous.db import validator as my_validator

LOG = logging.getLogger(__name__)
CONF = config.CONF


def download_from_url(dir_path, url, random_name=False):
    '''download file from url(s3/atrifact url)

    :param dir_path: file path to save, eg. /tmp/
    :type dir_path: str
    :param url: file url
    :type url: str
    :param random_name: generate uuid prefix name, defaults to False
    :type random_name: bool, optional
    :return: local file path
    :rtype: str
    '''
    filename = url.rsplit('/', 1)[-1]
    if random_name:
        filename = '%s_%s' % (utils.generate_uuid(), filename)
    filepath = os.path.join(dir_path, filename)
    if url.startswith(CONF.wecube.base_url):
        # nexus url
        token = wecube.get_wecube_token()
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
        client.download_file(filepath, CONF.wecube.s3.access_key, CONF.wecube.s3.secret_key)
    return filepath


def ensure_url_cached(url):
    '''download file form url, use cached file if available

    :param url: file url
    :type url: str
    :raises OSError: if timeout waiting for lock
    :return: local file path, filename
    :rtype: tuple(str, str)
    '''
    cache_dir = CONF.pakcage_cache_dir
    # make dir if not exist
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)
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


class Policy(resource.Policy):
    '''
    Policy Resource for CRUD
    '''
    pass


class Rule(resource.Rule):
    '''
    Rule Resource for CRUD
    '''
    pass


class MatchParam(resource.MatchParam):
    '''
    MatchParam Resource for CRUD
    '''
    def get_args(self, rid):
        ref = self.get(rid)
        results = []
        if ref:
            for arg in ref['params'].get('args', []):
                results.append({'type': 'string', 'name': arg['name']})
        return results


class Subject(resource.Subject):
    '''
    Subject Resource for CRUD
    '''
    pass


class Target(resource.Target):
    '''
    Target Resource for CRUD
    '''
    pass


class ServiceScript(resource.ServiceScript):
    '''
    ServiceScript Resource for CRUD
    '''
    def get_contents(self, service, plugin_param):
        '''get script contents from param according to service definition

        :param service: service name, eg. a/b(c)/d
        :type service: str
        :param plugin_param: service param instance
        :type plugin_param: dict
        :return: list of {'type': None/'sql'/'shell', 'content': '', 'name': ''}
        :rtype: list
        '''
        def _file_extension_supported(extensions, filename):
            for e in extensions:
                if filename.endswith(e):
                    return True
            return False

        # [{"type": None/"sql"/"shell", "content": "...", "name": "additional name info"}]
        scripts = []
        script_locations = self.list(filters={'service': service})
        if len(script_locations) == 0:
            LOG.warn('service_script[%s] not found, get_contents will return empty content', service)
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


class BoxManage(resource.BoxManage):
    '''
    Rule Resource for CRUD
    '''
    pass


class Box(resource.Box):
    '''
    Rule Resource for CRUD
    '''
    runall_rules = [
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
        crud.ColumnValidator(field='entityType',
                             rule=my_validator.LengthValidator(0, 255),
                             validate_on=['check:O'],
                             nullable=True),
        crud.ColumnValidator(field='entityInstances',
                             rule=my_validator.TypeValidator(list),
                             validate_on=['check:M'],
                             nullable=False),
        crud.ColumnValidator(field='inputParams',
                             rule=my_validator.TypeValidator(list),
                             validate_on=['check:M'],
                             nullable=False),
    ]

    def _get_rules(self, data, boxes=None, without_subject_test=False):
        boxes = boxes or self.list(filters={'policy.enabled': 1, 'subject.enabled': 1, 'enabled': 1})
        rules = {}
        hasher = hashlib.sha256()
        hasher.update(json.dumps(data).encode('utf-8'))
        digest = hasher.hexdigest()
        LOG.debug('scope test with data - %s ...', str(data)[:4096])
        for b in boxes:
            LOG.info('scope test of box[%s - %s]', b['id'], b['name'])
            subject_included = False
            if without_subject_test:
                subject_included = True
            else:
                for target in b['subject']['targets']:
                    target_included = True
                    # target with the same data is cached
                    key = 'scope/target/%s/data/%s' % (target['id'], digest)
                    cached = cache.get(key, 10)
                    if cache.validate(cached):
                        target_included = cached
                        LOG.debug('scope test of target[%s - %s]: %s', target['id'], target['name'],
                                  ('accepted' if cached else 'rejected'))
                    else:
                        LOG.debug('scope test of target[%s - %s]', target['id'], target['name'])
                        if target['enabled']:
                            # jsonscope match & exprscope match
                            if target['args_scope']:
                                target_included = scope.JsonScope(target['args_scope']).is_match(data)
                            else:
                                target_included = True
                            if target_included:
                                LOG.debug('args scope: accepted')
                                if target['entity_scope']:
                                    target_included = scope.WeCubeScope(target['entity_scope']).is_match(
                                        data['entityInstances'], data.get('entityType', None))
                                else:
                                    target_included = True
                                if target_included:
                                    LOG.debug('entity scope: accepted')
                                else:
                                    LOG.debug('entity scope: rejected')
                            else:
                                LOG.debug('args scope: rejected')
                        else:
                            LOG.debug('target: disabled')
                            target_included = False
                    cache.set(key, target_included)
                    # if any target are included, means subject is inlcuded
                    if target_included:
                        subject_included = True
                        break
            if subject_included:
                # extend box rules(enabled)
                new_rules_map = {}
                for rule in b['policy']['rules']:
                    if rule['enabled']:
                        new_rules_map[rule['id']] = rule
                rules.update(new_rules_map)
                LOG.info('scope test of box[%s - %s]: accepted, rules: %s', b['id'], b['name'],
                         list(new_rules_map.keys()))
            else:
                LOG.info('scope test of box[%s - %s]: rejected', b['id'], b['name'])
        return list(rules.values())

    def _rule_grouping(self, rules):
        # {'filter': [r1, r2], 'cli': [r3], 'sql/text/fulltext/..': [rx...]}
        results = {}
        for r in rules:
            rs = results.setdefault(r['match_type'], [])
            rs.append(r)
        return results

    def simplerun(self, data, rid):
        '''run box[rid] rule check

        :param data: see function check
        :type data: dict
        :param rid: box id
        :type rid: any
        :raises exceptions.NotFoundError: if id of box not found
        :return: see function check
        :rtype: see function check
        '''
        # check even box is diabled
        refs = self.list({'id': rid})
        if len(refs) == 0:
            raise exceptions.NotFoundError(resource='Box')
        return self.check(data, boxes=refs, without_subject_test=True)

    def plugin_check(self, data):
        '''run plugin params check

        :param data: input data
        {
            "operator": "admin",
            "serviceName": "qcloud/vm(resource)/create",
            "servicePath": "/qcloud/v1/vm/create",
            "entityType": "wecmdb:host_resource_instance",
            "entityInstances": [{"id": "xxx_xxxxxx"}],
            // inputs param for serviceName
            "inputParams": [
                {"xml define prop": xxx},
                {},
                {}
            ]
        }

        :return: see funcion check
        :rtype: see funcion check
        '''
        results = []
        clean_data = crud.ColumnValidator.get_clean_data(self.runall_rules, data, 'check')
        service = clean_data['serviceName']
        entity_instances = clean_data['entityInstances']
        input_params = clean_data['inputParams']
        for input_param in input_params:
            detect_data = {
                "operator": clean_data.get('operator', None),
                'serviceName': service,
                'servicePath': clean_data.get('servicePath', None),
                'inputParams': input_param,
                'scripts': ServiceScript().get_contents(service, input_param),
                'entityType': clean_data.get('entityType', None),
                'entityInstances': entity_instances
            }
            input_results = self.check(detect_data)
            results.extend(input_results)
        text_output = ''
        if results:
            table = texttable.Texttable(max_width=120)
            # {
            # 'lineno': [start, end], 'level': level of rule,
            # 'content': content, 'message': rule name, 'script_name': script name
            # }
            table.set_cols_align(["c", "l", "l", "l"])
            table.set_cols_valign(["m", "m", "m", "m"])
            table.header([_("Line"), _("Content"), _("Message"), _('Source Script')])
            for ret in results:
                table.add_row([
                    '%s-%s' % (ret['lineno'][0], ret['lineno'][1]), ret['content'], ret['message'], ret['script_name']
                ])
            text_output = table.draw()
        return {'text': text_output, 'data': results}

    def check(self, data, boxes=None, without_subject_test=False):
        '''check script & param with boxes, return dangerous contents & rule name

        :param data: data with param & script content
        {
            (Optional - JsonScope check)"operator": "admin",
            (Optional - JsonScope check)"serviceName": "qcloud/vm(resource)/create",
            (Optional - JsonScope check)"servicePath": "/qcloud/v1/vm/create",
            (Optional - JsonScope check)"inputParams": {...service input params},
            (Must - script check)"scripts": [{"type": None/"sql"/"shell", "content": "...", "name": "filename"}],
            (Optional - EntityScope check)"entityType": "wecmdb:host_resource_instance",
            (Must - EntityScope check)"entityInstances": [{"id": "xxx_xxxxxx"}]}
        :type data: dict
        :param boxes: specific boxes if any, defaults to None, mean all boxes
        :type boxes: list of Box, optional
        :return: list of {'lineno': [start, end], 'level': level of rule, 
                          'content': content, 'message': rule name, 'script_name': script name}
        :rtype: list
        '''

        results = []
        scripts = data['scripts']
        rules = self._get_rules(data, boxes=boxes, without_subject_test=without_subject_test)
        rules = self._rule_grouping(rules)
        for item in scripts:
            script_name = item.get('name', '') or ''
            script_content = item.get('content', '') or ''
            script_type = item.get('type', None)
            for key, values in rules.items():
                script_results = []
                if not script_type:
                    script_type = reader.guess(script_content) or 'text'
                if key == 'cli' and script_type == 'shell':
                    script_results = detector.BashCliDetector(script_content, values).check()
                elif key == 'sql' and script_type == 'sql':
                    script_results = detector.SqlDetector(script_content, values).check()
                elif key == 'text':
                    script_results = detector.LineTextDetector(script_content, values).check()
                elif key == 'fulltext':
                    script_results = detector.FullTextDetector(script_content, values).check()
                for r in script_results:
                    r['script_name'] = script_name
                results.extend(script_results)
        # check filter rules global
        json_results = detector.JsonFilterDetector(data, rules.get('filter', [])).check()
        for r in json_results:
            r['script_name'] = ''
        results.extend(json_results)
        return results


class WecubeService(object):
    def list(self, filters=None, orders=None, offset=None, limit=None, hooks=None):
        results = []
        service_name = filters.get('serviceName', '') or ''
        client = wecube.WeCubeClient(CONF.wecube.base_url)
        key = '/platform/v1/plugins/interfaces/enabled'
        cached = cache.get(key, 15)
        if cache.validate(cached):
            resp = cached
        else:
            resp = client.retrieve('/platform/v1/plugins/interfaces/enabled')
            cache.set(key, resp)
        for interface in resp['data']:
            if interface['serviceName'] == service_name:
                for param in interface['inputParameters']:
                    results.append({'type': param['dataType'], 'name': 'inputParams.' + param['name']})
        return results