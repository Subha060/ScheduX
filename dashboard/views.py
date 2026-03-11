from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import Task, AIChat, EmailDraft, CalendarEvent, Summary
from django.utils import timezone
from django.utils.timesince import timesince

def get_time_ago(dt):
    if not dt:
        return ""
    return timesince(dt).split(',')[0] + " ago"

@login_required
def home(request):
    user = request.user
    
    # 1. Stats Calculation
    tasks_pending = Task.objects.filter(user=user, status='todo').count()
    tasks_done = Task.objects.filter(user=user, status='done').count()
    total_tasks = tasks_pending + tasks_done
    
    # Simple way to count tasks created today matching current local date
    # (Better to use __date but SQLite handles this correctly if USE_TZ is true/false consistently)
    today = timezone.now().date()
    # Note: timezone.now().date() might not work perfectly with sqlite if dates are stored differently,
    # but using __date on DateTimeField works in Django.
    tasks_added_today = Task.objects.filter(user=user, created_at__date=today).count()
    
    events_count = CalendarEvent.objects.filter(user=user).count()
    
    tasks_completion_pct = int((tasks_done / total_tasks * 100) if total_tasks > 0 else 0)

    # Hardcoded SVGs for UI consistency
    task_icon = '<path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />'
    chat_icon = '<path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />'
    calendar_icon = '<path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />'

    stats = [
        {
            'gradient': 'from-blue-600/5 to-transparent',
            'icon_bg': 'bg-blue-500/10',
            'icon_color': 'text-blue-400',
            'icon': task_icon,
            'label': 'Tasks',
            'value': f'{tasks_pending} Pending',
            'change_color': 'text-blue-400',
            'change': f'↑ {tasks_added_today} added today'
        },
        {
            'gradient': 'from-cyan-600/5 to-transparent',
            'icon_bg': 'bg-cyan-500/10',
            'icon_color': 'text-cyan-400',
            'icon': calendar_icon,
            'label': 'Events',
            'value': f'{events_count}',
            'change_color': 'text-slate-500',
            'change': 'Total calendar events'
        },
        {
            'gradient': 'from-emerald-600/5 to-transparent',
            'icon_bg': 'bg-emerald-500/10',
            'icon_color': 'text-emerald-400',
            'icon': task_icon,
            'label': 'Tasks Done',
            'value': f'{tasks_done} / {total_tasks}',
            'change_color': 'text-emerald-400',
            'change': f'{tasks_completion_pct}% complete'
        }
    ]

    # 2. Recent Activity Compilation
    activities = []
    
    # Tasks
    recent_tasks = Task.objects.filter(user=user).order_by('-created_at')[:3]
    for t in recent_tasks:
        activities.append({
            'icon_bg': 'bg-emerald-500/10' if t.status == 'done' else 'bg-blue-500/10',
            'icon_color': 'text-emerald-400' if t.status == 'done' else 'text-blue-400',
            'icon': task_icon,
            'title': f'Completed "{t.title}"' if t.status == 'done' else f'Added task "{t.title}"',
            'time': get_time_ago(t.created_at),
            'dt': t.created_at,
            'url': '/tasks/'
        })
        
    # AI Chats
    recent_chats = AIChat.objects.filter(user=user).order_by('-created_at')[:3]
    for c in recent_chats:
        activities.append({
            'icon_bg': 'bg-purple-500/10',
            'icon_color': 'text-purple-400',
            'icon': chat_icon,
            'title': f'Chat: "{c.request_text[:30]}..."' if len(c.request_text) > 30 else f'Chat: "{c.request_text}"',
            'time': get_time_ago(c.created_at),
            'dt': c.created_at,
            'url': '/chat/'
        })
        
    # Email Drafts
    email_icon = '<path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />'
    recent_emails = EmailDraft.objects.filter(user=user).order_by('-created_at')[:3]
    for e in recent_emails:
        activities.append({
            'icon_bg': 'bg-amber-500/10',
            'icon_color': 'text-amber-400',
            'icon': email_icon,
            'title': f'Drafted email: "{e.subject}"' if e.subject else 'Drafted a new email',
            'time': get_time_ago(e.created_at),
            'dt': e.created_at,
            'url': '/email/'
        })

    # Calendar Events
    recent_events = CalendarEvent.objects.filter(user=user).order_by('-created_at')[:3]
    for evt in recent_events:
        activities.append({
            'icon_bg': 'bg-cyan-500/10',
            'icon_color': 'text-cyan-400',
            'icon': calendar_icon,
            'title': f'Scheduled "{evt.title}"',
            'time': get_time_ago(evt.created_at),
            'dt': evt.created_at,
            'url': '/calendar/'
        })

    # Sort all activities by datetime descending and take top 5
    activities.sort(key=lambda x: x['dt'], reverse=True)
    activity_feed = activities[:5]

    context = {
        'stats': stats,
        'activity': activity_feed,
    }
    return render(request, "dashboard.html", context)

from accounts.models import AIChat

@login_required
def chat(request):
    recent_chats = AIChat.objects.filter(user=request.user).order_by('-created_at')[:30]
    return render(request, "chat.html", {'recent_chats': recent_chats})

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from accounts.models import UserProfile, EmailDraft

def serialize_drafts(drafts_queryset):
    """Helper to convert EmailDraft model instances to dictionaries for JSON"""
    return [
        {
            'email': {
                'tone': d.tone,
                'subject': d.subject,
                'greeting': d.greeting,
                'body': d.body,
                'closing': d.closing,
                'signature': d.signature
            }
        }
        for d in drafts_queryset
    ]


@login_required
def email_view(request):
    try:
        user_drafts_qs = EmailDraft.objects.filter(user=request.user).order_by('-created_at')
        drafts = serialize_drafts(user_drafts_qs)
    except Exception:
        drafts = []
    
    context = {
        'drafts': drafts,
        'drafts_json': json.dumps(drafts)
    }
    return render(request, "email.html", context)

@login_required
def activity_view(request):
    return render(request, "activity.html")


@login_required
def summaries_view(request):
    import markdown
    summaries_qs = Summary.objects.filter(user=request.user).order_by('-created_at')
    
    # Pre-render markdown for all summaries to make split-pane fast
    summaries = []
    for s in summaries_qs:
        summaries.append({
            'id': s.id,
            'summary_text': s.summary_text,
            'summary_html': markdown.markdown(s.summary_text),
            'original_text': s.original_text,
            'original_preview': s.original_text[:800] + ("..." if len(s.original_text) > 800 else ""),
            'created_at': s.created_at
        })
        
    import json
    from django.core.serializers.json import DjangoJSONEncoder
    summaries_json = json.dumps(summaries, cls=DjangoJSONEncoder)
    
    return render(request, "summaries.html", {
        'summaries': summaries,
        'summaries_json': summaries_json
    })


@csrf_exempt
@login_required
def delete_summary(request, summary_id):
    try:
        summary = Summary.objects.get(id=summary_id, user=request.user)
        summary.delete()
        return JsonResponse({'status': 'success'})
    except Summary.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Summary not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


