from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User, UserProfile, Department


class UserRegistrationForm(UserCreationForm):
    """Form for creating new users"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    department = forms.CharField(max_length=100, required=False)
    employee_id = forms.CharField(max_length=20, required=False)
    phone_number = forms.CharField(max_length=15, required=False)
    hire_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    salary = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2',
                 'role', 'department', 'employee_id', 'phone_number', 'hire_date', 'salary')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email
    
    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        role = self.cleaned_data.get('role')
        
        if role in [User.EMPLOYEE, User.ADMINISTRATOR, User.ACCOUNTANT] and not employee_id:
            raise ValidationError("Employee ID is required for this role.")
        
        if employee_id and User.objects.filter(employee_id=employee_id).exists():
            raise ValidationError("A user with this employee ID already exists.")
        
        return employee_id


class UserUpdateForm(forms.ModelForm):
    """Form for updating user information"""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'address', 
                 'date_of_birth', 'department', 'profile_picture')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    """Form for user profile information"""
    
    class Meta:
        model = UserProfile
        fields = ('bio', 'emergency_contact_name', 'emergency_contact_phone', 
                 'skills', 'certifications')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'skills': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter skills separated by commas'}),
            'certifications': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class AdminUserUpdateForm(forms.ModelForm):
    """Form for administrators to update user information"""
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'is_active',
                 'department', 'employee_id', 'phone_number', 'address', 'date_of_birth',
                 'hire_date', 'salary', 'is_active_employee')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Restrict role choices based on user's level
        if user and user.level != User.LEVEL_1:
            restricted_roles = []
            for role, label in User.ROLE_CHOICES:
                if role == User.SUPERADMIN:
                    continue
                if user.level == User.LEVEL_2 and role in [User.ADMIN, User.ADMINISTRATOR, User.ACCOUNTANT]:
                    continue
                restricted_roles.append((role, label))
            self.fields['role'].choices = restricted_roles
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class DepartmentForm(forms.ModelForm):
    """Form for creating/updating departments"""
    
    class Meta:
        model = Department
        fields = ('name', 'description', 'head')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show users who can be department heads
        self.fields['head'].queryset = User.objects.filter(
            role__in=[User.ADMIN, User.ADMINISTRATOR]
        )
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class UserSearchForm(forms.Form):
    """Form for searching users"""
    search = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, username, email, or employee ID'
        })
    )
    role = forms.ChoiceField(
        choices=[('', 'All Roles')] + User.ROLE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Department'
        })
    )
    is_active = forms.ChoiceField(
        choices=[('', 'All'), ('true', 'Active'), ('false', 'Inactive')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
