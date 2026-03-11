import json
import uuid
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from accounts.models import UserProfile, DailyGoal, TimeBlock, CurrentFocus

@login_required
def planner_view(request):
    goals = DailyGoal.objects.filter(user=request.user)
    blocks = TimeBlock.objects.filter(user=request.user)
    focus, created = CurrentFocus.objects.get_or_create(
        user=request.user, 
        defaults={'title': 'Focus on your top priority', 'type_label': 'DEEP WORK (1H)'}
    )
    
    context = {
        'goals': goals,
        'blocks': blocks,
        'focus': focus
    }
    return render(request, "planner.html", context)

@csrf_exempt
@login_required
def create_goal(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Find the max order to append at the end
            max_order_query = DailyGoal.objects.filter(user=request.user).order_by('-order').first()
            new_order = (max_order_query.order + 1) if max_order_query else 0
            
            goal = DailyGoal.objects.create(
                user=request.user,
                text=data.get('text', 'New Goal'),
                is_completed=data.get('is_completed', False),
                is_high_priority=data.get('is_high_priority', False),
                order=new_order
            )
            return JsonResponse({'success': True, 'id': goal.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
@login_required
def update_goal(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            goal_id = data.get('id')
            goal = DailyGoal.objects.filter(user=request.user, id=goal_id).first()
            if not goal:
                return JsonResponse({'error': 'Goal not found'}, status=404)
            
            if 'text' in data:
                goal.text = data['text']
            if 'is_completed' in data:
                goal.is_completed = data['is_completed']
            if 'is_high_priority' in data:
                goal.is_high_priority = data['is_high_priority']
            if 'order' in data:
                goal.order = data['order']
                
            goal.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
@login_required
def delete_goal(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            goal_id = data.get('id')
            DailyGoal.objects.filter(user=request.user, id=goal_id).delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
@login_required
def create_timeblock(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            block = TimeBlock.objects.create(
                user=request.user,
                start_time_str=data.get('start_time_str', '12:00'),
                time_period=data.get('time_period', 'PM'),
                title=data.get('title', 'New Block'),
                description=data.get('description', ''),
                color=data.get('color', 'emerald')
            )
            return JsonResponse({'success': True, 'id': block.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
@login_required
def update_focus(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            focus, _ = CurrentFocus.objects.get_or_create(user=request.user)
            if 'title' in data:
                focus.title = data['title']
            if 'type_label' in data:
                focus.type_label = data['type_label']
            if 'is_completed' in data:
                focus.is_completed = data['is_completed']
            focus.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)
