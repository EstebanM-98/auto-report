from datetime import date
from typing import List, Dict, Any
from src.utils.date_utils import get_business_days_in_month
from src.config.settings import settings
import random

class TaskDistributor:
    def __init__(self):
        pass

    def distribute_tasks(self, tasks: List[Dict[str, Any]], year: int, month: int) -> Dict[date, List[Dict]]:
        """
        Distributes tasks across valid business days in the month.
        Ensures strict 8-hour filling per day.
        """
        business_days = get_business_days_in_month(year, month)
        if not business_days:
            print("No business days found for this month!")
            return {}

        # Initialize schedule
        schedule = {day: {'tasks': [], 'hours': 0.0} for day in business_days}
        
        target_daily_hours = settings.MAX_HOURS_PER_DAY # Should be 8
        
        # 1. Round Robin / Greedy Distribution
        # We try to fill days until they reach target.
        
        # Sort days? Or just iterate.
        day_idx = 0
        num_days = len(business_days)
        
        for task in tasks:
            task_hours = float(task.get('hours', 1.0))
            
            # Find a day that has space
            assigned = False
            # Try start from current index to spread out
            for _ in range(num_days):
                current_day = business_days[day_idx]
                current_load = schedule[current_day]['hours']
                
                # Check if adding this task exceeds target significantly? 
                # Relaxed check: We will normalize later, so just pile them up roughly even?
                # Better: 'Least Loaded' strategy again.
                
                day_idx = (day_idx + 1) % num_days
            
            # Use strict Least Loaded strategy to distribute evenly
            least_loaded_day = min(business_days, key=lambda d: schedule[d]['hours'])
            schedule[least_loaded_day]['tasks'].append(task)
            schedule[least_loaded_day]['hours'] += task_hours
            
        # 2. Strict Normalization (scaling)
        # For each day, scale hours to sum exactly to target_daily_hours
        
        final_schedule = {}
        for day in business_days:
            day_data = schedule[day]
            current_tasks = day_data['tasks']
            total_h = sum(float(t['hours']) for t in current_tasks)
            
            if not current_tasks:
                # Emergency filler if no tasks assigned (e.g. very few commits)
                # This ensures we report 8 hours even if empty.
                current_tasks.append({
                    "task_name": "General review and maintenance of systems",
                    "client_project": settings.DEFAULT_CLIENT_PROJECT,
                    "hours": target_daily_hours
                })
                total_h = target_daily_hours

            # Calculate scale factor
            if total_h > 0:
                scale_factor = target_daily_hours / total_h
                
                # Apply scale
                running_sum = 0
                for i, t in enumerate(current_tasks):
                    # For last item, take the remainder to be exact
                    if i == len(current_tasks) - 1:
                        new_h = target_daily_hours - running_sum
                    else:
                        new_h = round(float(t['hours']) * scale_factor, 2)
                        running_sum += new_h
                    
                    t['hours'] = max(0.1, new_h) # Avoid 0 or negative
                    
                # Store
                final_schedule[day] = current_tasks
                
        return final_schedule
