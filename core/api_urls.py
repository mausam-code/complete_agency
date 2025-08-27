from django.urls import path
from . import api_views

app_name = 'core_api'

urlpatterns = [
    # Company
    path('companies/', api_views.CompanyListCreateAPIView.as_view(), name='company_list_create'),
    path('companies/<int:pk>/', api_views.CompanyDetailAPIView.as_view(), name='company_detail'),
    
    # Projects
    path('projects/', api_views.ProjectListCreateAPIView.as_view(), name='project_list_create'),
    path('projects/<int:pk>/', api_views.ProjectDetailAPIView.as_view(), name='project_detail'),
    
    # Tasks
    path('tasks/', api_views.TaskListCreateAPIView.as_view(), name='task_list_create'),
    path('tasks/<int:pk>/', api_views.TaskDetailAPIView.as_view(), name='task_detail'),
    
    # Attendance
    path('attendance/', api_views.AttendanceListCreateAPIView.as_view(), name='attendance_list_create'),
    path('attendance/<int:pk>/', api_views.AttendanceDetailAPIView.as_view(), name='attendance_detail'),
    path('attendance/mark-today/', api_views.mark_attendance_today, name='mark_attendance_today'),
    
    # Leave Requests
    path('leave-requests/', api_views.LeaveRequestListCreateAPIView.as_view(), name='leave_request_list_create'),
    path('leave-requests/<int:pk>/', api_views.LeaveRequestDetailAPIView.as_view(), name='leave_request_detail'),
    path('leave-requests/<int:pk>/approve/', api_views.approve_leave_request, name='approve_leave_request'),
    
    # Expenses
    path('expenses/', api_views.ExpenseListCreateAPIView.as_view(), name='expense_list_create'),
    path('expenses/<int:pk>/', api_views.ExpenseDetailAPIView.as_view(), name='expense_detail'),
    path('expenses/<int:pk>/approve/', api_views.approve_expense, name='approve_expense'),
    
    # Payroll
    path('payroll/', api_views.PayrollListCreateAPIView.as_view(), name='payroll_list_create'),
    path('payroll/<int:pk>/', api_views.PayrollDetailAPIView.as_view(), name='payroll_detail'),
    path('payroll/my/', api_views.my_payroll, name='my_payroll'),
    
    # Notifications
    path('notifications/', api_views.NotificationListAPIView.as_view(), name='notification_list'),
    path('notifications/<int:pk>/', api_views.NotificationDetailAPIView.as_view(), name='notification_detail'),
    path('notifications/<int:pk>/mark-read/', api_views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', api_views.mark_all_notifications_read, name='mark_all_notifications_read'),
]
