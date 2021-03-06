# coding=utf-8

from __future__ import absolute_import
import datetime

from talos.core.i18n import _
from talos.db import crud
from talos.db import validator
from talos.utils import scoped_globals

from wecube_plugins_itsdangerous.common import exceptions
from wecube_plugins_itsdangerous.db import models_box
from wecube_plugins_itsdangerous.db import models_manage
from wecube_plugins_itsdangerous.db import validator as my_validator


class BackRefValidator(validator.NullValidator):
    def __init__(self, cls_res):
        self.cls_res = cls_res

    def validate(self, value):
        if self.cls_res().count(filters={'id': value}) == 0:
            return _('reference of %(resource)s(%(id)s) not found') % {'resource': self.cls_res.__name__, 'id': value}
        return True


class MetaCRUD(crud.ResourceBase):
    def _before_create(self, resource, validate):
        resource['created_by'] = scoped_globals.GLOBALS.request.auth_user or None
        resource['created_time'] = datetime.datetime.now()

    def _before_update(self, rid, resource, validate):
        resource['updated_by'] = scoped_globals.GLOBALS.request.auth_user or None
        resource['updated_time'] = datetime.datetime.now()


class MatchParam(MetaCRUD):
    orm_meta = models_manage.MatchParam
    _default_order = ['-id']
    _validate = [
        crud.ColumnValidator(field='name',
                             rule=my_validator.LengthValidator(1, 36),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='description',
                             rule=my_validator.LengthValidator(0, 63),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='type',
                             rule_type='in',
                             rule=['regex', 'cli', 'cli_handover'],
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='params', rule=validator.TypeValidator(dict), validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='created_by', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='created_time', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='updated_by', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='updated_time', validate_on=('create:O', 'update:O'), nullable=True)
    ]

    _validate_params_cli = [
        crud.ColumnValidator(field='name', rule=my_validator.LengthValidator(1, 36), validate_on=('create:M', )),
        crud.ColumnValidator(field='opt_strip_path',
                             rule_type='in',
                             rule=[True, False],
                             validate_on=('create:O', ),
                             nullable=True),
        crud.ColumnValidator(field='args', rule=validator.TypeValidator(list), validate_on=('create:M', ))
    ]

    _validate_params_cli_args = [
        crud.ColumnValidator(field='name', rule=my_validator.LengthValidator(1, 36), validate_on=('create:M', )),
        crud.ColumnValidator(field='shortcut',
                             rule=my_validator.LengthValidator(0, 255),
                             validate_on=('create:O', ),
                             nullable=True),
        crud.ColumnValidator(field='action',
                             rule_type='in',
                             rule=['store', 'store_true', 'store_false', 'count', 'append'],
                             validate_on=('create:O', )),
        crud.ColumnValidator(field='convert_int',
                             rule_type='in',
                             rule=[True, False],
                             validate_on=('create:O', ),
                             nullable=True),
        crud.ColumnValidator(field='repeatable',
                             rule=my_validator.RepeatableValidator(),
                             validate_on=('create:O', ),
                             nullable=True),
    ]

    def _addtional_create(self, session, resource, created):
        super()._addtional_create(session, resource, created)
        if created['type'] in ('cli', 'cli_handover'):
            params = created['params']
            self.validate(params, 'create', rule=self._validate_params_cli)
            args = params['args']
            for arg in args:
                self.validate(arg, 'create', rule=self._validate_params_cli_args)

    def _addtional_update(self, session, rid, resource, before_updated, after_updated):
        super()._addtional_update(session, rid, resource, before_updated, after_updated)
        if after_updated['type'] in ('cli', 'cli_handover'):
            params = after_updated['params']
            self.validate(params, 'create', rule=self._validate_params_cli)
            args = params['args']
            for arg in args:
                self.validate(arg, 'create', rule=self._validate_params_cli_args)

    def delete(self, rid, filters=None, detail=True):
        refs = Rule().list({'match_param_id': rid})
        if refs:
            names = '|'.join([i['name'] for i in refs])
            raise exceptions.ConflictError(oid=rid, name=names)
        return super().delete(rid, filters, detail)


