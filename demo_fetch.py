from src.core.github_client import LocalGitClient
from src.config.settings import settings
from datetime import date

def show_commits():
    client = LocalGitClient()
    repo_path = settings.REPO_LIST[0]
    
    # Let's look at the last 30 days or the specific month intended
    # Assuming the user wants to see commits for the report month (Jan 2026?)
    # But for a demo, let's try to fetch something relevant. 
    # If the repo is new or old, maybe we should just fetch "all" recent commits?
    # Let's try Jan 2025 to Jan 2026 to be safe and catch something?
    # Or just asking git log directly might be safer for a "demo" if dates are uncertain.
    # But let's stick to the tool's interface.
    
    start_date = date(2025, 1, 1) 
    end_date = date(2026, 12, 31)
    
    print(f"Fetching commits for: {repo_path}")
    print(f"Range: {start_date} to {end_date}")
    
    commits = client.get_commits(repo_path, start_date, end_date)
    
    print(f"\nFound {len(commits)} commits. Showing first 5:")
    for c in commits[:5]:
        print(f"[{c['date']}] {c['author']}: {c['message'].splitlines()[0]}")

if __name__ == "__main__":
    show_commits()
