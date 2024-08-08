# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin

from apps import db, login_manager

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime


class Journal(db.Model, UserMixin):

    __tablename__ = 'journal'

    id = Column(Integer, primary_key=True)
    journal_at = Column(DateTime, unique=False)
    updated_at = Column(DateTime, unique=False)
    description = Column(Text, unique=False)
    debit = Column(Float)
    credit = Column(Float)
    account = Column(String(50))
    trx_id = Column(Integer, ForeignKey('transactions.id'))  # Foreign key relationship
    
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            setattr(self, property, value)

    def __repr__(self):
        return str(self.description)

class Account(db.Model):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f'{self.name}' 
    
class Transaction(db.Model, UserMixin):

    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    trx_at = Column(String(17), nullable=False, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    updated_at = Column(String(17), nullable=False, onupdate=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    description = Column(Text, unique=False)
    debit = Column(Float)
    credit = Column(Float)
    status = Column(String(10))
    owner_id = Column(Integer, ForeignKey('users.id', name='fk_transactions_owner_id', ondelete='CASCADE'))
    owner = relationship('Users', foreign_keys=[owner_id], backref='owned_transactions')
    
    treasurer_id = Column(Integer, ForeignKey('users.id', name='fk_transactions_treasurer_id', ondelete='CASCADE'))
    treasurer = relationship('Users', foreign_keys=[treasurer_id], backref='treasurer_transactions')
    
    account_id = Column(Integer, ForeignKey('accounts.id', name='fk_transactions_account_id', ondelete='CASCADE'))
    account = relationship('Account',foreign_keys=[account_id], backref='transactions')    # roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))
    
    __table_args__ = (
        UniqueConstraint('id', name='uq_transactions_id'),
        CheckConstraint('debit >= 0', name='chk_transactions_debit_positive'),
        CheckConstraint('credit >= 0', name='chk_transactions_credit_positive'),
    )
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            setattr(self, property, value)

