from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy.sql import text
from sqlalchemy import desc, and_

from backend.models import Category

if TYPE_CHECKING:
    from sqlalchemy.orm import Session as sql_Session



class CategoryQuery:
    def __init__(self, session:sql_Session):
        self.session = session
        self.account_id:int = None
    

    def category_exists(self, name:str, category_type:str) -> bool:
        result = self.session.query(Category).filter_by(name=name, category_type=category_type, account_id=self.account_id).first()
        return bool(result)


    def create_category(self, name:str, category_type:str, position:int):
        self.session.add(Category(name, category_type, position, self.account_id))
        self.session.commit()


    def get_available_position(self, category_type:str) -> int:
        last_category = self.session.query(Category).filter_by(category_type=category_type, account_id=self.account_id).order_by(desc(Category.position)).first()

        if last_category is None:
            return 0
        
        return last_category.position + 1


    def change_category_position(self, new_position:int, old_position:int, category_id:int, category_type:str):
        if new_position < old_position:
            self.session.query(Category).filter(and_(Category.position < old_position, Category.position >= new_position, Category.category_type == category_type, Category.account_id == self.account_id)).update(
                {Category.position: Category.position + 1}, synchronize_session=False
            )
        else:
            self.session.query(Category).filter(and_(Category.position > old_position, Category.position <= new_position, Category.category_type == category_type, Category.account_id == self.account_id)).update(
                {Category.position: Category.position - 1}, synchronize_session=False
            )
        self.session.query(Category).filter_by(id=category_id).update({Category.position: new_position}, synchronize_session=False)
        self.session.commit()


    def remove_position(self, category_id:int):
        position = self.session.query(Category).filter_by(id=category_id).first().position
        self.session.query(Category).filter(Category.position > position).update(
            {Category.position: Category.position - 1}, synchronize_session=False
        )
        self.session.commit()


    def get_category(self, name:str, category_type:str) -> Category:
        category = self.session.query(Category).filter_by(name=name, category_type=category_type, account_id=self.account_id).first()
        return category
    

    def get_all_categories(self) -> list[Category]:
        return self.session.query(Category).filter_by(account_id=self.account_id).order_by(Category.position).all()


    def rename_category(self, category_id:int, new_name:str):
        self.session.query(Category).filter_by(id=category_id).update({Category.name:new_name}, False)
        self.session.commit()


    def delete_category(self, category_id:int):
        self.remove_position(category_id)
        self.session.query(Category).filter_by(id=category_id).delete(False)
        self.session.commit()
        self.session.execute(text("VACUUM"))
        self.session.commit()
