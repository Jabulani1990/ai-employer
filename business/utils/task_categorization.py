import json
from business.models import TaskCategory
import requests
from django.conf import settings


OPENAI_API_KEY = settings.OPENAI_API_KEY

def categorize_task(description):
    """
    Uses OpenAI's GPT API to classify a task into a category.
    Returns a TaskCategory instance.
    """
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        prompt = f"""
        Categorize the following task description into:
        - Industry: (Technology, Finance, Healthcare, Marketing, Other)
        - Job Role: (Data Entry, Design, Writing, Development, Other)
        - Complexity: (Simple, Intermediate, Advanced)

        Task Description: {description}

        Provide the result in JSON format like this:
        {{"industry": "Technology", "job_role": "Development", "complexity": "Intermediate"}}
        """

        data = {
            "model": "gpt-4",
            "messages": [{"role": "system", "content": "You are an AI task categorizer."},
                         {"role": "user", "content": prompt}],
            "temperature": 0.3
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)
        response_data = response.json()

         # ✅ Log response to console
        print("🟢 OpenAI Response:", json.dumps(response_data, indent=4))  # Pretty-print JSON
        
        category_info = eval(response_data["choices"][0]["message"]["content"])  # Convert response to dictionary
        
        # Get or create the appropriate TaskCategory instance
        category, _ = TaskCategory.objects.get_or_create(
            industry=category_info["industry"].lower(),
            job_role=category_info["job_role"].lower(),
            complexity=category_info["complexity"].lower()
        )

        return category

    except Exception as e:
        print(f"Error in categorizing task: {e}")
        return None
