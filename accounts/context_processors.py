from accounts.models import Task, EmailDraft, Summary

def sidebar_counts(request):
    if request.user.is_authenticated:
        task_count = Task.objects.filter(user=request.user).exclude(status='done').count()
        draft_count = EmailDraft.objects.filter(user=request.user).count()
        summary_count = Summary.objects.filter(user=request.user).count()
        return {
            'sidebar_task_count': task_count,
            'sidebar_draft_count': draft_count,
            'sidebar_summary_count': summary_count,
        }
    return {
        'sidebar_task_count': 0,
        'sidebar_draft_count': 0,
        'sidebar_summary_count': 0,
    }
