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
                # Emergency filler if no tasks assigned.
                # Split into chunks of max 2.5 hours to satisfy instructions.
                remaining = target_daily_hours
                chunk_size = 2.0
                
                filler_activities = [
                    "General review and maintenance of systems",
                    "Code optimization and technical debt reduction",
                    "Documentation updates and process review",
                    "Security patches and dependency updates"
                ]
                
                idx = 0
                while remaining > 0:
                    h = min(remaining, chunk_size)
                    current_tasks.append({
                        "task_name": filler_activities[idx % len(filler_activities)],
                        "client_project": settings.DEFAULT_CLIENT_PROJECT,
                        "hours": h
                    })
                    remaining -= h
                    idx += 1
                    
                total_h = target_daily_hours

            # Strategy:
            # 1. If total < target: Add filler tasks to reach target (don't scale up coding tasks widely)
            # 2. If total > target: Scale down proportionally (safe, as it reduces hours)
            
            if total_h < target_daily_hours:
                deficit = target_daily_hours - total_h
                chunk_size = 2.0 # Max size for fillers
                
                if settings.LANGUAGE == 'es':
                    filler_activities = [
                        "Sincronización diaria con el equipo y actualización de estado",
                        "Revisión de documentación y notas técnicas",
                        "Optimización de código y reducción de deuda técnica",
                        "Discusión técnica interna y planificación",
                        "Gestión de correos pendientes y comunicación"
                    ]
                else:
                    filler_activities = [
                        "Daily team synchronization and status update",
                        "Documentation review and technical notes",
                        "Codebase optimization and cleanup",
                        "Internal technical discussion",
                        "Pending emails and communication"
                    ]
                idx = 0
                while deficit > 0.01:
                    h = min(deficit, chunk_size)
                    # Don't make tinier tasks than 0.5 if possible, unless it's the last bit
                    if h < 0.5 and deficit > 0.5:
                         h = 0.5 
                    
                    current_tasks.append({
                        "task_name": filler_activities[idx % len(filler_activities)],
                        "client_project": settings.DEFAULT_CLIENT_PROJECT,
                        "hours": round(h, 2)
                    })
                    deficit -= h
                    idx += 1
                
                # Update total
                total_h = sum(float(t['hours']) for t in current_tasks)

            # Final Normalize (Scaling down if needed, or fixing tiny precision errors)
            scale_factor = target_daily_hours / total_h if total_h > 0 else 1
            
            running_sum = 0
            for i, t in enumerate(current_tasks):
                # For last item, take the remainder to be exact
                if i == len(current_tasks) - 1:
                    new_h = target_daily_hours - running_sum
                else:
                    new_h = float(t['hours']) * scale_factor
                    running_sum += new_h
                
                # Sanity check: if new_h > 3.0 (very unlikely if we filled specifically), clamp it?
                # But strict 8h is priority. If we scaled down, it's <= 3. If we filled, it's <= 3.
                t['hours'] = round(new_h, 2)
                
            final_schedule[day] = current_tasks
                
        return final_schedule
