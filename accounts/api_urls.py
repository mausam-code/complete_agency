from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import api_views

app_name = 'accounts_api'

urlpatterns = [
    # Authentication
    path('auth/login/', api_views.LoginAPIView.as_view(), name='login'),
    path('auth/logout/', api_views.LogoutAPIView.as_view(), name='logout'),
    path('auth/token/', api_views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/change-password/', api_views.ChangePasswordAPIView.as_view(), name='change_password'),
    
    # Current user
    path('auth/me/', api_views.CurrentUserAPIView.as_view(), name='current_user'),
    
    # User management
    path('users/', api_views.UserListCreateAPIView.as_view(), name='user_list_create'),
    path('users/search/', api_views.UserSearchAPIView.as_view(), name='user_search'),
    path('users/<int:pk>/', api_views.UserDetailAPIView.as_view(), name='user_detail'),
    
    # User profiles
    path('profiles/<int:user_id>/', api_views.UserProfileAPIView.as_view(), name='user_profile'),
    path('profiles/me/', api_views.UserProfileAPIView.as_view(), name='my_profile'),
    
    # Departments
    path('departments/', api_views.DepartmentListCreateAPIView.as_view(), name='department_list_create'),
    path('departments/<int:pk>/', api_views.DepartmentDetailAPIView.as_view(), name='department_detail'),
    
    # Login history
    path('login-history/', api_views.LoginHistoryAPIView.as_view(), name='login_history'),
    
    # Statistics
    path('stats/dashboard/', api_views.dashboard_stats, name='dashboard_stats'),
    path('stats/users/', api_views.user_stats, name='user_stats'),
    
    # Notifications
    path('notifications/mark-read/', api_views.mark_notifications_read, name='mark_notifications_read'),
]
