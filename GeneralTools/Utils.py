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