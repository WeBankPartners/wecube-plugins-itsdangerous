# coding=utf-8

from __future__ import absolute_import

import hashlib
import json
import logging

from talos.common import cache
from talos.db import crud

from wecube_plugins_itsdangerous.apps.processor import detector
from wecube_plugins_itsdangerous.common import reader
from wecube_plugins_itsdangerous.common import scope
from wecube_plugins_itsdangerous.common import exceptions
from wecube_plugins_itsdangerous.db import resource
from wecube_plugins_itsdangerous.db import validator as my_validator

LOG = logging.getLogger(__name__)


class Policy(resource.Policy):
    pass


class Rule(resource.Rule):
    pass


class MatchParam(resource.MatchParam):
    pass


class Subject(resource.Subject):
    pass


class Target(resource.Target):
    pass


class ServiceScript(resource.ServiceScript):
    pass


class BoxManage(resource.BoxManage):
    pass


class Box(resource.Box):
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
        crud.ColumnValidator(field='entityInstances',
                             rule=my_validator.TypeValidator(list),
                             validate_on=['check:M'],
                             nullable=False),
        crud.ColumnValidator(field='inputs',
                             rule=my_validator.TypeValidator(list),
                             validate_on=['check:M'],
                             nullable=False),
    ]

    def _get_rules(self, data, boxes=None):
        boxes = boxes or self.list(filters={'policy.enabled': 1, 'subject.enabled': 1})
        rules = {}
        hasher = hashlib.sha256()
        hasher.update(json.dumps(data).encode('utf-8'))
        digest = hasher.hexdigest()
        LOG.debug('scope test with data - %s ...', str(data)[:4096])
        for b in boxes:
            LOG.debug('scope test of box[%s - %s]', b['id'], b['name'])
            subject_included = False
            for target in b['subject']['targets']:
                target_included = True
                # target with the same data is cached
                key = 'scope/target/%s/data/%s' % (target['id'], digest)
                cached = cache.get(key, 30)
                if cache.validate(cached):
                    target_included = cached
                    LOG.debug('scope test of target[%s - %s]: %s', target['id'], target['name'],
                              ('accepted' if cached else 'rejected'))
                else:
                    LOG.debug('scope test of target[%s - %s]', target['id'], target['name'])
                    if target['enabled']:
                        if target['args_scope']:
                            target_included = scope.JsonScope(target['args_scope']).is_match(data)
                        else:
                            target_included = True
                        if target_included:
                            LOG.debug('args scope: accepted')
                            if target['entity_scope']:
                                target_included = scope.WeCubeScope(target['entity_scope']).is_match(
                                    data['entityInstances'])
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
                if target_included:
                    subject_included = True
                    break
            if subject_included:
                # extend box rules(enabled)
                for rule in b['policy']['rules']:
                    if rule['enabled']:
                        rules[rule['id']] = rule
                LOG.debug('scope test of box[%s - %s]: accepted, rules: %s', b['id'], b['name'], list(rules.keys()))
            else:
                LOG.debug('scope test of box[%s - %s]: rejected', b['id'], b['name'])
        return list(rules.values())

    def _rule_grouping(self, rules):
        # {'filter': [r1, r2], 'cli': [r3], 'sql/text/fulltext': [rx...]}
        results = {}
        for r in rules:
            rs = results.setdefault(r['match_type'], [])
            rs.append(r)
        return results

    def run(self, data, rid):
        refs = Box().list({'id': rid})
        if len(refs) == 0:
            raise exceptions.NotFoundError(resource='Box')
        return self.check(data, boxes=refs)

    def runall(self, data):
        '''
        input data:
        {
            // 操作人
            "operator": "admin",
            "serviceName": "a/b(c)/d",
            "servicePath": "a/b/run",
            "entityInstances": [{"id": "xxx_xxxxxx"}],
            // inputs param for serviceName
            "inputs": [/
                {"callbackParameter": "", "xml define prop": xxx},
                {},
                {}
            ]
        }
        '''
        from wecube_plugins_itsdangerous.apps.plugin import api as plugin_api
        results = []
        clean_data = crud.ColumnValidator.get_clean_data(self.runall_rules, data, 'check')
        service = clean_data['serviceName']
        entity_instances = clean_data['entityInstances']
        input_params = clean_data['inputs']
        for input_param in input_params:
            detect_data = {
                'serviceName': service,
                'servicePath': clean_data.get('servicePath', None),
                'inputParams': input_param,
                'scripts': plugin_api.ServiceScript().get_contents(service, input_param),
                'entityInstances': entity_instances
            }
            input_results = self.check(detect_data)
            results.append({'is_danger': True if len(input_results) > 0 else False, 'details': input_results})
        return results

    def check(self, data, boxes=None):
        '''
        data: {
            (Optional - JsonScope check)"serviceName": "a/b(c)/d", 
            (Optional - JsonScope check)"servicePath": "a/b/run", 
            (Optional - JsonScope check)"inputParams": {...service input params}, 
            (Must - script check)"scripts": [{"type": None/"sql"/"shell", "content": "...", "name": "additional name info"}], 
            (Must - WeCMDBScope check)"entityInstances": [{"guid": "xxx_xxxxxx"}]}
        '''

        results = []
        scripts = data['scripts']
        rules = self._get_rules(data, boxes=boxes)
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
        results.extend(detector.JsonFilterDetector(data, rules.get('filter', [])).check())
        return results
