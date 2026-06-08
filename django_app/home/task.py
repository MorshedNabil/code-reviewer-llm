from celery import Celery, shared_task
from home.utils.github import analyze_pr

# app = Celery('django_app')
# app.config_from_object('django.cong:settings', namespace="Celery")

@shared_task
def analyze_pr_task(repo_url, pr_number, github_token=None):
    result = analyze_pr(repo_url, pr_number, github_token)
    return result