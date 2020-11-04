# coding=utf-8

from __future__ import absolute_import
from wecube_plugins_itsdangerous.common import exceptions

from talos.core.i18n import _
from talos.db import crud
from talos.db import validator

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


class MatchParam(crud.ResourceBase):
    orm_meta = models_manage.MatchParam
    _default_order = ['-id']
    _validate = [
        crud.ColumnValidator(field='name',
                             rule=my_validator.LengthValidator(1, 36),
                             validate_on=['create:M', 'update:O']),
        crud.ColumnValidator(field='description',
                             rule=my_validator.LengthValidator(0, 63),
                             validate_on=['create:O', 'update:O'],
                             nullable=True),
        crud.ColumnValidator(field='type', rule_type='in', rule=['regex', 'cli'], validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='params', rule=validator.TypeValidator(dict), validate_on=('create:M', 'update:O')),
    ]


class Policy(crud.ResourceBase):
    orm_meta = models_manage.Policy
    _default_order = ['-id']
    _validate = [
        crud.ColumnValidator(field='name',
                             rule=my_validator.LengthValidator(1, 36),
                             validate_on=['create:M', 'update:O']),
        crud.ColumnValidator(field='description',
                             rule=my_validator.LengthValidator(0, 63),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='enabled', rule_type='in', rule=[0, 1], validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='rules',
                             rule=validator.TypeValidator(list),
                             validate_on=('create:O', 'update:O'),
                             orm_required=False)
    ]

    def _addtional_create(self, session, resource, created):
        if 'rules' in resource:
            refs = resource['rules']
            for ref in refs:
                new_ref = {}
                new_ref['policy_id'] = created['id']
                new_ref['rule_id'] = ref
                PolicyRule(transaction=session).create(new_ref)

    def _addtional_update(self, session, rid, resource, before_updated, after_updated):
        if 'rules' in resource:
            refs = resource['rules']
            PolicyRule(transaction=session).delete_all(filters={'policy_id': before_updated['id']})
            for ref in refs:
                new_ref = {}
                new_ref['policy_id'] = before_updated['id']
                new_ref['rule_id'] = ref
                PolicyRule(transaction=session).create(new_ref)

    def delete(self, rid, filters, detail):
        with self.transaction() as session:
            refs = BoxManage(session=session).list({'policy_id': rid})
            if refs:
                names = '|'.join([i['name'] for i in refs])
                raise exceptions.ConflictError(name=names)
            PolicyRule(transaction=session).delete_all(filters={'policy_id': rid})
            return super().delete(rid, filters, detail)


class Rule(crud.ResourceBase):
    orm_meta = models_manage.Rule
    _default_order = ['-id']
    _validate = [
        crud.ColumnValidator(field='name',
                             rule=my_validator.LengthValidator(1, 36),
                             validate_on=['create:M', 'update:O']),
        crud.ColumnValidator(field='description',
                             rule=my_validator.LengthValidator(0, 63),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='level',
                             rule=validator.NumberValidator(int, range_min=0),
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
                             rule=my_validator.LengthValidator(1, 512),
                             validate_on=('create:M', 'update:O')),
    ]


