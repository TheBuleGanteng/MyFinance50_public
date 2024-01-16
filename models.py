from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

class User(db.Model):
    # Name of the table
    __tablename__ = 'users'
    # If a table w/ the same name already exists the new definition should replace the old one.
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False, unique=True)
    hash = db.Column(db.String, nullable=False)
    cash = db.Column(db.Float, nullable=False, default= 10000.00)

    # Relationship to Transactions (if you need to access user's transactions)
    transactions = relationship("Transaction", backref="user")

    # Converts the table to a dict, if needed (for example w/ API).
    def as_dict(self):
            return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    


class Transaction(db.Model):
    # Name of the table
    __tablename__ = 'transactions'
    # If a table w/ the same name already exists in the SQLAlchemy metadata, 
    # the new definition should replace the old one.
    __table_args__ = {'extend_existing': True}
    
    txn_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    txn_date = db.Column(db.DateTime, nullable=False)
    txn_type = db.Column(db.String, nullable=False)
    symbol = db.Column(db.String, nullable=False)
    txn_shrs = db.Column(db.Integer, nullable=False)
    txn_shr_price= db.Column(db.Float, nullable=False)
    txn_value= db.Column(db.Float, nullable=False)

    # Converts the table to a dict, if needed (for example w/ API).
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
