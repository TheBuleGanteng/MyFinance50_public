from extensions import db
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Instructions for update:
# Step 1: flask db migrate -m "XX MESSAGE HERE XX"
# Step 2: flask db upgrade

class User(db.Model):
    # Name of the table
    __tablename__ = 'users'
    # If a table w/ the same name already exists the new definition should replace the old one.
    __table_args__ = (
        UniqueConstraint('username', 'email', name='uq_users_username_email'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_first = db.Column(db.String, nullable=False, default="no_entry")
    name_last = db.Column(db.String, nullable=False, default="no_entry")
    username = db.Column(db.String, nullable=False, unique=True, default="no_entry")
    email = db.Column(db.String, nullable=False, unique=True, default="no_entry")
    confirmed = db.Column(db.String, nullable=False, default = 'No')
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    hash = db.Column(db.String, nullable=False)
    cash = db.Column(db.Float(precision=2), nullable=False, default= 10000.00)
    accounting_method = db.Column(db.String, nullable=False, default='FIFO')
    tax_loss_offsets = db.Column(db.String, nullable=False, default='On')
    tax_rate_STCG = db.Column(db.Float, nullable=False, default= 15.00)
    tax_rate_LTCG = db.Column(db.Float, nullable=False, default= 30.00)

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
    
    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    type = db.Column(db.String, nullable=False)
    symbol = db.Column(db.String, nullable=False)
    shares = db.Column(db.Integer, nullable=False)
    transaction_value_per_share= db.Column(db.Float(precision=2), nullable=False)
    transaction_value_total= db.Column(db.Float(precision=2), nullable=False)

    # Converts the table to a dict, if needed (for example w/ API).
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Listing(db.Model):
    # Name of the table
    __tablename__ = 'listings'
    # If a table w/ the same name already exists in the SQLAlchemy metadata, 
    # the new definition should replace the old one.
    __table_args__ = {'extend_existing': True}
    
    symbol = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)
    exchange = db.Column(db.String)
    exchange_short = db.Column(db.String)
    listing_type= db.Column(db.String)

    # Converts the table to a dict, if needed (for example w/ API).
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
