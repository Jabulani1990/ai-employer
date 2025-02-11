from django.db.models import Count, F, Q, FloatField
from django.db.models.functions import Cast
from accounts.models import User

def find_best_candidate(task):
    required_skills = set(task.required_skills.split(", "))

    potential_candidates = User.objects.filter(
        Q(account_type='freelancer') | Q(account_type='business'),
        skills__name__in=required_skills
    ).distinct().annotate(
        skill_match=Cast(
            Count('skills', filter=Q(skills__name__in=required_skills)), FloatField()
        ) / len(required_skills),
        task_count=Count('assigned_tasks'),
        experience_score=Cast(F('experience_level'), FloatField()) / 10
    )

    # Compute budget match dynamically
    ranked_candidates = potential_candidates.annotate(
        budget_match=1 - (Cast(F('hourly_rate'), FloatField()) / task.budget),
        total_score=(
            (F('skill_match') * 0.4) +
            (F('experience_score') * 0.3) +
            ((1 - F('task_count')) * 0.2) +
            (F('budget_match') * 0.1) +
            (F('rating_score') / 5 * 0.1)  # Use stored rating
        )
    ).order_by('-total_score')

    return ranked_candidates.first()
