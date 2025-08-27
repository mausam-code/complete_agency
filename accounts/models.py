from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

class User(AbstractUser):
    """
    Custom User model with role-based access control
    3 levels of users: Level 1 (Superadmin), Level 2 (Admin/Manager), Level 3 (Employee/Customer)
    """
    
    # User Roles
    SUPERADMIN = 'superadmin'
    ADMIN = 'admin'
    ADMINISTRATOR = 'administrator'
    ACCOUNTANT = 'accountant'
    EMPLOYEE = 'employee'
    CUSTOMER = 'customer'
    
    ROLE_CHOICES = [
        (SUPERADMIN, 'Super Administrator'),
        (ADMIN, 'Admin'),
        (ADMINISTRATOR, 'Administrator'),
        (ACCOUNTANT, 'Accountant'),
        (EMPLOYEE, 'Employee'),
        (CUSTOMER, 'Customer'),
    ]
    
    # User Levels (for hierarchical permissions)
    LEVEL_1 = 1  # Superadmin
    LEVEL_2 = 2  # Admin, Administrator, Accountant
    LEVEL_3 = 3  # Employee, Customer
    
    LEVEL_CHOICES = [
        (LEVEL_1, 'Level 1 - Super Admin'),
        (LEVEL_2, 'Level 2 - Management'),
        (LEVEL_3, 'Level 3 - Staff/Customer'),
    ]
    
    # Additional fields
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=EMPLOYEE)
    level = models.IntegerField(choices=LEVEL_CHOICES, default=LEVEL_3)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active_employee = models.BooleanField(default=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """Override save to automatically set level based on role"""
        if self.role == self.SUPERADMIN:
            self.level = self.LEVEL_1
            self.is_staff = True
            self.is_superuser = True
        elif self.role in [self.ADMIN, self.ADMINISTRATOR, self.ACCOUNTANT]:
            self.level = self.LEVEL_2
            self.is_staff = True
        else:
            self.level = self.LEVEL_3
            self.is_staff = False
            self.is_superuser = False
            
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate user data"""
        if self.role in [self.EMPLOYEE, self.ADMINISTRATOR, self.ACCOUNTANT] and not self.employee_id:
            raise ValidationError("Employee ID is required for employees and staff.")
    
    def get_permissions_level(self):
        """Get user's permission level"""
        return self.level
    
    def can_manage_users(self):
        """Check if user can manage other users"""
        return self.level <= self.LEVEL_2
    
    def can_view_financial_data(self):
        """Check if user can view financial information"""
        return self.role in [self.SUPERADMIN, self.ADMIN, self.ACCOUNTANT]
    
    def can_manage_employees(self):
        """Check if user can manage employees"""
        return self.role in [self.SUPERADMIN, self.ADMIN, self.ADMINISTRATOR]
    
    def get_subordinates(self):
        """Get users that this user can manage"""
        if self.level == self.LEVEL_1:
            return User.objects.all().exclude(id=self.id)
        elif self.level == self.LEVEL_2:
            return User.objects.filter(level__gt=self.level)
        else:
            return User.objects.none()
    
    def get_unread_notifications_count(self):
        """Get count of unread notifications"""
        return self.notifications.filter(is_read=False).count()
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    class Meta:
        ordering = ['level', 'username']


class Department(models.Model):
    """Department model for organizing employees"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    head = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                           related_name='headed_departments')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Extended profile information for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    skills = models.TextField(blank=True, help_text="Comma-separated list of skills")
    certifications = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class LoginHistory(models.Model):
    """Track user login history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    class Meta:
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"
