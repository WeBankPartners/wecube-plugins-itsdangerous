# coding=utf-8

from __future__ import absolute_import

from sqlalchemy import Column, ForeignKey, String, text, JSON
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from talos.db.dictbase import DictBase

Base = declarative_base()
metadata = Base.metadata


class MatchParam(Base, DictBase):
    __tablename__ = 'match_param'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(36), nullable=False)
    description = Column(String(63), server_default=text("''"), nullable=True)
    type = Column(String(36), nullable=False)
    params = Column(JSON, nullable=False)


class Policy(Base, DictBase):
    __tablename__ = 'policy'
    attributes = ['id', 'name', 'description', 'enabled', 'rules']
    detail_attributes = attributes
    summary_attributes = attributes

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(36), nullable=False)
    description = Column(String(63), server_default=text("''"), nullable=True)
    enabled = Column(TINYINT(4), nullable=False)

    rules = relationship("Rule", secondary="policy_rule", lazy='subquery')


class Rule(Base, DictBase):
    __tablename__ = 'rule'
    attributes = [
        'id', 'name', 'description', 'level', 'effect_on', 'enabled', 'match_type', 'match_param_id', 'match_value',
        'match_param'
    ]
    detail_attributes = attributes
    summary_attributes = attributes

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(36), nullable=False)
    description = Column(String(63), server_default=text("''"), nullable=True)
    level = Column(INTEGER(11), nullable=False)
    effect_on = Column(String(36), nullable=False)
    match_type = Column(String(36), nullable=False)
    match_param_id = Column(ForeignKey('match_param.id'), nullable=True)
    match_value = Column(String(512), nullable=False)
    enabled = Column(TINYINT(4), nullable=False)

    match_param = relationship('MatchParam', lazy=False)
    # policies = relationship("Policy", back_populates="policy_rule")


class Subject(Base, DictBase):
    __tablename__ = 'subject'
    attributes = ['id', 'name', 'description', 'enabled', 'targets']
    detail_attributes = attributes
    summary_attributes = attributes

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(36), nullable=False)
    description = Column(String(63), server_default=text("''"), nullable=True)
    enabled = Column(TINYINT(4), nullable=False)

    targets = relationship('Target', secondary='subject_target', lazy='subquery')


class Target(Base, DictBase):
    __tablename__ = 'target'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(36), nullable=False)
    args_scope = Column(String(512), nullable=True)
    entity_scope = Column(String(512), nullable=True)
    enabled = Column(TINYINT(4), nullable=False)

    # subjects = relationship('SubjectTarget', back_populates='target')


class Box(Base, DictBase):
    __tablename__ = 'box'
    attributes = ['id', 'name', 'description', 'policy_id', 'subject_id', 'policy', 'subject']
    detail_attributes = attributes
    summary_attributes = attributes

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(36), nullable=False)
    description = Column(String(63), server_default=text("''"), nullable=True)
    policy_id = Column(ForeignKey('policy.id'), nullable=False, index=True)
    subject_id = Column(ForeignKey('subject.id'), nullable=False, index=True)

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


class SerivceScript(Base, DictBase):
    __tablename__ = 'serivce_script'
    __table_args__ = {'comment': 'serivce script extraction '}

    id = Column(INTEGER(11), primary_key=True)
    service = Column(String(63), nullable=False)
    content_type = Column(String(36))
    content_field = Column(String(63))
    endpoint_field = Column(String(63))
