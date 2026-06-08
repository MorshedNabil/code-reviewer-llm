from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .task import analyze_pr_task
from celery.result import AsyncResult

@api_view(['POST'])
def start_task(request):
    data = request.data
    repo_url = data.get('repo_url')
    pr_number = data.get('pr_number')
    github_token = data.get('github_token')
    
    task = analyze_pr_task.delay(repo_url, pr_number, github_token)

    return Response({
        'task_id': task.id,
        'status': "task started"
    })


@api_view(['GET'])
def task_status_view(request, task_id):
    result = AsyncResult(task_id)

    response = {
        'task_id': task_id,
        'status': result.state,
        'result': result.result
    }

    return Response(response)
