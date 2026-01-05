import requests
import json
from typing import List, Dict
from src.config.settings import settings

class DeepSeekProcessor:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = "https://api.deepseek.com/v1/chat/completions" # Standard DeepSeek Endpoint
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def process_commits(self, commits: List[Dict], target_days: int) -> List[Dict]:
        """
        Takes a list of commits and returns a list of refined task entries.
        Each task entry: {'task_name': str, 'project': str, 'hours': float}
        """
        if not commits:
            return []

        # Calculate target
        hours_per_day = settings.MAX_HOURS_PER_DAY
        total_hours_needed = target_days * hours_per_day
        
        # Prepare context for the LLM
        commit_text = "\n".join([f"- [{c['date'].strftime('%Y-%m-%d')}] {c['message']} (Repo: {c['repo']})" for c in commits])
        
        prompt = f"""
        You are an expert software consultant creating a monthly activity report.
        I will provide a list of git commits. Your goal is to convert these into professional task descriptions for a timesheet.
        
        Context:
        - We are reporting for a period of {target_days} business days.
        - We MUST report exactly {hours_per_day} hours per day.
        - Total target hours to fill: {total_hours_needed} hours.
        
        Rules:
        1. **Segment & Expand**: You MUST break down the provided commits into enough granular tasks to cover the {total_hours_needed} hours. A single commit might need to be split into 3-4 subtasks (Planning, Implementation, Testing, Refactoring) to fill the time.
        2. **Professional Tone**: Use corporate language (e.g., "fix bug" -> "Refactoring and debugging of module X", "Analysis of Y").
        3. **Estimate**: Assign hours to each task. 
        4. **Output JSON** only. List of objects with keys: "task_name", "hours".
        
        Commits:
        {commit_text}
        
        Output format:
        [
            {{"task_name": "Implemented authentication", "hours": 2.5}},
            ...
        ]
        """

        payload = {
            "model": "deepseek-chat", # or deepseek-coder, assuming chat for general instruction following
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that generates JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3, # Low temp for deterministic output
            "max_tokens": 4000
        }

        try:
            # Using requests directly
            print("Sending request to DeepSeek...")
            response = requests.post("https://api.deepseek.com/chat/completions", headers=self.headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            # Sanitizing JSON output in case of markdown blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            tasks = json.loads(content.strip())
            
            # Inject Client/Project from settings
            for task in tasks:
                task['client_project'] = settings.DEFAULT_CLIENT_PROJECT
                
            return tasks
            
        except Exception as e:
            print(f"Error calling DeepSeek: {e}")
            # Fallback: Just return raw commits as tasks
            fallback_tasks = []
            for c in commits:
                fallback_tasks.append({
                    "task_name": c['message'].split('\n')[0],
                    "client_project": settings.DEFAULT_CLIENT_PROJECT,
                    "hours": 1.0
                })
            return fallback_tasks

