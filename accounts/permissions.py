from rest_framework import permissions
from .models import User


class IsOwnerOrManager(permissions.BasePermission):
    """
    Permission to only allow owners of an object or managers to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to the owner or managers
        if hasattr(obj, 'user'):  # For profile objects
            return obj.user == request.user or request.user.can_manage_users()
        elif hasattr(obj, 'id'):  # For user objects
            return obj == request.user or request.user.can_manage_users()
        
        return False


class CanManageUsers(permissions.BasePermission):
    """
    Permission for users who can manage other users.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.can_manage_users()


class IsSuperAdminOrManager(permissions.BasePermission):
    """
    Permission for super admin or management level users.
    """
    
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.level <= User.LEVEL_2)


class IsSuperAdmin(permissions.BasePermission):
    """
    Permission for super admin only.
    """
    
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.role == User.SUPERADMIN)


class CanViewFinancialData(permissions.BasePermission):
    """
    Permission for users who can view financial data.
    """
    
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.can_view_financial_data())


class CanManageEmployees(permissions.BasePermission):
    """
    Permission for users who can manage employees.
    """
    
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.can_manage_employees())


class IsOwnerOrCanManage(permissions.BasePermission):
    """
    Permission to allow access to own data or if user can manage others.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if it's the user's own data
        if hasattr(obj, 'employee'):
            return obj.employee == request.user or request.user.can_manage_employees()
        elif hasattr(obj, 'user'):
            return obj.user == request.user or request.user.can_manage_users()
        elif hasattr(obj, 'submitted_by'):
            return (obj.submitted_by == request.user or 
                   request.user.can_view_financial_data())
        
        return False


class ProjectPermission(permissions.BasePermission):
    """
    Custom permission for project access.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.level <= User.LEVEL_2
    
    def has_object_permission(self, request, view, obj):
        # Super admin and admin can access all projects
        if request.user.level == User.LEVEL_1 or request.user.role == User.ADMIN:
            return True
        
        # Project manager can access their projects
        if obj.manager == request.user:
            return True
        
        # Team members can view projects they're assigned to
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.team_members.all()
        
        return False


class TaskPermission(permissions.BasePermission):
    """
    Custom permission for task access.
    """
    
    def has_object_permission(self, request, view, obj):
        # Super admin and admin can access all tasks
        if request.user.level <= User.LEVEL_2:
            return True
        
        # Task assignee can access their tasks
        if obj.assigned_to == request.user:
            return True
        
        # Project manager can access tasks in their projects
        if obj.project.manager == request.user:
            return True
        
        return False
