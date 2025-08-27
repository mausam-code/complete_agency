from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Department, UserProfile
from core.models import Company, Project, Task
from datetime import date, timedelta
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for the company management system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))

        # Create company
        company, created = Company.objects.get_or_create(
            name="J.K. OVERSEAS PVT.LTD.",
            defaults={
                'registration_number': 'JKO001',
                'address': '123 Business Street, Commercial District, Mumbai 400001',
                'phone': '+91-22-1234-5678',
                'email': 'info@jkoverseas.com',
                'website': 'https://jkoverseas.com',
                'established_date': date(2015, 1, 1),
            }
        )

        # Create departments
        departments = [
            {'name': 'IT Department', 'description': 'Information Technology'},
            {'name': 'HR Department', 'description': 'Human Resources'},
            {'name': 'Finance Department', 'description': 'Finance and Accounting'},
            {'name': 'Marketing Department', 'description': 'Marketing and Sales'},
        ]

        for dept_data in departments:
            Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'description': dept_data['description']}
            )

        # Create users with different roles
        users_data = [
            {
                'username': 'superadmin',
                'email': 'superadmin@jkoverseas.com',
                'first_name': 'Super',
                'last_name': 'Admin',
                'role': User.SUPERADMIN,
                'password': 'admin123',
                'department': 'IT Department',
                'employee_id': 'SA001',
            },
            {
                'username': 'admin',
                'email': 'admin@jkoverseas.com',
                'first_name': 'John',
                'last_name': 'Admin',
                'role': User.ADMIN,
                'password': 'admin123',
                'department': 'IT Department',
                'employee_id': 'AD001',
            },
            {
                'username': 'hr_manager',
                'email': 'hr@jkoverseas.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'role': User.ADMINISTRATOR,
                'password': 'admin123',
                'department': 'HR Department',
                'employee_id': 'HR001',
            },
            {
                'username': 'accountant',
                'email': 'finance@jkoverseas.com',
                'first_name': 'Mike',
                'last_name': 'Wilson',
                'role': User.ACCOUNTANT,
                'password': 'admin123',
                'department': 'Finance Department',
                'employee_id': 'FN001',
            },
            {
                'username': 'employee1',
                'email': 'emp1@jkoverseas.com',
                'first_name': 'Alice',
                'last_name': 'Smith',
                'role': User.EMPLOYEE,
                'password': 'emp123',
                'department': 'IT Department',
                'employee_id': 'EMP001',
            },
            {
                'username': 'employee2',
                'email': 'emp2@jkoverseas.com',
                'first_name': 'Bob',
                'last_name': 'Brown',
                'role': User.EMPLOYEE,
                'password': 'emp123',
                'department': 'Marketing Department',
                'employee_id': 'EMP002',
            },
            {
                'username': 'customer1',
                'email': 'customer1@example.com',
                'first_name': 'David',
                'last_name': 'Customer',
                'role': User.CUSTOMER,
                'password': 'cust123',
            },
        ]

        created_users = {}
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'role': user_data['role'],
                    'department': user_data.get('department'),
                    'employee_id': user_data.get('employee_id'),
                    'hire_date': date.today() - timedelta(days=365),
                    'salary': 50000 if user_data['role'] == User.EMPLOYEE else 75000,
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                
                # Create user profile
                UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'bio': f'This is {user.first_name} {user.last_name}\'s profile.',
                        'skills': 'Python, Django, JavaScript' if user.role == User.EMPLOYEE else 'Management, Leadership',
                    }
                )
                
            created_users[user_data['username']] = user

        # Create sample projects
        if 'admin' in created_users and 'customer1' in created_users:
            project, created = Project.objects.get_or_create(
                name="Website Redesign Project",
                defaults={
                    'description': 'Complete redesign of the company website with modern UI/UX',
                    'status': 'in_progress',
                    'priority': 'high',
                    'start_date': date.today() - timedelta(days=30),
                    'end_date': date.today() + timedelta(days=60),
                    'budget': 50000.00,
                    'actual_cost': 15000.00,
                    'manager': created_users['admin'],
                    'client': created_users['customer1'],
                }
            )
            
            if created:
                # Add team members
                if 'employee1' in created_users:
                    project.team_members.add(created_users['employee1'])
                if 'employee2' in created_users:
                    project.team_members.add(created_users['employee2'])

                # Create sample tasks
                tasks_data = [
                    {
                        'title': 'Design Homepage Mockup',
                        'description': 'Create wireframes and mockups for the new homepage',
                        'status': 'completed',
                        'priority': 'high',
                        'assigned_to': created_users['employee2'],
                        'estimated_hours': 16,
                        'actual_hours': 14,
                    },
                    {
                        'title': 'Implement User Authentication',
                        'description': 'Develop secure user login and registration system',
                        'status': 'in_progress',
                        'priority': 'high',
                        'assigned_to': created_users['employee1'],
                        'estimated_hours': 24,
                        'actual_hours': 12,
                    },
                    {
                        'title': 'Database Migration',
                        'description': 'Migrate existing data to new database structure',
                        'status': 'todo',
                        'priority': 'medium',
                        'assigned_to': created_users['employee1'],
                        'estimated_hours': 8,
                        'actual_hours': 0,
                    },
                ]

                for task_data in tasks_data:
                    Task.objects.get_or_create(
                        title=task_data['title'],
                        project=project,
                        defaults={
                            'description': task_data['description'],
                            'status': task_data['status'],
                            'priority': task_data['priority'],
                            'assigned_to': task_data['assigned_to'],
                            'created_by': created_users['admin'],
                            'due_date': timezone.now() + timedelta(days=14),
                            'estimated_hours': task_data['estimated_hours'],
                            'actual_hours': task_data['actual_hours'],
                            'completed_date': timezone.now() - timedelta(days=5) if task_data['status'] == 'completed' else None,
                        }
                    )

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write(self.style.WARNING('Login credentials:'))
        self.stdout.write('Superadmin: superadmin / admin123')
        self.stdout.write('Admin: admin / admin123')
        self.stdout.write('HR Manager: hr_manager / admin123')
        self.stdout.write('Accountant: accountant / admin123')
        self.stdout.write('Employee: employee1 / emp123')
        self.stdout.write('Employee: employee2 / emp123')
        self.stdout.write('Customer: customer1 / cust123')