class Subject(crud.ResourceBase):
    orm_meta = models_manage.Subject
    _default_order = ['-id']
    _validate = [
        crud.ColumnValidator(field='name',
                             rule=my_validator.LengthValidator(1, 36),
                             validate_on=['create:M', 'update:O']),
        crud.ColumnValidator(field='description',
                             rule=my_validator.LengthValidator(0, 63),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='enabled', rule_type='in', rule=[0, 1], validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='targets',
                             rule=validator.TypeValidator(list),
                             validate_on=('create:O', 'update:O'),
                             orm_required=False)
    ]

    def _addtional_create(self, session, resource, created):
        if 'targets' in resource:
            refs = resource['targets']
            for ref in refs:
                new_ref = {}
                new_ref['subject_id'] = created['id']
                new_ref['target_id'] = ref
                SubjectTarget(transaction=session).create(new_ref)

    def _addtional_update(self, session, rid, resource, before_updated, after_updated):
        if 'targets' in resource:
            refs = resource['targets']
            SubjectTarget(transaction=session).delete_all(filters={'subject_id': before_updated['id']})
            for ref in refs:
                new_ref = {}
                new_ref['subject_id'] = before_updated['id']
                new_ref['target_id'] = ref
                SubjectTarget(transaction=session).create(new_ref)

    def delete(self, rid, filters, detail):
        with self.transaction() as session:
            refs = BoxManage(session=session).list({'subject_id': rid})
            if refs:
                names = '|'.join([i['name'] for i in refs])
                raise exceptions.ConflictError(name=names)
            SubjectTarget(transaction=session).delete_all(filters={'subject_id': rid})
            return super().delete(rid, filters, detail)


class Target(crud.ResourceBase):
    orm_meta = models_manage.Target
    _default_order = ['-id']
    _validate = [
        crud.ColumnValidator(field='name',
                             rule=my_validator.LengthValidator(1, 36),
                             validate_on=['create:M', 'update:O']),
        crud.ColumnValidator(field='enabled', rule_type='in', rule=[0, 1], validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='args_scope',
                             rule=my_validator.LengthValidator(0, 512),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
        crud.ColumnValidator(field='entity_scope',
                             rule=my_validator.LengthValidator(0, 512),
                             validate_on=('create:O', 'update:O'),
                             nullable=True),
    ]


class Box(crud.ResourceBase):
    # optimize for box query
    orm_meta = models_box.Box
    _default_order = ['-id']
    _dynamic_relationship = False


class BoxManage(crud.ResourceBase):
    orm_meta = models_manage.Box
    _default_order = ['-id']
    _validate = [
        crud.ColumnValidator(field='name',
                             rule=my_validator.LengthValidator(1, 36),
                             validate_on=['create:M', 'update:O']),
        crud.ColumnValidator(field='description',
                             rule=my_validator.LengthValidator(0, 63),
                             validate_on=['create:O', 'update:O'],
                             nullable=True),
        crud.ColumnValidator(field='policy_id', rule=BackRefValidator(Policy), validate_on=('create:M', 'update:O')),
        crud.ColumnValidator(field='subject_id', rule=BackRefValidator(Subject), validate_on=('create:M', 'update:O')),
    ]


class PolicyRule(crud.ResourceBase):
    orm_meta = models_manage.PolicyRule
    _validate = [
        crud.ColumnValidator(field='policy_id', validate_on=('create:M', 'update:M')),
        crud.ColumnValidator(field='rule_id', rule=BackRefValidator(Rule), validate_on=('create:M', 'update:M')),
    ]


class SubjectTarget(crud.ResourceBase):
    orm_meta = models_manage.SubjectTarget
    _validate = [
        crud.ColumnValidator(field='subject_id', validate_on=('create:M', 'update:M')),
        crud.ColumnValidator(field='target_id', rule=BackRefValidator(Target), validate_on=('create:M', 'update:M')),
    ]


class ServiceScript(crud.ResourceBase):
    orm_meta = models_manage.ServiceScript
    _default_order = ['-id']
    _validate = [
        crud.ColumnValidator(field='service',
                             rule=my_validator.LengthValidator(1, 63),
                             validate_on=['create:M', 'update:O']),
        crud.ColumnValidator(field='content_type',
                             rule_type='in',
                             rule=['shell', 'sql'],
                             validate_on=['create:O', 'update:O'],
                             nullable=True),
        crud.ColumnValidator(field='content_field',
                             rule=my_validator.LengthValidator(1, 63),
                             validate_on=['create:O', 'update:O'],
                             nullable=True),
        crud.ColumnValidator(field='endpoint_field',
                             rule=my_validator.LengthValidator(1, 63),
                             validate_on=['create:O', 'update:O'],
                             nullable=True),
    ]
