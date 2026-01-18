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


def convert_to_megabytes(size_in_bytes:int, decimals:int = 2) -> float:
    """Convert size from bytes to megabytes.

        Arguments
        ---------
            `size_in_bytes` : (int) - Size in bytes to convert.
    """
    size_in_megabytes = round(size_in_bytes / (1024 * 1024), decimals)
    return size_in_megabytes