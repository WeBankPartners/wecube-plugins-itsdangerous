# coding=utf-8

from __future__ import absolute_import

import hashlib
import json
import logging

from talos.common import cache

from wecube_plugins_itsdangerous.apps.processor import detector
from wecube_plugins_itsdangerous.common import reader
from wecube_plugins_itsdangerous.common import scope
from wecube_plugins_itsdangerous.db import resource

LOG = logging.getLogger(__name__)

Policy = resource.Policy
Subject = resource.Subject


class Box(resource.Box):

    def _get_rules(self, data, boxes=None):
        boxes = boxes or self.list(filters={'policy.enabled': 1, 'subject.enabled': 1})
        rules = {}
        hasher = hashlib.sha256()
        hasher.update(json.dumps(data).encode('utf-8'))
        digest = hasher.hexdigest()
        for b in boxes:
            subject_included = False
            for target in b['subject']['targets']:
                target_included = True
                # target with the same data is cached
                key = 'scope/target/%s/data/%s' % (target['id'], digest)
                cached = cache.get(key, 30)
                if cache.validate(cached):
                    target_included = cached
                else:
                    if target['enabled']:
                        if target['args_scope'] is not None:
                            target_included = scope.JsonScope(target['args_scope']).is_match(data)
                        else:
                            target_included = True
                        if target_included:
                            if target['entity_scope'] is not None:
                                target_included = scope.WeCMDBScope(target['entity_scope']).is_match(data['entityInstances'])
                            else:
                                target_included = True
                    else:
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
        return list(rules.values())

    def _rule_grouping(self, rules):
        # {'filter': [r1, r2], 'cli': [r3], 'sql/text/fulltext': [rx...]}
        results = {}
        for r in rules:
            rs = results.setdefault(r['match_type'], [])
            rs.append(r)
        return results

    def check(self, data, boxes=None):
        results = []
        service_name = data['serviceName']
        input_params = data['inputParams']
        entity_instances = data['entityInstances']
        # TODO: one or more scripts support
        script = input_params.get('script', '') or ''
        script_type = input_params.get('script_type', None)
        rules = self._get_rules(data, boxes=boxes)
        rules = self._rule_grouping(rules)
        for key, values in rules.items():
            if not script_type:
                script_type = reader.guess(script) or 'text'
            if key == 'filter':
                results.extend(detector.JsonFilterDetector(data, values).check())
            elif key == 'cli' and script_type == 'shell':
                results.extend(detector.BashCliDetector(script, values).check())
            elif key == 'sql' and script_type == 'sql':
                results.extend(detector.SqlDetector(script, values).check())
            elif key == 'text':
                results.extend(detector.LineTextDetector(script, values).check())
            elif key == 'fulltext':
                results.extend(detector.FullTextDetector(script, values).check())
        return results
