import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from accounts.models import Task

def serialize_tasks(tasks_queryset):
    """Helper to convert Task model instances to dictionaries for JSON"""
    return [
        {
            'id': str(t.task_id),
            'title': t.title,
            'status': t.status,
            'priority': t.priority,
            'description': t.description,
            'due_date': t.due_date,
            'due_time': t.due_time,
        }
        for t in tasks_queryset
    ]

@login_required
def tasks(request):
    try:
        user_tasks_qs = Task.objects.filter(user=request.user).order_by('created_at')
        user_tasks = serialize_tasks(user_tasks_qs)
    except Exception:
        user_tasks = []
    
    context = {
        'tasks': user_tasks,
        'tasks_json': json.dumps(user_tasks)
    }
    return render(request, "tasks.html", context)

@csrf_exempt
@login_required
def update_task_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = str(data.get('id', ''))
            new_status = data.get('status')
            
            task = Task.objects.filter(user=request.user, task_id=task_id).first()
            if task:
                task.status = new_status
                task.save()
                return JsonResponse({'success': True})
            return JsonResponse({'error': 'Task not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
@login_required
def delete_task(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = str(data.get('id', ''))
            
            deleted, _ = Task.objects.filter(user=request.user, task_id=task_id).delete()
            if deleted > 0:
                return JsonResponse({'success': True})
            return JsonResponse({'error': 'Task not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
@login_required
def clear_tasks_by_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            status = data.get('status')
            
            Task.objects.filter(user=request.user, status=status).delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
@login_required
def create_task(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_task = Task.objects.create(
                user=request.user,
                title=data.get('title', 'New Task'),
                status=data.get('status', 'todo'),
                priority='medium',
                description='',
                due_date='',
                due_time=''
            )
            
            task_dict = {
                'id': str(new_task.task_id),
                'title': new_task.title,
                'status': new_task.status,
                'priority': new_task.priority,
                'description': new_task.description,
                'due_date': new_task.due_date,
                'due_time': new_task.due_time
            }
            return JsonResponse({'success': True, 'task': task_dict})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
@login_required
def update_task_title(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = str(data.get('id', ''))
            new_title = data.get('title', '').strip()
            if not new_title:
                return JsonResponse({'error': 'Empty title'}, status=400)
                
            task = Task.objects.filter(user=request.user, task_id=task_id).first()
            if task:
                task.title = new_title
                task.save()
                return JsonResponse({'success': True})
            return JsonResponse({'error': 'Task not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)
