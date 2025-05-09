from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy.sql import text
from sqlalchemy import desc, and_

from backend.models import Category
from AppObjects.logger import get_logger

if TYPE_CHECKING:
    from sqlalchemy.orm import Session as sql_Session



logger = get_logger(__name__)

class CategoryQuery:
    """This class is used to manage categories and related data in the database."""

    def __init__(self, session:sql_Session) -> None:
        self.session = session
        self.account_id:int
    

    def category_exists(self, name:str, category_type:str) -> bool:
        """Check if a category with the given name and type exists in the database.

            Arguments
            ---------
                `name` : (str) - Name of the category to check.
                `category_type` : (str) - Type of the category (income or expense).
            Returns
            -------
                `bool` - True if the category exists, False otherwise.
        """

        result = self.session.query(Category).filter_by(name=name, category_type=category_type, account_id=self.account_id).first()
        return bool(result)


    def create_category(self, name:str, category_type:str, position:int) -> None:
        """Create a new category in the database.

            Arguments
            ---------
                `name` : (str) - Name of the category to create.
                `category_type` : (str) - Type of the category (income or expense).
                `position` : (int) - Position of the category for sorting.
        """

        self.session.add(Category(name=name, category_type=category_type, position=position, account_id=self.account_id))
        self.session.commit()


    def get_available_position(self, category_type:str) -> int:
        """Get the next available position for a category of the given type.

            Arguments
            ---------
                `category_type` : (str) - Type of the category (income or expense).
            Returns
            -------
                `int` - Next available position for the category.
        """
        last_category = self.session.query(Category).filter_by(category_type=category_type, account_id=self.account_id).order_by(desc(Category.position)).first()

        if last_category is None:
            return 0
        
        return last_category.position + 1


    def change_category_position(self, new_position:int, old_position:int, category_id:int, category_type:str) -> None:
        """Change the position of a category in the database.

            Arguments
            ---------
                `new_position` : (int) - New position of the category.
                `old_position` : (int) - Old position of the category.
                `category_id` : (int) - ID of the category to change.
                `category_type` : (str) - Type of the category (income or expense).
        """

        if new_position < old_position:
            self.session.query(Category).filter(and_(Category.position < old_position, Category.position >= new_position, Category.category_type == category_type, Category.account_id == self.account_id)).update(
                {Category.position: Category.position + 1}, synchronize_session=False)
        else:
            self.session.query(Category).filter(and_(Category.position > old_position, Category.position <= new_position, Category.category_type == category_type, Category.account_id == self.account_id)).update(
                {Category.position: Category.position - 1}, synchronize_session=False)
        self.session.query(Category).filter_by(id=category_id).update({Category.position: new_position}, synchronize_session=False)
        self.session.commit()


    def remove_position(self, category_id:int) -> None:
        """Remove the position of a category in the database.

            Arguments
            ---------
                `category_id` : (int) - ID of the category to remove.
        """

        category = self.session.query(Category).filter_by(id=category_id).first()

        if category:
            self.session.query(Category).filter(Category.position > category.position).update(
                {Category.position: Category.position - 1}, synchronize_session=False)
            self.session.commit()
        else:
            logger.error(f"Category with ID {category_id} not found.")


    def get_category(self, name:str, category_type:str) -> Category|None:
        """Get a category by its name and type.

            Arguments
            ---------
                `name` : (str) - Name of the category to get.
                `category_type` : (str) - Type of the category (income or expense).
            Returns
            -------
                `Category` - The category object if found, None otherwise.
        """

        category = self.session.query(Category).filter_by(name=name, category_type=category_type, account_id=self.account_id).first()

        if category:
            return category
        else:
            logger.error(f"Category with name {name} and type {category_type} not found. Although it should be there.")
            return None
            
    

    def get_all_categories(self) -> list[Category]:
        """Get all categories from the database.

            Returns
            -------
                `list[Category]` - List of all categories in the database.
        """

        return self.session.query(Category).filter_by(account_id=self.account_id).order_by(Category.position).all()


    def rename_category(self, category_id:int, new_name:str) -> None:
        """Rename a category in the database.

            Arguments
            ---------
                `category_id` : (int) - ID of the category to rename.
                `new_name` : (str) - New name of the category.
        """
        self.session.query(Category).filter_by(id=category_id).update({Category.name:new_name}, False)
        self.session.commit()


    def delete_category(self, category_id:int) -> None:
        """Delete a category from the database.

            Arguments
            ---------
                `category_id` : (int) - ID of the category to delete.
        """
        self.remove_position(category_id)
        self.session.query(Category).filter_by(id=category_id).delete(False)
        self.session.commit()
        self.session.execute(text("VACUUM"))
        self.session.commit()
