# coding=utf-8

from __future__ import absolute_import

import logging

from talos.common import cache

from wecube_plugins_itsdangerous.apps.processor import detector
from wecube_plugins_itsdangerous.common import scope
from wecube_plugins_itsdangerous.db import resource

LOG = logging.getLogger(__name__)

Policy = resource.Policy
Subject = resource.Subject


class Box(resource.Box):

    def _get_rules(self, data):
        boxes = self.list(filters={'policy.enabled': 1, 'subject.enabled': 1})
        rules = {}
        for b in boxes:
            subject_included = False
            for target in b['subject']['targets']:
                target_included = []
                key = 'scope/target/%s' % target['id']
                cached = cache.get(key, 30)
                if cache.validate(cached) and cached:
                    target_included.append(True)
                else:
                    if target['enabled']:
                        if target['args_scope'] is not None:
                            target_included.append(scope.JsonScope(target['args_scope']).is_match(data))
                        else:
                            target_included.append(True)
                        if target_included and target['entity_scope'] is not None:
                            target_included.append(scope.WeCMDBScope(target['entity_scope']).is_match(data['entityInstances']))
                        else:
                            target_included.append(True)
                    else:
                        target_included.append(False)
                if False in target_included:
                    cache.set(key, False)
                    continue
                else:
                    cache.set(key, True)
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

    def check(self, data):
        with self.get_session() as session:
            results = []
            service_name = data['serviceName']
            input_params = data['inputParams']
            entity_instances = data['entityInstances']
            rules = self._get_rules(data)
            rules = self._rule_grouping(rules)
            for key, values in rules.items():
                # TODO: one or more scripts support
                script = input_params.get('script', '') or ''
                if key == 'filter':
                    results.extend(detector.JsonFilterDetector(data, values).check())
                elif key == 'cli':
                    results.extend(detector.BashCliDetector(script, values).check())
                elif key == 'sql':
                    results.extend(detector.SqlDetector(script, values).check())
                elif key == 'text':
                    results.extend(detector.LineTextDetector(script, values).check())
                elif key == 'fulltext':
                    results.extend(detector.FullTextDetector(script, values).check())
            return results
