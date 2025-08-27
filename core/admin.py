from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Company, Project, Task, Attendance, LeaveRequest, 
    Payroll, Expense, Notification
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration_number', 'phone', 'email', 'established_date')
    search_fields = ('name', 'registration_number', 'email')
    list_filter = ('established_date',)


class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = ('title', 'assigned_to', 'status', 'priority', 'due_date')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'client', 'status', 'priority', 'start_date', 'end_date', 'budget_status')
    list_filter = ('status', 'priority', 'start_date', 'manager')
    search_fields = ('name', 'description', 'manager__username', 'client__username')
    filter_horizontal = ('team_members',)
    inlines = [TaskInline]
    
    def budget_status(self, obj):
        if obj.is_over_budget():
            return format_html('<span style="color: red;">Over Budget</span>')
        else:
            return format_html('<span style="color: green;">Within Budget</span>')
    budget_status.short_description = 'Budget Status'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'status', 'priority', 'due_date', 'is_overdue')
    list_filter = ('status', 'priority', 'project', 'due_date')
    search_fields = ('title', 'description', 'assigned_to__username', 'project__name')
    date_hierarchy = 'due_date'
    
    def is_overdue(self, obj):
        if obj.is_overdue():
            return format_html('<span style="color: red;">Yes</span>')
        return format_html('<span style="color: green;">No</span>')
    is_overdue.short_description = 'Overdue'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status', 'check_in_time', 'check_out_time', 'work_hours')
    list_filter = ('status', 'date', 'employee__department')
    search_fields = ('employee__username', 'employee__first_name', 'employee__last_name')
    date_hierarchy = 'date'
    
    def work_hours(self, obj):
        hours = obj.get_work_hours()
        return f"{hours:.2f} hours" if hours else "N/A"
    work_hours.short_description = 'Work Hours'


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'total_days', 'status', 'approved_by')
    list_filter = ('leave_type', 'status', 'start_date', 'approved_by')
    search_fields = ('employee__username', 'reason')
    date_hierarchy = 'start_date'
    
    def total_days(self, obj):
        return obj.get_total_days()
    total_days.short_description = 'Total Days'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.role == 'superadmin':
            return qs
        elif request.user.can_manage_employees():
            return qs.filter(employee__level__gt=request.user.level)
        else:
            return qs.filter(employee=request.user)


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('employee', 'pay_period_start', 'pay_period_end', 'gross_salary', 'net_salary', 'is_paid')
    list_filter = ('is_paid', 'pay_period_start', 'employee__department')
    search_fields = ('employee__username', 'employee__first_name', 'employee__last_name')
    date_hierarchy = 'pay_period_start'
    readonly_fields = ('gross_salary', 'net_salary')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.can_view_financial_data():
            return qs
        else:
            return qs.filter(employee=request.user)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'amount', 'submitted_by', 'status', 'date', 'approved_by')
    list_filter = ('category', 'status', 'date', 'approved_by')
    search_fields = ('title', 'description', 'submitted_by__username')
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.can_view_financial_data():
            return qs
        else:
            return qs.filter(submitted_by=request.user)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'recipient__username')
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.role == 'superadmin':
            return qs
        else:
            return qs.filter(recipient=request.user)
