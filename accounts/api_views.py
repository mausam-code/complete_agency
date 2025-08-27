from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta

from .models import User, UserProfile, Department, LoginHistory
from .serializers import (
    UserSerializer, UserListSerializer, LoginSerializer, ChangePasswordSerializer,
    DepartmentSerializer, LoginHistorySerializer, UserStatsSerializer,
    DashboardStatsSerializer, UserProfileSerializer
)
from .permissions import IsOwnerOrManager, CanManageUsers, IsSuperAdminOrManager


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token view with additional user data"""
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Get user data
            username = request.data.get('username')
            user = User.objects.get(username=username)
            
            # Log the login
            LoginHistory.objects.create(
                user=user,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Add user data to response
            user_serializer = UserListSerializer(user)
            response.data['user'] = user_serializer.data
            
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LoginAPIView(APIView):
    """Session-based login API"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            
            # Log the login
            LoginHistory.objects.create(
                user=user,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Return user data
            user_serializer = UserListSerializer(user)
            return Response({
                'message': 'Login successful',
                'user': user_serializer.data,
                'session_id': request.session.session_key
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutAPIView(APIView):
    """Logout API for both session and JWT"""
    
    def post(self, request):
        try:
            # For JWT logout, blacklist the refresh token if provided
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # For session logout
            logout(request)
            
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Logout failed',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserAPIView(APIView):
    """Get current user information"""
    
    def get(self, request):
        if request.user.is_authenticated:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)


class UserListCreateAPIView(generics.ListCreateAPIView):
    """List users and create new users"""
    serializer_class = UserListSerializer
    permission_classes = [CanManageUsers]
    
    def get_queryset(self):
        user = self.request.user
        if user.level == User.LEVEL_1:
            return User.objects.all()
        elif user.level == User.LEVEL_2:
            return User.objects.filter(level__gt=user.level)
        else:
            return User.objects.filter(id=user.id)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserSerializer
        return UserListSerializer
    
    def perform_create(self, serializer):
        # Ensure user level restrictions
        user = serializer.validated_data
        if (self.request.user.level != User.LEVEL_1 and 
            user.get('level', User.LEVEL_3) <= self.request.user.level):
            raise serializers.ValidationError(
                'You cannot create users with equal or higher privileges.'
            )
        serializer.save()


class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a user"""
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrManager]
    
    def get_queryset(self):
        user = self.request.user
        if user.level == User.LEVEL_1:
            return User.objects.all()
        elif user.level == User.LEVEL_2:
            return User.objects.filter(Q(level__gt=user.level) | Q(id=user.id))
        else:
            return User.objects.filter(id=user.id)


class ChangePasswordAPIView(APIView):
    """Change user password"""
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """User profile management"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsOwnerOrManager]
    
    def get_object(self):
        user_id = self.kwargs.get('user_id', self.request.user.id)
        user = User.objects.get(id=user_id)
        profile, created = UserProfile.objects.get_or_create(user=user)
        return profile


class DepartmentListCreateAPIView(generics.ListCreateAPIView):
    """List and create departments"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsSuperAdminOrManager]


class DepartmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Department detail operations"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsSuperAdminOrManager]


class LoginHistoryAPIView(generics.ListAPIView):
    """View login history"""
    serializer_class = LoginHistorySerializer
    permission_classes = [IsSuperAdminOrManager]
    
    def get_queryset(self):
        queryset = LoginHistory.objects.all()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset.order_by('-login_time')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics based on user role"""
    user = request.user
    stats = {}
    
    if user.role == User.SUPERADMIN:
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'level_1_users': User.objects.filter(level=User.LEVEL_1).count(),
            'level_2_users': User.objects.filter(level=User.LEVEL_2).count(),
            'level_3_users': User.objects.filter(level=User.LEVEL_3).count(),
            'recent_logins': LoginHistory.objects.filter(
                login_time__gte=timezone.now() - timedelta(days=7)
            ).count(),
        }
        
        # Add project and expense stats if core models are available
        try:
            from core.models import Project, Expense, LeaveRequest
            stats.update({
                'total_projects': Project.objects.count(),
                'active_projects': Project.objects.filter(status='in_progress').count(),
                'pending_expenses': Expense.objects.filter(status='pending').count(),
                'pending_leaves': LeaveRequest.objects.filter(status='pending').count(),
            })
        except ImportError:
            pass
            
    elif user.level == User.LEVEL_2:
        subordinates = user.get_subordinates()
        stats = {
            'team_members': subordinates.count(),
            'active_team_members': subordinates.filter(is_active=True).count(),
        }
        
        # Add management-specific stats
        try:
            from core.models import Project, Task, LeaveRequest
            stats.update({
                'my_projects': Project.objects.filter(manager=user).count(),
                'pending_tasks': Task.objects.filter(
                    assigned_to__in=subordinates, 
                    status__in=['todo', 'in_progress']
                ).count(),
                'pending_leaves': LeaveRequest.objects.filter(
                    employee__in=subordinates, 
                    status='pending'
                ).count(),
            })
        except ImportError:
            pass
            
    else:  # Level 3 users
        stats = {
            'profile_completion': 75,  # Calculate based on filled fields
        }
        
        # Add employee-specific stats
        try:
            from core.models import Task, Project, LeaveRequest
            stats.update({
                'my_tasks': Task.objects.filter(assigned_to=user).count(),
                'pending_tasks': Task.objects.filter(
                    assigned_to=user, 
                    status__in=['todo', 'in_progress']
                ).count(),
                'my_projects': Project.objects.filter(team_members=user).count(),
                'my_leaves': LeaveRequest.objects.filter(employee=user).count(),
            })
        except ImportError:
            pass
    
    serializer = DashboardStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsSuperAdminOrManager])
def user_stats(request):
    """Get detailed user statistics"""
    stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'level_1_users': User.objects.filter(level=User.LEVEL_1).count(),
        'level_2_users': User.objects.filter(level=User.LEVEL_2).count(),
        'level_3_users': User.objects.filter(level=User.LEVEL_3).count(),
        'recent_logins': LoginHistory.objects.filter(
            login_time__gte=timezone.now() - timedelta(days=7)
        ).count(),
    }
    
    serializer = UserStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notifications_read(request):
    """Mark notifications as read"""
    notification_ids = request.data.get('notification_ids', [])
    
    if notification_ids:
        # Mark specific notifications as read
        updated = request.user.notifications.filter(
            id__in=notification_ids
        ).update(is_read=True)
    else:
        # Mark all notifications as read
        updated = request.user.notifications.filter(
            is_read=False
        ).update(is_read=True)
    
    return Response({
        'message': f'{updated} notifications marked as read',
        'updated_count': updated
    })


class UserSearchAPIView(generics.ListAPIView):
    """Search users with filters"""
    serializer_class = UserListSerializer
    permission_classes = [CanManageUsers]
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        # Apply user level restrictions
        user = self.request.user
        if user.level != User.LEVEL_1:
            queryset = queryset.filter(level__gte=user.level)
        
        # Apply search filters
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(employee_id__icontains=search)
            )
        
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department__icontains=department)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('level', 'username')
