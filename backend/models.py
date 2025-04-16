from __future__ import annotations
from typing import Any
import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, SmallInteger
from sqlalchemy.orm import Mapped, DeclarativeBase, relationship, mapped_column



class Base(DeclarativeBase):
    """Base class for all models in the application."""
    pass



class Account(Base):
    """Represents an account in the application."""

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    current_balance: Mapped[float] = mapped_column(Float, default=0)
    current_total_income: Mapped[float] = mapped_column(Float, default=0)
    current_total_expenses: Mapped[float] = mapped_column(Float, default=0)
    start_balance: Mapped[float] = mapped_column(Float)
    created_date: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.now
    )

    categories: Mapped[list["Category"]] = relationship(
        back_populates="account",
        cascade="all, delete, delete-orphan"
    )


    # def __init__(self, name:Column[str], start_balance:Column[float]):
    #     self.name = name
    #     self.start_balance = start_balance


    def __repr__(self):
        return f"{self.name} created {self.created_date}"



class Category(Base):
    """Represents a category in the application."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    category_type: Mapped[str] = mapped_column(String)
    position: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    account: Mapped[Account] = relationship(back_populates="categories")
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="category",
        cascade="all, delete, delete-orphan"
    )


    # def __init__(self, name:Column[str], category_type:Column[str], position:Column[int], account:Column[int]):
    #     self.name = name
    #     self.category_type = category_type
    #     self.position = position
    #     self.account_id = account
    

    def __repr__(self):
        return f"Name {self.name} type {self.category_type} account {self.account.name}"
    



class Transaction(Base):
    """Represents a transaction in the application."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    day: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    name: Mapped[str | None] = mapped_column(String)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship(
        back_populates="transactions"
    )


    # def __init__(self, year:Column[int], month:Column[int], day:Column[int], value:Column[float], name:Column[str], category:Column[int]):
    #     self.year = year
    #     self.month = month
    #     self.day = day
    #     self.value = value
    #     self.name = name
    #     self.category_id = category
    
    def __repr__(self):
        return f"{self.year}-{self.month}-{self.day}-{self.name} value:{self.value}"
    

    