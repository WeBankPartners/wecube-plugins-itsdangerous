# coding=utf-8

from __future__ import absolute_import

from talos.db import crud

from wecube_plugins_itsdangerous.db import models


class Policy(crud.ResourceBase):
    orm_meta = models.Policy


class Rule(crud.ResourceBase):
    orm_meta = models.Rule


class Subject(crud.ResourceBase):
    orm_meta = models.Subject


class Target(crud.ResourceBase):
    orm_meta = models.Target


class Box(crud.ResourceBase):
    orm_meta = models.Box
    _dynamic_relationship = False


class PolicyRule(crud.ResourceBase):
    orm_meta = models.PolicyRule


class SubjectTarget(crud.ResourceBase):
    orm_meta = models.SubjectTarget


class MatchParam(crud.ResourceBase):
    orm_meta = models.MatchParam