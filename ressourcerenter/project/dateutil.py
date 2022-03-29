from datetime import date, timedelta
from math import ceil


def date_get_last_day_of_month(dato):
    return month_last_date(dato.year, dato.month)


def quarter_number(dato):
    return ceil(dato.month / 3)


def quarter_first_month(quarter):
    return ((quarter-1) * 3) + 1


def quarter_last_month(quarter):
    return ((quarter-1) * 3) + 3


def quarter_first_date(year, quarter):
    if quarter > 4:
        year += int(quarter/4)
        quarter %= 4
    return date(year, quarter_first_month(quarter), 1)


def quarter_last_date(year, quarter):
    return quarter_first_date(year, quarter+1) - timedelta(days=1)


def month_last_date(year, month):
    month += 1
    if month > 12:
        year += int(month/12)
        month %= 12
    return date(year, month, 1) - timedelta(days=1)
