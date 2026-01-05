import requests
import json
import os
from datetime import datetime
from typing import List, Dict
from src.config.settings import settings

class DeepSeekProcessor:
    def __init__(self):
        # We can support multiple backends. Defaulting to Ollama if no API key or explicitly requested.
        self.use_ollama = settings.USE_OLLAMA
        self.ollama_url = "http://localhost:11434/api/chat"
        self.ollama_model = settings.OLLAMA_MODEL

        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = "https://api.deepseek.com/v1/chat/completions" 
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Ensure logs dir exists
        os.makedirs(settings.LOGS_DIR, exist_ok=True)

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
        
        lang_instruction = "Spanish (Español)" if settings.LANGUAGE == 'es' else "English"
        
        prompt = f"""
        You are an expert software consultant.
        
        Context:
        - Report for {target_days} days.
        - Target: {hours_per_day} hours/day.
        - Total: {total_hours_needed} hours.
        - **OUTPUT LANGUAGE**: {lang_instruction}
        
        Rules:
        1. **Segment & Expand**: Break down commits to cover {total_hours_needed} hours. A single commit MUST be split into multiple small subtasks (e.g. Planning, Implementation, Testing, Documentation).
        2. **Tone**: Professional corporate in {lang_instruction}.
        3. **Estimate**: Hours per task. 
        4. **Granularity Constraint**: **NO task can be longer than 3 hours**. Each task must be between 0.5 and 3 hours. You must generate many tasks to fill the quota.
        5. **Output JSON**: List of objects with keys: "task_name", "hours". Return ONLY valid JSON.
        6. **LANGUAGE**: All "task_name" values MUST be in {lang_instruction}. Do NOT use English unless the technical term requires it.
        
        Commits:
        {commit_text}
        
        Output format:
        [
            {{"task_name": "Implemented authentication", "hours": 2.5}},
            ...
        ]
        """
        
        # Log input
        self._log_to_file("INPUT", prompt)
        
        try:
            if self.use_ollama:
                response = self._call_ollama(prompt)
            else:
                response = self._call_deepseek(prompt)
            
            return response
                
        except Exception as e:
            print(f"Error calling LLM: {e}")
            self._log_to_file("ERROR", str(e))
            return self._fallback(commits)

    def _log_to_file(self, type_str: str, content: str):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(settings.LOGS_DIR, f"interaction_{timestamp}_{type_str}.txt")
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"Warning: Could not write log: {e}")

    def _call_ollama(self, prompt: str) -> List[Dict]:
        print(f"Sending request to Ollama ({self.ollama_model})...")
        payload = {
            "model": self.ollama_model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that generates JSON."},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "format": "json" # Ollama support for strict JSON
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            data = response.json()
            content = data['message']['content']
            return self._parse_response(content)
        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to Ollama at http://localhost:11434. Is it running?")
            raise

    def _call_deepseek(self, prompt: str) -> List[Dict]:
        print("Sending request to DeepSeek...")
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that generates JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 4000
        }
        response = requests.post("https://api.deepseek.com/chat/completions", headers=self.headers, json=payload)
        response.raise_for_status()
        data = response.json()
        content = data['choices'][0]['message']['content']
        return self._parse_response(content)

    def _parse_response(self, content: str) -> List[Dict]:
        print(f"DEBUG: Raw LLM Response: {content}")
        self._log_to_file("OUTPUT", content)
        
        # Clean markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        try:
            tasks = json.loads(content.strip())
        except json.JSONDecodeError:
            print("Error: LLM did not return valid JSON.")
            return []

        # Handle nested keys like {"tasks": [...]} which Llama loves to do
        if isinstance(tasks, dict):
            if 'tasks' in tasks and isinstance(tasks['tasks'], list):
                tasks = tasks['tasks']
            else:
                # If it's a single dict task, wrap in list
                tasks = [tasks]
        
        if not isinstance(tasks, list):
            print("Error: LLM JSON is not a list.")
            return []

        final_tasks = []
        for task in tasks:
            # Handle string case if LLM returned ["Task 1", "Task 2"]
            if isinstance(task, str):
                task = {"task_name": task, "hours": 2.0} # Default assumption
            
            # Inject client
            if isinstance(task, dict):
                task['client_project'] = settings.DEFAULT_CLIENT_PROJECT
                final_tasks.append(task)
            
        return final_tasks

    def _fallback(self, commits: List[Dict]) -> List[Dict]:
        fallback_tasks = []
        for c in commits:
            fallback_tasks.append({
                "task_name": c['message'].split('\n')[0],
                "client_project": settings.DEFAULT_CLIENT_PROJECT,
                "hours": 1.0
            })
        return fallback_tasks

