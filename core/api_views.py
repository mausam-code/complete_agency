from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta

from accounts.models import User
from accounts.permissions import (
    IsSuperAdminOrManager, CanViewFinancialData, CanManageEmployees,
    IsOwnerOrCanManage, ProjectPermission, TaskPermission
)
from .models import (
    Company, Project, Task, Attendance, LeaveRequest,
    Payroll, Expense, Notification
)
from .serializers import (
    CompanySerializer, ProjectListSerializer, ProjectDetailSerializer,
    ProjectCreateUpdateSerializer, TaskListSerializer, TaskDetailSerializer,
    TaskCreateUpdateSerializer, AttendanceSerializer, LeaveRequestSerializer,
    LeaveRequestCreateSerializer, PayrollSerializer, ExpenseSerializer,
    ExpenseCreateUpdateSerializer, NotificationSerializer, NotificationUpdateSerializer
)


# Company Views
class CompanyListCreateAPIView(generics.ListCreateAPIView):
    """List and create companies"""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsSuperAdminOrManager]


class CompanyDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Company detail operations"""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsSuperAdminOrManager]


# Project Views
class ProjectListCreateAPIView(generics.ListCreateAPIView):
    """List and create projects"""
    permission_classes = [IsSuperAdminOrManager]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Project.objects.all()
        
        # Filter based on user level and role
        if user.level == User.LEVEL_1 or user.role == User.ADMIN:
            return queryset
        elif user.level == User.LEVEL_2:
            return queryset.filter(Q(manager=user) | Q(team_members=user))
        else:
            return queryset.filter(team_members=user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProjectCreateUpdateSerializer
        return ProjectListSerializer
    
    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)


class ProjectDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Project detail operations"""
    permission_classes = [ProjectPermission]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Project.objects.all()
        
        if user.level == User.LEVEL_1 or user.role == User.ADMIN:
            return queryset
        elif user.level == User.LEVEL_2:
            return queryset.filter(Q(manager=user) | Q(team_members=user))
        else:
            return queryset.filter(team_members=user)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProjectCreateUpdateSerializer
        return ProjectDetailSerializer


# Task Views
class TaskListCreateAPIView(generics.ListCreateAPIView):
    """List and create tasks"""
    
    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.all()
        
        if user.level <= User.LEVEL_2:
            # Managers can see all tasks or filter by project
            project_id = self.request.query_params.get('project')
            if project_id:
                queryset = queryset.filter(project_id=project_id)
        else:
            # Employees can only see their assigned tasks
            queryset = queryset.filter(assigned_to=user)
        
        # Additional filters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        priority_filter = self.request.query_params.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateUpdateSerializer
        return TaskListSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Task detail operations"""
    permission_classes = [TaskPermission]
    
    def get_queryset(self):
        user = self.request.user
        if user.level <= User.LEVEL_2:
            return Task.objects.all()
        else:
            return Task.objects.filter(assigned_to=user)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TaskCreateUpdateSerializer
        return TaskDetailSerializer


# Attendance Views
class AttendanceListCreateAPIView(generics.ListCreateAPIView):
    """List and create attendance records"""
    serializer_class = AttendanceSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Attendance.objects.all()
        
        if user.level <= User.LEVEL_2:
            # Managers can see all attendance or filter by employee
            employee_id = self.request.query_params.get('employee')
            if employee_id:
                queryset = queryset.filter(employee_id=employee_id)
        else:
            # Employees can only see their own attendance
            queryset = queryset.filter(employee=user)
        
        # Date filter
        date_filter = self.request.query_params.get('date')
        if date_filter:
            queryset = queryset.filter(date=date_filter)
        
        return queryset.order_by('-date')
    
    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)


class AttendanceDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Attendance detail operations"""
    serializer_class = AttendanceSerializer
    permission_classes = [IsOwnerOrCanManage]
    
    def get_queryset(self):
        user = self.request.user
        if user.level <= User.LEVEL_2:
            return Attendance.objects.all()
        else:
            return Attendance.objects.filter(employee=user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_attendance_today(request):
    """Mark attendance for today"""
    today = timezone.now().date()
    attendance, created = Attendance.objects.get_or_create(
        employee=request.user,
        date=today,
        defaults={
            'status': request.data.get('status', 'present'),
            'check_in_time': request.data.get('check_in_time'),
            'check_out_time': request.data.get('check_out_time'),
            'notes': request.data.get('notes', '')
        }
    )
    
    if not created:
        # Update existing attendance
        for field in ['status', 'check_in_time', 'check_out_time', 'notes']:
            if field in request.data:
                setattr(attendance, field, request.data[field])
        attendance.save()
    
    serializer = AttendanceSerializer(attendance)
    return Response(serializer.data)


# Leave Request Views
class LeaveRequestListCreateAPIView(generics.ListCreateAPIView):
    """List and create leave requests"""
    
    def get_queryset(self):
        user = self.request.user
        queryset = LeaveRequest.objects.all()
        
        if user.can_manage_employees():
            # Managers can see all leave requests or filter by employee
            employee_id = self.request.query_params.get('employee')
            if employee_id:
                queryset = queryset.filter(employee_id=employee_id)
        else:
            # Employees can only see their own leave requests
            queryset = queryset.filter(employee=user)
        
        # Status filter
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LeaveRequestCreateSerializer
        return LeaveRequestSerializer
    
    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)


class LeaveRequestDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Leave request detail operations"""
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsOwnerOrCanManage]
    
    def get_queryset(self):
        user = self.request.user
        if user.can_manage_employees():
            return LeaveRequest.objects.all()
        else:
            return LeaveRequest.objects.filter(employee=user)


@api_view(['POST'])
@permission_classes([CanManageEmployees])
def approve_leave_request(request, pk):
    """Approve or reject leave request"""
    try:
        leave_request = LeaveRequest.objects.get(pk=pk)
    except LeaveRequest.DoesNotExist:
        return Response({'error': 'Leave request not found'}, status=status.HTTP_404_NOT_FOUND)
    
    action = request.data.get('action')  # 'approve' or 'reject'
    
    if action == 'approve':
        leave_request.status = 'approved'
        leave_request.approved_by = request.user
        leave_request.approval_date = timezone.now()
        message = 'Leave request approved successfully'
    elif action == 'reject':
        leave_request.status = 'rejected'
        leave_request.approved_by = request.user
        leave_request.approval_date = timezone.now()
        leave_request.rejection_reason = request.data.get('rejection_reason', '')
        message = 'Leave request rejected successfully'
    else:
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
    
    leave_request.save()
    
    # Create notification for employee
    Notification.objects.create(
        recipient=leave_request.employee,
        title=f'Leave Request {action.title()}',
        message=f'Your leave request from {leave_request.start_date} to {leave_request.end_date} has been {action}d.',
        notification_type='info'
    )
    
    serializer = LeaveRequestSerializer(leave_request)
    return Response({
        'message': message,
        'leave_request': serializer.data
    })


# Expense Views
class ExpenseListCreateAPIView(generics.ListCreateAPIView):
    """List and create expenses"""
    
    def get_queryset(self):
        user = self.request.user
        queryset = Expense.objects.all()
        
        if user.can_view_financial_data():
            # Financial users can see all expenses
            pass
        else:
            # Others can only see their own expenses
            queryset = queryset.filter(submitted_by=user)
        
        # Status filter
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ExpenseCreateUpdateSerializer
        return ExpenseSerializer
    
    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)


class ExpenseDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Expense detail operations"""
    permission_classes = [IsOwnerOrCanManage]
    
    def get_queryset(self):
        user = self.request.user
        if user.can_view_financial_data():
            return Expense.objects.all()
        else:
            return Expense.objects.filter(submitted_by=user)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ExpenseCreateUpdateSerializer
        return ExpenseSerializer


@api_view(['POST'])
@permission_classes([CanViewFinancialData])
def approve_expense(request, pk):
    """Approve or reject expense"""
    try:
        expense = Expense.objects.get(pk=pk)
    except Expense.DoesNotExist:
        return Response({'error': 'Expense not found'}, status=status.HTTP_404_NOT_FOUND)
    
    action = request.data.get('action')  # 'approve' or 'reject'
    
    if action == 'approve':
        expense.status = 'approved'
        expense.approved_by = request.user
        expense.approval_date = timezone.now()
        message = 'Expense approved successfully'
    elif action == 'reject':
        expense.status = 'rejected'
        expense.approved_by = request.user
        expense.approval_date = timezone.now()
        message = 'Expense rejected successfully'
    else:
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
    
    expense.save()
    
    # Create notification for employee
    Notification.objects.create(
        recipient=expense.submitted_by,
        title=f'Expense {action.title()}',
        message=f'Your expense "{expense.title}" has been {action}d.',
        notification_type='info'
    )
    
    serializer = ExpenseSerializer(expense)
    return Response({
        'message': message,
        'expense': serializer.data
    })


# Payroll Views
class PayrollListCreateAPIView(generics.ListCreateAPIView):
    """List and create payroll records"""
    serializer_class = PayrollSerializer
    permission_classes = [CanViewFinancialData]
    
    def get_queryset(self):
        queryset = Payroll.objects.all()
        
        # Employee filter
        employee_id = self.request.query_params.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # Date filter
        month_filter = self.request.query_params.get('month')
        if month_filter:
            year, month = month_filter.split('-')
            queryset = queryset.filter(
                pay_period_start__year=year,
                pay_period_start__month=month
            )
        
        return queryset.order_by('-pay_period_start')


class PayrollDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Payroll detail operations"""
    queryset = Payroll.objects.all()
    serializer_class = PayrollSerializer
    permission_classes = [CanViewFinancialData]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_payroll(request):
    """Get current user's payroll records"""
    payroll_records = Payroll.objects.filter(employee=request.user).order_by('-pay_period_start')
    serializer = PayrollSerializer(payroll_records, many=True)
    return Response(serializer.data)


# Notification Views
class NotificationListAPIView(generics.ListAPIView):
    """List user notifications"""
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        queryset = self.request.user.notifications.all()
        
        # Filter by read status
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        return queryset.order_by('-created_at')


class NotificationDetailAPIView(generics.RetrieveUpdateAPIView):
    """Notification detail operations"""
    serializer_class = NotificationUpdateSerializer
    
    def get_queryset(self):
        return self.request.user.notifications.all()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, pk):
    """Mark a specific notification as read"""
    try:
        notification = request.user.notifications.get(pk=pk)
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    updated = request.user.notifications.filter(is_read=False).update(is_read=True)
    return Response({
        'message': f'{updated} notifications marked as read',
        'updated_count': updated
    })
