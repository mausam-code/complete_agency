def notifications_context(request):
    """Add notification count to all templates"""
    if request.user.is_authenticated:
        return {
            'unread_notifications_count': request.user.get_unread_notifications_count()
        }
    return {}
