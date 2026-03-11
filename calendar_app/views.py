from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from accounts.models import CalendarEvent

@login_required
def calendar_view(request):
    events_qs = CalendarEvent.objects.filter(user=request.user).order_by('date', 'start_time')
    events = [
        {
            'id': e.id,
            'title': e.title,
            'date': e.date,
            'start_time': e.start_time,
            'end_time': e.end_time,
            'description': e.description,
        }
        for e in events_qs
    ]
    return render(request, "calendar.html", {
        'events_json': json.dumps(events)
    })

@csrf_exempt
@login_required
def create_event(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # If AI mode is requested or only title is provided (no specific date/time)
            if data.get('is_ai_mode') or (not data.get('date') and not data.get('start_time')):
                from ai_engine.event_parser import parse_event
                from accounts.models import UserProfile
                from datetime import date
                
                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                text = data.get('title', '')
                
                event_data = parse_event(text, api_key=profile.ai_api_key, model_name=profile.ai_model)
                
                event = CalendarEvent.objects.create(
                    user=request.user,
                    title=event_data.get('title', text),
                    date=event_data.get('date', date.today().strftime('%Y-%m-%d')),
                    start_time=event_data.get('start_time', '09:00'),
                    end_time=event_data.get('end_time', '10:00'),
                    description=event_data.get('description', '')
                )
            else:
                event = CalendarEvent.objects.create(
                    user=request.user,
                    title=data.get('title', 'New Event'),
                    date=data.get('date'),
                    start_time=data.get('start_time'),
                    end_time=data.get('end_time'),
                    description=data.get('description', '')
                )
            return JsonResponse({'status': 'success', 'id': event.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)

@csrf_exempt
@login_required
def update_event(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            event_id = data.get('id')
            event = CalendarEvent.objects.get(id=event_id, user=request.user)
            
            if 'title' in data: event.title = data['title']
            if 'date' in data: event.date = data['date']
            if 'start_time' in data: event.start_time = data['start_time']
            if 'end_time' in data: event.end_time = data['end_time']
            if 'description' in data: event.description = data['description']
            
            event.save()
            return JsonResponse({'status': 'success'})
        except CalendarEvent.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)

@csrf_exempt
@login_required
def delete_event(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            event_id = data.get('id')
            event = CalendarEvent.objects.get(id=event_id, user=request.user)
            event.delete()
            return JsonResponse({'status': 'success'})
        except CalendarEvent.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)
