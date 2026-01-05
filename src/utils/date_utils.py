import holidays
from datetime import date, timedelta
from typing import List
from src.config.settings import settings

def get_holidays(year: int = settings.HOLIDAYS_YEAR, country: str = settings.COUNTRY_CODE) -> dict:
    """Returns a dict of date -> name for the given year and country."""
    # Note: 'CO' is Colombia. 
    country_holidays = holidays.country_holidays(country, years=year)
    return country_holidays

def is_business_day(check_date: date) -> bool:
    """
    Returns True if the date is a weekday (Mon-Fri) and not a holiday.
    """
    if check_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
        return False
    
    country_holidays = get_holidays(year=check_date.year)
    return check_date not in country_holidays

def get_business_days_in_month(year: int, month: int) -> List[date]:
    """Returns a list of all business days in the specified month."""
    start_date = date(year, month, 1)
    # Get last day of month
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    
    last_day = next_month - timedelta(days=1)
    
    business_days = []
    current_day = start_date
    while current_day <= last_day:
        if is_business_day(current_day):
            business_days.append(current_day)
        current_day += timedelta(days=1)
    
    return business_days