class Policy(MetaCRUD):
    orm_meta = models_manage.Policy
    _default_order = ['-id']
    _validate = [
        crud.ColumnValidator(field='name',
                             rule=my_validator.LengthValidator(1, 36),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='description',
                             rule=my_validator.LengthValidator(0, 63),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='enabled', rule_type='in', rule=[0, 1], validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='created_by', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='created_time', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='updated_by', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='updated_time', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='rules',
                             rule=validator.TypeValidator(list),
                             validate_on=('create:O', 'update:O'),
                             orm_required=False)
    ]

    def _addtional_create(self, session, resource, created):
        if 'rules' in resource:
            refs = resource['rules']
            reduce_refs = list(set(refs))
            reduce_refs.sort(key=refs.index)
            for ref in reduce_refs:
                new_ref = {}
                new_ref['policy_id'] = created['id']
                new_ref['rule_id'] = ref
                PolicyRule(transaction=session).create(new_ref)

    def _addtional_update(self, session, rid, resource, before_updated, after_updated):
        if 'rules' in resource:
            refs = resource['rules']
            old_refs = [
                result['rule_id']
                for result in PolicyRule(session=session).list(filters={'policy_id': before_updated['id']})
            ]
            create_refs = list(set(refs) - set(old_refs))
            create_refs.sort(key=refs.index)
            delete_refs = set(old_refs) - set(refs)
            if delete_refs:
                PolicyRule(transaction=session).delete_all(filters={
                    'policy_id': before_updated['id'],
                    'rule_id': {
                        'in': list(delete_refs)
                    }
                })
            for ref in create_refs:
                new_ref = {}
                new_ref['policy_id'] = before_updated['id']
                new_ref['rule_id'] = ref
                PolicyRule(transaction=session).create(new_ref)

    def delete(self, rid, filters=None, detail=True):
        with self.transaction() as session:
            refs = BoxManage(session=session).list({'policy_id': rid})
            if refs:
                names = '|'.join([i['name'] for i in refs])
                raise exceptions.ConflictError(oid=rid, name=names)
            PolicyRule(transaction=session).delete_all(filters={'policy_id': rid})
            return super().delete(rid, filters, detail)


class Rule(MetaCRUD):
    orm_meta = models_manage.Rule
    _default_order = ['-id']
    _validate = [
        crud.ColumnValidator(field='name',
                             rule=my_validator.LengthValidator(1, 36),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='description',
                             rule=my_validator.LengthValidator(0, 63),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='level',
                             rule_type='in',
                             rule=['critical', 'high', 'medium', 'low'],
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='effect_on',
                             rule_type='in',
                             rule=['param', 'script'],
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='match_type',
                             rule_type='in',
                             rule=['filter', 'cli', 'sql', 'text', 'fulltext'],
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='match_param_id',
                             rule=BackRefValidator(MatchParam),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='enabled', rule_type='in', rule=[0, 1], validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='match_value',
                             rule=my_validator.LengthValidator(0, 512),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='created_by', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='created_time', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='updated_by', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='updated_time', validate_on=('create:O', 'update:O'), nullable=True),
    ]

    def create(self, resource, validate=True, detail=False):
        '''make detail False as default, or it will return policies.rules extra info[performance issue]'''
        return super().create(resource, validate=validate, detail=detail)

    def update(self, rid, resource, filters=None, validate=True, detail=False):
        '''make detail False as default, or it will return policies.rules extra info[performance issue]'''
        return super().update(rid, resource, filters=filters, validate=validate, detail=detail)

    def _addtional_validation(self, resource):
        if resource['effect_on'] == 'param' and resource['match_type'] not in ('filter', ):
            raise exceptions.ValidationError(attribute='match_type',
                                             msg=_('%(value)s is not acceptable, use %(fixed_value)s instead') % {
                                                 'value': resource['match_type'],
                                                 'fixed_value': 'filter'
                                             })
        if resource['effect_on'] == 'script' and resource['match_type'] not in ('cli', 'sql', 'text', 'fulltext'):
            raise exceptions.ValidationError(attribute='match_type',
                                             msg=_('%(value)s is not acceptable, use %(fixed_value)s instead') % {
                                                 'value': resource['match_type'],
                                                 'fixed_value': ('cli', 'sql', 'text', 'fulltext')
                                             })
        if resource['effect_on'] == 'script' and resource['match_type'] == 'cli' and not resource['match_param_id']:
            raise exceptions.FieldRequired(attribute='match_param_id')

    def _addtional_create(self, session, resource, created):
        self._addtional_validation(created)

    def _addtional_update(self, session, rid, resource, before_updated, after_updated):
        self._addtional_validation(after_updated)

    def delete(self, rid, filters=None, detail=True):
        ref = super().get(rid)
        if ref:
            names = '|'.join([i['name'] for i in ref['policies']])
            if names:
                raise exceptions.ConflictError(oid=rid, name=names)
        return super().delete(rid, filters, detail)


class Subject(MetaCRUD):
    orm_meta = models_manage.Subject
    _default_order = ['-id']
    _validate = [
        crud.ColumnValidator(field='name',
                             rule=my_validator.LengthValidator(1, 36),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='description',
                             rule=my_validator.LengthValidator(0, 63),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='enabled', rule_type='in', rule=[0, 1], validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='created_by', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='created_time', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='updated_by', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='updated_time', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='targets',
                             rule=validator.TypeValidator(list),
                             validate_on=('create:O', 'update:O'),
                             orm_required=False)
    ]

    def _addtional_create(self, session, resource, created):
        if 'targets' in resource:
            refs = resource['targets']
            reduce_refs = list(set(refs))
            reduce_refs.sort(key=refs.index)
            for ref in reduce_refs:
                new_ref = {}
                new_ref['subject_id'] = created['id']
                new_ref['target_id'] = ref
                SubjectTarget(transaction=session).create(new_ref)

    def _addtional_update(self, session, rid, resource, before_updated, after_updated):
        if 'targets' in resource:
            refs = resource['targets']
            old_refs = [
                result['target_id']
                for result in SubjectTarget(session=session).list(filters={'subject_id': before_updated['id']})
            ]
            create_refs = list(set(refs) - set(old_refs))
            create_refs.sort(key=refs.index)
            delete_refs = set(old_refs) - set(refs)
            if delete_refs:
                SubjectTarget(transaction=session).delete_all(filters={
                    'subject_id': before_updated['id'],
                    'target_id': {
                        'in': list(delete_refs)
                    }
                })
            for ref in create_refs:
                new_ref = {}
                new_ref['subject_id'] = before_updated['id']
                new_ref['target_id'] = ref
                SubjectTarget(transaction=session).create(new_ref)

    def delete(self, rid, filters=None, detail=True):
        with self.transaction() as session:
            refs = BoxManage(session=session).list({'subject_id': rid})
            if refs:
                names = '|'.join([i['name'] for i in refs])
                raise exceptions.ConflictError(oid=rid, name=names)
            SubjectTarget(transaction=session).delete_all(filters={'subject_id': rid})
            return super().delete(rid, filters, detail)


