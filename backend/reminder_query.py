from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import date
from sqlalchemy import and_
from sqlalchemy.orm import joinedload

from backend.models import Category, MonthlyReminder, Transaction
from GeneralTools.Utils import get_covered_period, shift_month, get_due_date_for_covered_month
from AppObjects.logger import get_logger

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker, Session as sql_Session



logger = get_logger(__name__)

class ReminderQuery:
    """This class is used to manage monthly reminders of the current account in the database.
    Names are compared with `strip().casefold()` in Python because SQLite `lower()` is ASCII-only.
    """

    def __init__(self, session_factory:sessionmaker[sql_Session]) -> None:
        self.session_factory = session_factory
        self.account_id:int


    def get_all_reminders(self) -> list[MonthlyReminder]:
        """Get all reminders of the current account with their categories loaded.

            Returns
            -------
                `list[MonthlyReminder]` - Reminders ordered by next due date and name.
        """

        with self.session_factory() as session:
            with session.begin():
                return session.query(MonthlyReminder).join(Category).options(
                    joinedload(MonthlyReminder.category)
                ).filter(
                    Category.account_id == self.account_id
                ).order_by(MonthlyReminder.next_due_date, MonthlyReminder.name).all()


    def get_reminder(self, reminder_id:int) -> MonthlyReminder:
        """Get a reminder of the current account by its ID with its category loaded.

            Arguments
            ---------
                `reminder_id` : (int) - ID of the reminder.
            Returns
            -------
                `MonthlyReminder` - The reminder, raises RuntimeError if not found.
        """

        with self.session_factory() as session:
            with session.begin():
                reminder = session.query(MonthlyReminder).join(Category).options(
                    joinedload(MonthlyReminder.category)
                ).filter(and_(
                    MonthlyReminder.id == reminder_id,
                    Category.account_id == self.account_id
                )).first()

                if reminder is None:
                    logger.error(f"Reminder with ID {reminder_id} not found for account ID {self.account_id}.")
                    raise RuntimeError(f"Reminder with ID {reminder_id} not found for account ID {self.account_id}.")
                return reminder


    def reminder_name_exists(self, name:str, exclude_reminder_id:int|None = None) -> bool:
        """Check case-insensitively if a reminder with the given name exists in the current account.

            Arguments
            ---------
                `name` : (str) - Name to check.
                `exclude_reminder_id` : (int|None) - Reminder ID to skip (used when the reminder itself is updated).
            Returns
            -------
                `bool` - True if the name is already used, False otherwise.
        """

        normalized_name = name.strip().casefold()
        with self.session_factory() as session:
            with session.begin():
                rows = session.query(MonthlyReminder.id, MonthlyReminder.name).join(Category).filter(
                    Category.account_id == self.account_id
                ).all()

        return any(
            row_name.strip().casefold() == normalized_name and row_id != exclude_reminder_id
            for row_id, row_name in rows
        )


    def create_reminder(
            self,
            name:str,
            category_id:int,
            value:float|None,
            day:int|None,
            next_due_date:date
        ) -> MonthlyReminder:
        """Create a new reminder.

            Arguments
            ---------
                `name` : (str) - Reminder name.
                `category_id` : (int) - Category ID.
                `value` : (float|None) - Expected value.
                `day` : (int|None) - Day of the month.
                `next_due_date` : (date) - First due date.
            Returns
            -------
                `MonthlyReminder` - The created reminder.
        """

        with self.session_factory() as session:
            with session.begin():
                reminder = MonthlyReminder(
                    name=name, category_id=category_id, value=value, day=day, next_due_date=next_due_date
                )
                session.add(reminder)

        logger.info(
            f'[ENTITY: REMINDER] [ACTION: CREATED] name="{name}" category_id={category_id} value={value} day={day} '
            f'next_due_date={next_due_date}'
        )
        return reminder


    def update_reminder(
            self,
            reminder_id:int,
            name:str,
            category_id:int,
            value:float|None,
            day:int|None,
            next_due_date:date
        ) -> None:
        """Update a reminder.

            Arguments
            ---------
                `reminder_id` : (int) - ID of the reminder to update.
                `name` : (str) - New name.
                `category_id` : (int) - New category ID.
                `value` : (float|None) - New expected value.
                `day` : (int|None) - New day of the month.
                `next_due_date` : (date) - New next due date.
        """

        with self.session_factory() as session:
            with session.begin():
                reminder = session.get(MonthlyReminder, reminder_id)
                if reminder is None:
                    logger.error(f"Reminder with ID {reminder_id} not found. Reminder can't be updated.")
                    raise RuntimeError(f"Reminder with ID {reminder_id} not found. Reminder can't be updated.")

                old_name = reminder.name
                reminder.name = name
                reminder.category_id = category_id
                reminder.value = value
                reminder.day = day
                reminder.next_due_date = next_due_date

        logger.info(
            f'[ENTITY: REMINDER] [ACTION: UPDATED] id={reminder_id} old_name="{old_name}" name="{name}" '
            f'category_id={category_id} value={value} day={day} next_due_date={next_due_date}'
        )


    def delete_reminder(self, reminder_id:int) -> None:
        """Delete a reminder.

            Arguments
            ---------
                `reminder_id` : (int) - ID of the reminder to delete.
        """

        with self.session_factory() as session:
            with session.begin():
                reminder = session.get(MonthlyReminder, reminder_id)
                if reminder is None:
                    logger.error(f"Reminder with ID {reminder_id} not found. Reminder can't be deleted.")
                    raise RuntimeError(f"Reminder with ID {reminder_id} not found. Reminder can't be deleted.")

                name = reminder.name
                session.delete(reminder)

        logger.info(f'[ENTITY: REMINDER] [ACTION: DELETED] id={reminder_id} name="{name}"')


    def update_next_due_date(self, reminder_id:int) -> date:
        """Shift the reminder next due date forward by one month.

            Arguments
            ---------
                `reminder_id` : (int) - ID of the reminder.
            Returns
            -------
                `date` - The new next due date.
        """

        with self.session_factory() as session:
            with session.begin():
                reminder = session.get(MonthlyReminder, reminder_id)
                if reminder is None:
                    logger.error(f"Reminder with ID {reminder_id} not found. Due date can't be updated.")
                    raise RuntimeError(f"Reminder with ID {reminder_id} not found. Due date can't be updated.")

                covered_start, _ = get_covered_period(reminder.next_due_date, reminder.day)
                next_year, next_month = shift_month(covered_start.year, covered_start.month, 1)
                # Day is re-derived from `day`, so 31 -> Feb 28 -> Mar 31
                reminder.next_due_date = get_due_date_for_covered_month(next_year, next_month, reminder.day)
                return reminder.next_due_date


    def matching_transaction_exists(self, name:str, category_id:int, period_start:date, period_end:date) -> bool:
        """Check if a transaction matching a reminder exists in the given period.

            Arguments
            ---------
                `name` : (str) - Reminder name. Compared case-insensitively.
                `category_id` : (int) - Category the transaction has to belong to.
                `period_start` : (date) - First day of the period.
                `period_end` : (date) - Last day of the period.
            Returns
            -------
                `bool` - True if a matching transaction exists, False otherwise.
        """

        normalized_name = name.strip().casefold()
        with self.session_factory() as session:
            with session.begin():
                transaction_names = session.query(Transaction.name).join(Category).filter(and_(
                    Transaction.category_id == category_id,
                    Category.account_id == self.account_id,
                    Transaction.date.between(period_start, period_end)
                )).all()

        return any(
            (transaction_name or "").strip().casefold() == normalized_name for (transaction_name,) in transaction_names
        )
