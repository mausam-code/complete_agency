from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from .models import User


def role_required(allowed_roles):
    """
    Decorator to restrict access based on user roles
    Usage: @role_required(['superadmin', 'admin'])
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('dashboard')
        return _wrapped_view
    return decorator


def level_required(min_level):
    """
    Decorator to restrict access based on user level
    Usage: @level_required(2) - allows level 1 and 2 users
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.level <= min_level:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'You do not have sufficient privileges to access this page.')
                return redirect('dashboard')
        return _wrapped_view
    return decorator


def superadmin_required(view_func):
    """
    Decorator to restrict access to superadmin only
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role == User.SUPERADMIN:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Only super administrators can access this page.')
            return redirect('dashboard')
    return _wrapped_view


def management_required(view_func):
    """
    Decorator to restrict access to management level users (Level 1 and 2)
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.level <= User.LEVEL_2:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'This page is restricted to management personnel only.')
            return redirect('dashboard')
    return _wrapped_view


def can_manage_user_required(view_func):
    """
    Decorator to check if user can manage other users
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.can_manage_users():
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'You do not have permission to manage users.')
            return redirect('dashboard')
    return _wrapped_view


def financial_access_required(view_func):
    """
    Decorator to restrict access to financial data
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.can_view_financial_data():
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'You do not have permission to access financial data.')
            return redirect('dashboard')
    return _wrapped_view


def employee_management_required(view_func):
    """
    Decorator to restrict access to employee management functions
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.can_manage_employees():
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'You do not have permission to manage employees.')
            return redirect('dashboard')
    return _wrapped_view


def own_data_or_manager_required(view_func):
    """
    Decorator to allow access to own data or if user is a manager
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Get the user_id from URL parameters if it exists
        user_id = kwargs.get('user_id') or request.GET.get('user_id')
        
        # If no user_id specified, assume it's for the current user
        if not user_id:
            return view_func(request, *args, **kwargs)
        
        # Convert to int if it's a string
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            messages.error(request, 'Invalid user ID.')
            return redirect('dashboard')
        
        # Allow if it's the user's own data or if they can manage users
        if request.user.id == user_id or request.user.can_manage_users():
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'You can only access your own data.')
            return redirect('dashboard')
    return _wrapped_view
