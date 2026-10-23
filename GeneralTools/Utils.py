from datetime import date
from calendar import monthrange



def generate_month_range(year:int, month:int) -> tuple[date, date]:
    """Generate the start and end date for a given month and year.

        Arguments
        ---------
            `year` : (int) - The year for which to generate the date range.
            `month` : (int) - The month for which to generate the date range.
    """
    _, last_day = monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)
    return start_date, end_date


def shift_month(year:int, month:int, offset:int) -> tuple[int, int]:
    """Shift a year and month by a number of months.

        Arguments
        ---------
            `year` : (int) - Year to shift.
            `month` : (int) - Month to shift (1-12).
            `offset` : (int) - Number of months to shift by. Can be negative.
        Returns
        -------
            `tuple[int, int]` - Shifted year and month.
    """

    months_since_zero = year * 12 + (month - 1) + offset
    return months_since_zero // 12, months_since_zero % 12 + 1


def get_due_date_for_covered_month(year:int, month:int, day:int|None) -> date:
    """Get the reminder due date for the month it covers.

        Arguments
        ---------
            `year` : (int) - Year of the covered month.
            `month` : (int) - Covered month.
            `day` : (int|None) - Reminder day. If None, the reminder is due on the 1st day of the next month.
        Returns
        -------
            `date` - Due date. The day is clamped to the last day of the month.
    """

    if day is None:
        next_year, next_month = shift_month(year, month, 1)
        return date(next_year, next_month, 1)

    _, last_day = monthrange(year, month)
    return date(year, month, min(day, last_day))


def get_covered_period(next_due_date:date, day:int|None) -> tuple[date, date]:
    """Get the month range in which a matching transaction for the reminder is searched.

        Arguments
        ---------
            `next_due_date` : (date) - Reminder next due date.
            `day` : (int|None) - Reminder day. If None, the covered month is the month before `next_due_date`.
        Returns
        -------
            `tuple[date, date]` - First and last day of the covered month.
    """

    if day is None:
        year, month = shift_month(next_due_date.year, next_due_date.month, -1)
    else:
        year, month = next_due_date.year, next_due_date.month

    return generate_month_range(year, month)


def convert_to_megabytes(size_in_bytes:int, decimals:int = 2) -> float:
    """Convert size from bytes to megabytes.

        Arguments
        ---------
            `size_in_bytes` : (int) - Size in bytes to convert.
    """
    size_in_megabytes = round(size_in_bytes / (1024 * 1024), decimals)
    return size_in_megabytes