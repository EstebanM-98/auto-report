from src.utils.date_utils import get_holidays, is_business_day
from datetime import date

def check_holidays():
    print("--- Colombian Holidays 2026 ---")
    holidays_2026 = get_holidays(2026)
    for date_obj, name in sorted(holidays_2026.items()):
        print(f"{date_obj}: {name}")
        
    print("\n--- Checking specific sample dates ---")
    # Jan 1 (Holiday)
    d1 = date(2026, 1, 1)
    print(f"{d1} (Thursday): Business Day? {is_business_day(d1)}")
    
    # Jan 2 (Friday)
    d2 = date(2026, 1, 2)
    print(f"{d2} (Friday): Business Day? {is_business_day(d2)}")
    
    # Jan 12 (Monday - Reyes Magos shifted?)
    # In Colombia, Epiphany (Jan 6) is shifted to next Monday -> Jan 12, 2026.
    d3 = date(2026, 1, 12)
    print(f"{d3} (Monday): Business Day? {is_business_day(d3)} ({holidays_2026.get(d3, 'Not a holiday')})")

if __name__ == "__main__":
    check_holidays()
