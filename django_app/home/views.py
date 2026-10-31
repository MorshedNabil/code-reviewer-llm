from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .tasks import analyze_pr_task
from celery.result import AsyncResult


# =========== Health check endpoint ===========
@api_view(['GET'])
def health_check(request):
    return Response({"status": "ok"}, status=status.HTTP_200_OK)


# =========== Start task endpoint ===========
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
    task_result = AsyncResult(task_id)

    response = {
        'task_id': task_id,
        'status': task_result.state, # AsyncResult.state returns the current state of the task (e.g., PENDING, STARTED, SUCCESS, FAILURE)
        'result': task_result.result # AsyncResult.result returns the result of the task if it has completed successfully, or None if it hasn't completed yet.
    }

    return Response(response)