class Target(MetaCRUD):
    orm_meta = models_manage.Target
    _default_order = ['-id']
    _validate = [
        crud.ColumnValidator(field='name',
                             rule=my_validator.LengthValidator(1, 36),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='enabled', rule_type='in', rule=[0, 1], validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='args_scope',
                             rule=my_validator.LengthValidator(0, 512),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='entity_scope',
                             rule=my_validator.LengthValidator(0, 512),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='created_by', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='created_time', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='updated_by', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='updated_time', validate_on=('create:O', 'update:O'), nullable=True),
    ]

    def create(self, resource, validate=True, detail=False):
        '''make detail False as default, or it will return subjects.targets extra info[performance issue]'''
        return super().create(resource, validate=validate, detail=detail)

    def update(self, rid, resource, filters=None, validate=True, detail=False):
        '''make detail False as default, or it will return subjects.targets extra info[performance issue]'''
        return super().update(rid, resource, filters=filters, validate=validate, detail=detail)

    def delete(self, rid, filters=None, detail=True):
        ref = super().get(rid)
        if ref:
            names = '|'.join([i['name'] for i in ref['subjects']])
            if names:
                raise exceptions.ConflictError(oid=rid, name=names)
        return super().delete(rid, filters, detail)


class Box(MetaCRUD):
    # optimize for box query
    orm_meta = models_box.Box
    _default_order = ['-id']
    _dynamic_relationship = False


class BoxManage(MetaCRUD):
    orm_meta = models_manage.Box
    _default_order = ['-id']
    _validate = [
        crud.ColumnValidator(field='name',
                             rule=my_validator.LengthValidator(1, 36),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='description',
                             rule=my_validator.LengthValidator(0, 63),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='policy_id', rule=BackRefValidator(Policy), validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='subject_id', rule=BackRefValidator(Subject), validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='created_by', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='created_time', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='updated_by', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='updated_time', validate_on=('create:O', 'update:O'), nullable=True),
    ]


class PolicyRule(MetaCRUD):
    orm_meta = models_manage.PolicyRule
    _validate = [
        crud.ColumnValidator(field='policy_id', validate_on=('create:M', 'update:M')),
        crud.ColumnValidator(field='rule_id', rule=BackRefValidator(Rule), validate_on=('create:M', 'update:M')),
    ]


class SubjectTarget(MetaCRUD):
    orm_meta = models_manage.SubjectTarget
    _validate = [
        crud.ColumnValidator(field='subject_id', validate_on=('create:M', 'update:M')),
        crud.ColumnValidator(field='target_id', rule=BackRefValidator(Target), validate_on=('create:M', 'update:M')),
    ]


class ServiceScript(MetaCRUD):
    orm_meta = models_manage.ServiceScript
    _default_order = ['-id']
    _validate = [
        crud.ColumnValidator(field='service',
                             rule=my_validator.LengthValidator(1, 63),
                             validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='content_type',
                             rule_type='in',
                             rule=['shell', 'sql'],
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='content_field',
                             rule=my_validator.LengthValidator(0, 63),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='endpoint_field',
                             rule=my_validator.LengthValidator(0, 63),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='endpoint_include',
                             rule=my_validator.LengthValidator(0, 255),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='created_by', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='created_time', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='updated_by', validate_on=('create:O', 'update:O'), nullable=True),
        crud.ColumnValidator(field='updated_time', validate_on=('create:O', 'update:O'), nullable=True),
    ]

    def _before_create(self, resource, validate):
        super()._before_create(resource, validate)
        if ('content_field' not in resource
                and 'endpoint_field' not in resource) or ('content_field' in resource and not resource['content_field']
                                                          and 'endpoint_field' in resource
                                                          and not resource['endpoint_field']):
            raise exceptions.FieldRequired(attribute='content_field or endpoint_field')

    def _before_update(self, rid, resource, validate):
        super()._before_update(rid, resource, validate)
        if 'content_field' in resource and not resource[
                'content_field'] and 'endpoint_field' in resource and not resource['endpoint_field']:
            raise exceptions.ValidationError(attribute='content_field and endpoint_field',
                                             msg=_('specify at least one field content'))
