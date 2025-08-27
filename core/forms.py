from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q
from accounts.models import User
from .models import (
    Project, Task, Attendance, LeaveRequest, Expense, Payroll
)


class ProjectForm(forms.ModelForm):
    """Form for creating/updating projects"""
    
    class Meta:
        model = Project
        fields = ('name', 'description', 'status', 'priority', 'start_date', 'end_date',
                 'budget', 'client', 'team_members')
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter clients to only show customers
        self.fields['client'].queryset = User.objects.filter(role=User.CUSTOMER)
        
        # Filter team members based on user's level
        if user:
            if user.level == User.LEVEL_1:
                self.fields['team_members'].queryset = User.objects.filter(
                    role__in=[User.EMPLOYEE, User.ADMINISTRATOR, User.ACCOUNTANT]
                )
            else:
                subordinates = user.get_subordinates()
                self.fields['team_members'].queryset = subordinates.filter(
                    role__in=[User.EMPLOYEE, User.ADMINISTRATOR, User.ACCOUNTANT]
                )
        
        # Add CSS classes
        for field_name, field in self.fields.items():
            if field_name == 'team_members':
                field.widget.attrs['class'] = 'form-control select2-multiple'
            else:
                field.widget.attrs['class'] = 'form-control'
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise ValidationError("End date must be after start date.")
        
        return cleaned_data


class TaskForm(forms.ModelForm):
    """Form for creating/updating tasks"""
    
    class Meta:
        model = Task
        fields = ('title', 'description', 'project', 'assigned_to', 'status', 'priority',
                 'due_date', 'estimated_hours')
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        
        # If project is specified, set it and hide the field
        if project:
            self.fields['project'].initial = project
            self.fields['project'].widget = forms.HiddenInput()
        
        # Filter projects based on user's access
        if user:
            if user.level <= User.LEVEL_2:
                self.fields['project'].queryset = Project.objects.all()
                self.fields['assigned_to'].queryset = User.objects.filter(
                    role__in=[User.EMPLOYEE, User.ADMINISTRATOR, User.ACCOUNTANT]
                )
            else:
                self.fields['project'].queryset = Project.objects.filter(
                    Q(manager=user) | Q(team_members=user)
                )
                self.fields['assigned_to'].queryset = User.objects.filter(id=user.id)
        
        # Add CSS classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date <= timezone.now():
            raise ValidationError("Due date must be in the future.")
        return due_date


class AttendanceForm(forms.ModelForm):
    """Form for marking attendance"""
    
    class Meta:
        model = Attendance
        fields = ('status', 'check_in_time', 'check_out_time', 'notes')
        widgets = {
            'check_in_time': forms.TimeInput(attrs={'type': 'time'}),
            'check_out_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_time')
        check_out = cleaned_data.get('check_out_time')
        status = cleaned_data.get('status')
        
        if status == 'present' and not check_in:
            raise ValidationError("Check-in time is required for present status.")
        
        if check_in and check_out and check_out <= check_in:
            raise ValidationError("Check-out time must be after check-in time.")
        
        return cleaned_data


class LeaveRequestForm(forms.ModelForm):
    """Form for creating leave requests"""
    
    class Meta:
        model = LeaveRequest
        fields = ('leave_type', 'start_date', 'end_date', 'reason')
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date >= end_date:
                raise ValidationError("End date must be after start date.")
            
            if start_date < timezone.now().date():
                raise ValidationError("Start date cannot be in the past.")
        
        return cleaned_data


class ExpenseForm(forms.ModelForm):
    """Form for creating expense reports"""
    
    class Meta:
        model = Expense
        fields = ('title', 'description', 'category', 'amount', 'date', 'receipt', 'project')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter projects based on user's access
        if user:
            if user.level <= User.LEVEL_2:
                self.fields['project'].queryset = Project.objects.all()
            else:
                self.fields['project'].queryset = Project.objects.filter(
                    Q(manager=user) | Q(team_members=user)
                )
        
        # Make project optional
        self.fields['project'].required = False
        
        # Add CSS classes
        for field_name, field in self.fields.items():
            if field_name != 'receipt':
                field.widget.attrs['class'] = 'form-control'
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise ValidationError("Amount must be greater than zero.")
        return amount
    
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise ValidationError("Expense date cannot be in the future.")
        return date


class PayrollForm(forms.ModelForm):
    """Form for creating/updating payroll records"""
    
    class Meta:
        model = Payroll
        fields = ('employee', 'pay_period_start', 'pay_period_end', 'basic_salary',
                 'allowances', 'overtime_hours', 'overtime_rate', 'tax_deduction',
                 'insurance_deduction', 'other_deductions')
        widgets = {
            'pay_period_start': forms.DateInput(attrs={'type': 'date'}),
            'pay_period_end': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter employees
        self.fields['employee'].queryset = User.objects.filter(
            role__in=[User.EMPLOYEE, User.ADMINISTRATOR, User.ACCOUNTANT]
        )
        
        # Add CSS classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('pay_period_start')
        end_date = cleaned_data.get('pay_period_end')
        
        if start_date and end_date and start_date >= end_date:
            raise ValidationError("Pay period end date must be after start date.")
        
        return cleaned_data


class TaskUpdateForm(forms.ModelForm):
    """Form for updating task status and progress"""
    
    class Meta:
        model = Task
        fields = ('status', 'actual_hours', 'completed_date')
        widgets = {
            'completed_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Make completed_date required only if status is completed
        self.fields['completed_date'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        completed_date = cleaned_data.get('completed_date')
        
        if status == 'completed' and not completed_date:
            cleaned_data['completed_date'] = timezone.now()
        
        return cleaned_data


class ExpenseApprovalForm(forms.Form):
    """Form for approving/rejecting expenses"""
    action = forms.ChoiceField(
        choices=[('approve', 'Approve'), ('reject', 'Reject')],
        widget=forms.RadioSelect
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Optional notes for the decision"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notes'].widget.attrs['class'] = 'form-control'
