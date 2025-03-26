from __future__ import annotations
from typing import TYPE_CHECKING
import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DATETIME, SmallInteger
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    current_balance = Column(Float, default=0)
    current_total_income = Column(Float, default=0)
    current_total_expenses = Column(Float, default=0)
    start_balance = Column(Float)
    created_date = Column(DATETIME(timezone=True), default=datetime.datetime.now)

    categories:Mapped[list[Category]] = relationship("Category", back_populates="account", cascade="all, delete, delete-orphan")


    def __init__(self, name:str, start_balance:float):
        self.name = name
        self.start_balance = start_balance


    def __repr__(self):
        return f"{self.name} created {self.created_date}"



class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    category_type = Column(String)
    position = Column(SmallInteger, nullable=False)

    account_id = Column(Integer, ForeignKey("accounts.id"))
    account:Mapped[Account] = relationship("Account", back_populates="categories")
    transactions:Mapped[list[Transaction]] = relationship("Transaction", back_populates="category", cascade="all, delete, delete-orphan")


    def __init__(self, name:str, category_type:str, position:int, account:int):
        self.name = name
        self.category_type = category_type
        self.position = position
        self.account_id = account
    

    def __repr__(self):
        return f"Name {self.name} type {self.category_type} account {self.account.name}"
    



class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(SmallInteger, nullable=False)
    month = Column(SmallInteger, nullable=False)
    day = Column(SmallInteger, nullable=False)
    value = Column(Float, nullable=False)
    name = Column(String)

    category_id = Column(Integer, ForeignKey("categories.id"))
    category:Mapped[Category] = relationship("Category", back_populates="transactions")


    def __init__(self, year:int, month:int, day:int, value:float, name:str, category:int):
        self.year = year
        self.month = month
        self.day = day
        self.value = value
        self.name = name
        self.category_id = category
    
    def __repr__(self):
        return f"{self.year}-{self.month}-{self.day}-{self.name} value:{self.value}"
    

    