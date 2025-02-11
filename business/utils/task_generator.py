import requests
import json
from django.conf import settings
from django.db.models import DecimalField, ExpressionWrapper


from business.models import Task, TaskCategory

class AutonomousTaskGenerator:
    def __init__(self, ai_employer):
        self.ai_employer = ai_employer
        self.business = ai_employer.business

    def generate_autonomous_tasks(self):
        """
        Dynamically generate tasks using AI reasoning
        """
        # Generate context prompt
        context_prompt = self._construct_context_prompt()
        
        # Use AI to generate tasks
        generated_tasks = self._generate_tasks_with_ai(context_prompt)
        
        # Validate and create tasks
        return self._process_ai_generated_tasks(generated_tasks)

    def _generate_tasks_with_ai(self, context_prompt):
        """
        Use OpenAI HTTP API to generate tasks based on context
        """
        print("Starting AI task generation...")  # Log process start

        try:
            api_url = settings.OPENAI_API_BASE
            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are an expert business strategist generating autonomous tasks."},
                    {"role": "user", "content": context_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }

            print(f"Sending request to OpenAI API at {api_url}...")  # Log API request
            response = requests.post(api_url, headers=headers, json=payload)
            
            response.raise_for_status()
            print("Received response from OpenAI API.")  # Log successful response

            tasks_json = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"Raw AI-generated response: {tasks_json}")  # Log raw AI response

            # Ensure we always return a list, even if parsing fails
            try:
                parsed_tasks = json.loads(tasks_json)
                print(f"Parsed AI tasks: {parsed_tasks}")  # Log parsed tasks
                return parsed_tasks if isinstance(parsed_tasks, list) else []
            except json.JSONDecodeError:
                print(f"Failed to parse tasks JSON: {tasks_json}")  # Log parsing failure
                return []

        except requests.RequestException as req_error:
            print(f"Request error while communicating with OpenAI API: {req_error}")  # Log request failure
            return []
        
        except Exception as e:
            print(f"AI Task Generation Error: {e}")  # Log unexpected error
            return []

        
    def _construct_context_prompt(self):
        """
        Create a comprehensive context prompt for AI task generation
        """
        context = {
            "Business": {
                "Name": self.business.name,
                "Industry": self.business.industry_type,
                "Goals": self.business.business_goals or "Not specified",
                "Daily Operations": self.business.daily_operations or {}
            },
            "AI Employer": {
                "Job Preferences": self.ai_employer.job_preferences or "Not specified",
                "Priority Focus": self.ai_employer.priority_focus or "General business improvement",
                "Past Tasks": self.ai_employer.past_tasks or []
            }
        }

        prompt = f"""
        You are an expert business strategist tasked with generating strategic business tasks.

        Business Context:
        {json.dumps(context, indent=2)}

        Task Generation Guidelines:
        1. Generate 3-5 strategic tasks
        2. Tasks must align with business goals
        3. Consider industry and job preferences
        4. Focus on business growth and operational efficiency
        5. Ensure tasks are specific, measurable, and time-bound

        Provide tasks in strict JSON format:
        [{{
            "title": "Task Title",
            "description": "Detailed task description",
            "required_skills": "Comma-separated skills",
            "estimated_impact": "High/Medium/Low",
            "complexity": "Simple/Intermediate/Advanced"
        }}]
        """

        return prompt

    def _process_ai_generated_tasks(self, ai_tasks):
        """
        Convert AI-generated tasks into database objects
        """
        created_tasks = []
        
        for task_data in ai_tasks:
            try:
                # Find or create appropriate task category
                task_category = self._get_or_create_task_category(task_data)
                
                # Create task
                task = Task.objects.create(
                    ai_employer=self.ai_employer,
                    title=task_data['title'],
                    description=task_data['description'],
                    required_skills=task_data['required_skills'],
                    category=task_category,
                    goal_alignment=self.ai_employer.priority_focus,
                    urgency=self._determine_urgency(task_data),
                    budget=self._calculate_task_budget(task_data)
                )
                
                created_tasks.append(task)
            
            except Exception as e:
                print(f"Task creation error: {e}")
        
        return created_tasks

    def _get_or_create_task_category(self, task_data):
        """
        Dynamically determine and create task category
        """
        skills = task_data['required_skills'].lower().split(',')
        
        # Map skills to job roles and complexity
        job_role_map = {
            'development': 'development',
            'design': 'design',
            'marketing': 'marketing',
            'analysis': 'data_entry',
            'writing': 'writing'
        }
        
        # Determine job role
        job_role = next((role for skill, role in job_role_map.items() if skill in skills), 'other')
        
        # Determine complexity
        complexity = task_data.get('complexity', 'intermediate').lower()
        
        # Find or create category
        category, _ = TaskCategory.objects.get_or_create(
            industry=self.business.industry_type.lower(),
            job_role=job_role,
            complexity=complexity
        )
        
        return category

    def _determine_urgency(self, task_data):
        """
        Determine task urgency based on estimated impact
        """
        impact_map = {
            'high': 3,  # High urgency
            'medium': 2,  # Medium urgency
            'low': 1   # Low urgency
        }
        return impact_map.get(task_data.get('estimated_impact', 'medium').lower(), 2)

    def _calculate_task_budget(self, task_data):
        """
        Calculate task budget dynamically
        """
        from decimal import Decimal

        complexity_budget_multiplier = {
            'simple': Decimal('0.05'),
            'intermediate': Decimal('0.1'),
            'advanced': Decimal('0.15')
        }
        
        complexity = task_data.get('complexity', 'intermediate').lower()
        multiplier = complexity_budget_multiplier.get(complexity, Decimal('0.1'))
        
        # Ensure budget is also Decimal
        budget = Decimal(self.ai_employer.budget)

        return 0.03

        #return budget * multiplier

# Usage function
def generate_autonomous_business_tasks(ai_employer):
    task_generator = AutonomousTaskGenerator(ai_employer)
    return task_generator.generate_autonomous_tasks()