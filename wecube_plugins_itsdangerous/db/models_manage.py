# coding=utf-8

from __future__ import absolute_import

from sqlalchemy import Column, DateTime, ForeignKey, String, text, JSON
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from talos.db.dictbase import DictBase

Base = declarative_base()
metadata = Base.metadata


class MatchParam(Base, DictBase):
    __tablename__ = 'match_param'
    summary_attributes = ['id', 'name', 'type', 'params']

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(36), nullable=False)
    description = Column(String(63), server_default=text("''"), nullable=True)
    type = Column(String(36), nullable=False)
    params = Column(JSON, nullable=False)

    created_by = Column(String(36), nullable=True)
    created_time = Column(DateTime, nullable=True)
    updated_by = Column(String(36), nullable=True)
    updated_time = Column(DateTime, nullable=True)


class Policy(Base, DictBase):
    __tablename__ = 'policy'
    attributes = [
        'id', 'name', 'description', 'enabled', 'created_by', 'created_time', 'updated_by', 'updated_time', 'rules'
    ]
    detail_attributes = attributes
    summary_attributes = ['id', 'name', 'description', 'enabled']

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(36), nullable=False)
    description = Column(String(63), server_default=text("''"), nullable=True)
    enabled = Column(TINYINT(4), nullable=False)

    created_by = Column(String(36), nullable=True)
    created_time = Column(DateTime, nullable=True)
    updated_by = Column(String(36), nullable=True)
    updated_time = Column(DateTime, nullable=True)

    rules = relationship("Rule", secondary="policy_rule", lazy=False)


class Rule(Base, DictBase):
    __tablename__ = 'rule'
    attributes = [
        'id', 'name', 'description', 'level', 'effect_on', 'enabled', 'match_type', 'match_param_id', 'match_value',
        'created_by', 'created_time', 'updated_by', 'updated_time', 'match_param'
    ]
    detail_attributes = [
        'id', 'name', 'description', 'level', 'effect_on', 'enabled', 'match_type', 'match_param_id', 'match_value',
        'created_by', 'created_time', 'updated_by', 'updated_time', 'match_param', 'policies'
    ]
    summary_attributes = [
        'id', 'name', 'description', 'level', 'effect_on', 'enabled', 'match_type', 'match_param_id', 'match_value',
        'match_param'
    ]

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(36), nullable=False)
    description = Column(String(63), server_default=text("''"), nullable=True)
    level = Column(String(36), nullable=False)
    effect_on = Column(String(36), nullable=False)
    match_type = Column(String(36), nullable=False)
    match_param_id = Column(ForeignKey('match_param.id'), nullable=True)
    match_value = Column(String(512), nullable=False)
    enabled = Column(TINYINT(4), nullable=False)

    created_by = Column(String(36), nullable=True)
    created_time = Column(DateTime, nullable=True)
    updated_by = Column(String(36), nullable=True)
    updated_time = Column(DateTime, nullable=True)

    match_param = relationship('MatchParam', lazy=False)
    policies = relationship("Policy", secondary="policy_rule", lazy=True)


class Subject(Base, DictBase):
    __tablename__ = 'subject'
    attributes = [
        'id', 'name', 'description', 'enabled', 'created_by', 'created_time', 'updated_by', 'updated_time', 'targets'
    ]
    detail_attributes = attributes
    summary_attributes = ['id', 'name', 'description', 'enabled']

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(36), nullable=False)
    description = Column(String(63), server_default=text("''"), nullable=True)
    enabled = Column(TINYINT(4), nullable=False)

    created_by = Column(String(36), nullable=True)
    created_time = Column(DateTime, nullable=True)
    updated_by = Column(String(36), nullable=True)
    updated_time = Column(DateTime, nullable=True)

    targets = relationship('Target', secondary='subject_target', lazy=False)


class Target(Base, DictBase):
    __tablename__ = 'target'
    attributes = [
        'id', 'name', 'args_scope', 'entity_scope', 'enabled', 'created_by', 'created_time', 'updated_by',
        'updated_time'
    ]
    detail_attributes = [
        'id', 'name', 'args_scope', 'entity_scope', 'enabled', 'created_by', 'created_time', 'updated_by',
        'updated_time', 'subjects'
    ]
    summary_attributes = ['id', 'name', 'args_scope', 'entity_scope', 'enabled']

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(36), nullable=False)
    args_scope = Column(String(512), nullable=True)
    entity_scope = Column(String(512), nullable=True)
    enabled = Column(TINYINT(4), nullable=False)

    created_by = Column(String(36), nullable=True)
    created_time = Column(DateTime, nullable=True)
    updated_by = Column(String(36), nullable=True)
    updated_time = Column(DateTime, nullable=True)

    subjects = relationship('Subject', secondary="subject_target", lazy=True)


class Box(Base, DictBase):
    __tablename__ = 'box'
    attributes = [
        'id', 'name', 'description', 'policy_id', 'subject_id', 'enabled', 'created_by', 'created_time', 'updated_by',
        'updated_time', 'policy', 'subject'
    ]
    detail_attributes = attributes
    summary_attributes = attributes

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(36), nullable=False)
    description = Column(String(63), server_default=text("''"), nullable=True)
    policy_id = Column(ForeignKey('policy.id'), nullable=False, index=True)
    subject_id = Column(ForeignKey('subject.id'), nullable=False, index=True)
    enabled = Column(TINYINT(4), nullable=False)

    created_by = Column(String(36), nullable=True)
    created_time = Column(DateTime, nullable=True)
    updated_by = Column(String(36), nullable=True)
    updated_time = Column(DateTime, nullable=True)

    policy = relationship('Policy', lazy=False)
    subject = relationship('Subject', lazy=False)


class PolicyRule(Base, DictBase):
    __tablename__ = 'policy_rule'

    id = Column(INTEGER(11), primary_key=True)
    policy_id = Column(ForeignKey('policy.id'), nullable=False, index=True)
    rule_id = Column(ForeignKey('rule.id'), nullable=False, index=True)

    # policy = relationship('Policy', back_populates='rules')
    # rule = relationship('Rule', back_populates='policies')


class SubjectTarget(Base, DictBase):
    __tablename__ = 'subject_target'

    id = Column(INTEGER(11), primary_key=True)
    subject_id = Column(ForeignKey('subject.id'), nullable=False, index=True)
    target_id = Column(ForeignKey('target.id'), nullable=False, index=True)

    # subject = relationship('Subject', back_populates='targets')
    # target = relationship('Target', back_populates='subjects')


class ServiceScript(Base, DictBase):
    __tablename__ = 'service_script'
    __table_args__ = {'comment': 'serivce script extraction '}

    id = Column(INTEGER(11), primary_key=True)
    service = Column(String(63), nullable=False)
    content_type = Column(String(36))
    content_field = Column(String(63))
    endpoint_field = Column(String(63))
    endpoint_include = Column(String(255))

    created_by = Column(String(36), nullable=True)
    created_time = Column(DateTime, nullable=True)
    updated_by = Column(String(36), nullable=True)
    updated_time = Column(DateTime, nullable=True)
