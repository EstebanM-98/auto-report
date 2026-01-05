import subprocess
import os
from datetime import datetime, date
from typing import List, Dict, Optional

class LocalGitClient:
    def __init__(self):
        pass

    def get_commits(self, repo_path: str, start_date: date, end_date: date, author: str = None) -> List[Dict]:
        """
        Fetches commits from a local git repository between start_date and end_date.
        
        Args:
            repo_path: Absolute path to the local git repository.
            start_date: Start date filter.
            end_date: End date filter.
            author: Optional author string to filter by (e.g. email or name).
            
        Returns:
            List of dictionaries with keys: 'hash', 'author', 'date', 'message'.
        """
        if not os.path.exists(repo_path):
            print(f"Warning: Repo path does not exist: {repo_path}")
            return []

        # Convert dates to git log format (YYYY-MM-DD)
        # We add 1 day to end_date because git --until is inclusive but sometimes behaves exclusively depending on time. 
        # Best to just use inclusive dates carefully or specific timestamps. 
        # Git log --since="2026-01-01 00:00:00" --until="2026-01-31 23:59:59"
        
        since_str = start_date.strftime("%Y-%m-%d 00:00:00")
        until_str = end_date.strftime("%Y-%m-%d 23:59:59")
        
        # Git command to get log with custom format
        # %H: commit hash
        # %an: author name
        # %ad: author date (strict ISO 8601 format)
        # %s: subject
        # %b: body
        # We separate fields by a pipe | or similar unique delimiter.
        delimiter = "|||"
        log_format = f"%H{delimiter}%an{delimiter}%aI{delimiter}%s{delimiter}%b"
        
        cmd = [
            'git', '-C', repo_path, 'log',
            f'--since={since_str}',
            f'--until={until_str}',
            f'--format={log_format}',
            '--no-merges' # explicit tasks usually aren't merges, but context dependent
        ]
        
        if author:
            cmd.append(f'--author={author}')
            
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
        except subprocess.CalledProcessError as e:
            print(f"Error running git log in {repo_path}: {e}")
            return []
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            
            parts = line.split(delimiter)
            if len(parts) >= 4:
                commit_hash = parts[0]
                commit_author = parts[1]
                commit_date_str = parts[2]
                subject = parts[3]
                body = parts[4] if len(parts) > 4 else ""
                
                full_message = f"{subject}\n{body}".strip()
                
                # Parse ISO date
                try:
                    commit_dt = datetime.fromisoformat(commit_date_str)
                except ValueError:
                    commit_dt = datetime.now() # Fallback

                commits.append({
                    'hash': commit_hash,
                    'author': commit_author,
                    'date': commit_dt,
                    'message': full_message,
                    'repo': os.path.basename(repo_path)
                })
                
        return commits

    def get_all_commits(self, repo_paths: List[str], start_date: date, end_date: date, author: str = None) -> List[Dict]:
        all_commits = []
        for path in repo_paths:
            print(f"Fetching commits from {path}...")
            repo_commits = self.get_commits(path, start_date, end_date, author)
            all_commits.extend(repo_commits)
        
        # Sort by date
        all_commits.sort(key=lambda x: x['date'])
        return all_commits
