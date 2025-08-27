from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Company, Project, Task, Attendance, LeaveRequest,
    Payroll, Expense, Notification
)

User = get_user_model()


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class ProjectListSerializer(serializers.ModelSerializer):
    """Simplified serializer for project lists"""
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    team_count = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'status', 'status_display', 
            'priority', 'priority_display', 'start_date', 'end_date',
            'budget', 'actual_cost', 'manager', 'manager_name', 
            'client', 'client_name', 'team_count', 'progress_percentage',
            'created_at', 'updated_at'
        ]

    def get_team_count(self, obj):
        return obj.team_members.count()

    def get_progress_percentage(self, obj):
        return obj.get_progress_percentage()


class ProjectDetailSerializer(serializers.ModelSerializer):
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    team_members_details = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    is_over_budget = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'status', 'status_display',
            'priority', 'priority_display', 'start_date', 'end_date',
            'budget', 'actual_cost', 'manager', 'manager_name',
            'client', 'client_name', 'team_members', 'team_members_details',
            'progress_percentage', 'is_over_budget', 'task_count',
            'created_at', 'updated_at'
        ]

    def get_team_members_details(self, obj):
        return [
            {
                'id': member.id,
                'name': member.get_full_name(),
                'role': member.get_role_display(),
                'employee_id': member.employee_id
            }
            for member in obj.team_members.all()
        ]

    def get_progress_percentage(self, obj):
        return obj.get_progress_percentage()

    def get_is_over_budget(self, obj):
        return obj.is_over_budget()

    def get_task_count(self, obj):
        return obj.tasks.count()


class TaskListSerializer(serializers.ModelSerializer):
    """Simplified serializer for task lists"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'status_display',
            'priority', 'priority_display', 'project', 'project_name',
            'assigned_to', 'assigned_to_name', 'created_by', 'created_by_name',
            'due_date', 'completed_date', 'estimated_hours', 'actual_hours',
            'is_overdue', 'created_at', 'updated_at'
        ]

    def get_is_overdue(self, obj):
        return obj.is_overdue()


class TaskDetailSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'status_display',
            'priority', 'priority_display', 'project', 'project_name',
            'assigned_to', 'assigned_to_name', 'created_by', 'created_by_name',
            'due_date', 'completed_date', 'estimated_hours', 'actual_hours',
            'is_overdue', 'progress_percentage', 'created_at', 'updated_at'
        ]

    def get_is_overdue(self, obj):
        return obj.is_overdue()

    def get_progress_percentage(self, obj):
        if obj.estimated_hours > 0:
            return round((obj.actual_hours / obj.estimated_hours) * 100, 2)
        return 0


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    work_hours = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            'id', 'employee', 'employee_name', 'date', 'status', 'status_display',
            'check_in_time', 'check_out_time', 'break_duration', 'notes',
            'work_hours', 'created_at', 'updated_at'
        ]

    def get_work_hours(self, obj):
        return obj.get_work_hours()


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    leave_type_display = serializers.CharField(source='get_leave_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_days = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'employee_name', 'leave_type', 'leave_type_display',
            'start_date', 'end_date', 'reason', 'status', 'status_display',
            'approved_by', 'approved_by_name', 'approval_date', 'rejection_reason',
            'total_days', 'created_at', 'updated_at'
        ]

    def get_total_days(self, obj):
        return obj.get_total_days()


class PayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)

    class Meta:
        model = Payroll
        fields = [
            'id', 'employee', 'employee_name', 'employee_id',
            'pay_period_start', 'pay_period_end', 'basic_salary',
            'allowances', 'overtime_hours', 'overtime_rate',
            'tax_deduction', 'insurance_deduction', 'other_deductions',
            'gross_salary', 'net_salary', 'is_paid', 'payment_date',
            'created_at', 'updated_at'
        ]


class ExpenseSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(source='submitted_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'title', 'description', 'category', 'category_display',
            'amount', 'date', 'receipt', 'submitted_by', 'submitted_by_name',
            'project', 'project_name', 'status', 'status_display',
            'approved_by', 'approved_by_name', 'approval_date',
            'created_at', 'updated_at'
        ]


class NotificationSerializer(serializers.ModelSerializer):
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'notification_type_display',
            'is_read', 'created_at'
        ]


class NotificationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['is_read']


# Create/Update Serializers
class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'name', 'description', 'status', 'priority', 'start_date', 'end_date',
            'budget', 'actual_cost', 'client', 'team_members'
        ]

    def validate(self, attrs):
        if attrs.get('start_date') and attrs.get('end_date'):
            if attrs['start_date'] >= attrs['end_date']:
                raise serializers.ValidationError("End date must be after start date.")
        return attrs


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'status', 'priority', 'project',
            'assigned_to', 'due_date', 'estimated_hours', 'actual_hours'
        ]

    def validate_due_date(self, value):
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError("Due date must be in the future.")
        return value


class LeaveRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']

    def validate(self, attrs):
        from django.utils import timezone
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date:
            if start_date >= end_date:
                raise serializers.ValidationError("End date must be after start date.")
            if start_date < timezone.now().date():
                raise serializers.ValidationError("Start date cannot be in the past.")
        
        return attrs


class ExpenseCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            'title', 'description', 'category', 'amount', 'date', 'receipt', 'project'
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_date(self, value):
        from django.utils import timezone
        if value > timezone.now().date():
            raise serializers.ValidationError("Expense date cannot be in the future.")
        return value
