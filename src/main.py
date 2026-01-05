import argparse
from datetime import date
from src.config.settings import settings
from src.core.github_client import LocalGitClient
from src.core.llm_processor import DeepSeekProcessor
from src.core.task_distributor import TaskDistributor
from src.core.excel_manager import ExcelManager
import os

def main():
    parser = argparse.ArgumentParser(description="Auto Report Generator")
    parser.add_argument("--month", type=int, default=date.today().month, help="Month to generate report for (1-12)")
    parser.add_argument("--year", type=int, default=settings.HOLIDAYS_YEAR, help="Year to generate report for")
    parser.add_argument("--dry-run", action="store_true", help="Print tasks without writing to Excel")
    parser.add_argument("--repo", action="append", help="Add repository path (can be used multiple times)")
    
    args = parser.parse_args()
    
    # Repositories
    repos = settings.REPO_LIST
    if args.repo:
        repos.extend(args.repo)
        
    if not repos:
        # Default to current directory if it's a git repo
        if os.path.exists(".git"):
            print("No repos specified in settings or args. Using current directory.")
            repos = [os.getcwd()]
        else:
            print("Error: No repositories specified in settings.REPO_LIST or --repo argument.")
            return

    print(f"--- Starting Auto Report for {args.month}/{args.year} ---")
    print(f"Repositories: {repos}")
    
    # 1. Fetch Commits
    git_client = LocalGitClient()
    # Define date range: 1st to End of Month
    # Note: We fetch commits from the WHOLE month to fill the report.
    start_date = date(args.year, args.month, 1)
    
    # Get last day
    if args.month == 12:
        end_date = date(args.year, 12, 31)
    else:
        # Easy way: date(year, month+1, 1) - 1 day
        next_month = date(args.year, args.month + 1, 1)
        import datetime
        end_date = next_month - datetime.timedelta(days=1)
        
    print(f"Fetching commits from {start_date} to {end_date}...")
    commits = git_client.get_all_commits(repos, start_date, end_date)
    print(f"Found {len(commits)} commits.")
    
    if not commits:
        print("No commits found. Exiting.")
        return

    # 2. Process with LLM
    from src.utils.date_utils import get_business_days_in_month
    
    business_days = get_business_days_in_month(args.year, args.month)
    target_days = len(business_days)
    print(f"Target Business Days: {target_days}")

    print("Processing commits with DeepSeek...")
    llm = DeepSeekProcessor()
    tasks = llm.process_commits(commits, target_days=target_days)
    print(f"Generated {len(tasks)} tasks.")
    
    # 3. Distribute
    print("Distributing tasks...")
    distributor = TaskDistributor()
    schedule = distributor.distribute_tasks(tasks, args.year, args.month)
    
    # 4. Write Excel
    if args.dry_run:
        print("--- Dry Run Schedule ---")
        for day, day_tasks in schedule.items():
            print(f"[{day}]: {len(day_tasks)} tasks, {sum(t['hours'] for t in day_tasks)} hours")
            for t in day_tasks:
                print(f"  - {t['task_name']} ({t['hours']}h)")
    else:
        template_path = os.path.join("src", "static", f"Seguimiento de actividades {args.year}.xlsx")
        # Allow checking if template exists, looking in absolute paths if needed
        if not os.path.exists(template_path):
             # Try absolute path from user request context if relative fails
             template_path = r"C:\Users\esteb\Desktop\REPOS-SYNAPTICA\auto-report\src\static\Seguimiento de actividades 2026.xlsx"
        
        if not os.path.exists(template_path):
            print(f"Template not found at {template_path}")
            return

        print(f"Writing report using template: {template_path}")
        manager = ExcelManager(template_path)
        output = manager.create_report(schedule, args.year, args.month)
        print(f"Report generated: {output}")

if __name__ == "__main__":
    main()
