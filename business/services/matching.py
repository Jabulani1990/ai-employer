from django.db.models import Count, F, Q, FloatField
from django.db.models.functions import Cast
from accounts.models import User

def find_best_candidate(task):
    """
    Finds the best candidate (employee or freelancer) for a given task based on:
    1. Skill match (40%)
    2. Experience level (30%)
    3. Availability (fewer assigned tasks) (20%)
    4. Budget fit (10%)
    5. Rating (bonus factor)
    """
    required_skills = set(task.required_skills.split(", "))  # Convert to set

    # Get candidates (employees + freelancers) with at least one matching skill
    potential_candidates = User.objects.filter(
        Q(account_type='freelancer') | Q(account_type='employee'),
        skills__name__in=required_skills
    ).distinct().annotate(
        skill_match=Cast(
            Count('skills', filter=Q(skills__name__in=required_skills)), FloatField()
        ) / len(required_skills),  # Normalize by required skill count
        task_count=Count('assigned_tasks'),
        experience_score=Cast(F('experience_level'), FloatField()) / 10,  # Normalize (max 10 years)
        budget_match=1 - (Cast(F('hourly_rate'), FloatField()) / task.budget),  # Normalize budget match
        rating_score=Cast(F('rating'), FloatField()) / 5  # Normalize rating (out of 5)
    )

    # Compute final weighted score
    ranked_candidates = potential_candidates.annotate(
        total_score=(
            (F('skill_match') * 0.4) +
            (F('experience_score') * 0.3) +
            ((1 - F('task_count')) * 0.2) +  # Lower task count is better
            (F('budget_match') * 0.1) +
            (F('rating_score') * 0.1)  # Bonus factor
        )
    ).order_by('-total_score')  # Rank by highest score

    return ranked_candidates.first()  # Return best candidate
