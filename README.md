# Company Management System

A comprehensive Django-based company management system with hierarchical user roles and permissions.

## Features

### User Management (3-Level Hierarchy)
- **Level 1 - Super Admin**: Full system access, can manage all users and data
- **Level 2 - Management**: Admin, Administrator, Accountant roles with management privileges
- **Level 3 - Staff/Customers**: Employee and Customer roles with limited access

### Core Functionality
- **Project Management**: Create, track, and manage projects with team assignments
- **Task Management**: Assign and track tasks within projects
- **Attendance System**: Employee attendance tracking with check-in/check-out
- **Leave Management**: Leave request submission and approval workflow
- **Expense Tracking**: Submit and approve expense reports
- **Payroll System**: Manage employee payroll and salary information
- **Notification System**: Real-time notifications for important events

### User Roles & Permissions

#### Super Admin (Level 1)
- Complete system access
- User management (create, edit, delete all users)
- System configuration
- All financial data access
- All reports and analytics

#### Admin (Level 2)
- Manage Level 3 users
- Project and task management
- Approve expenses and leave requests
- View team performance data
- Limited financial access

#### Administrator (Level 2)
- HR functions
- Employee management
- Leave request approvals
- Attendance monitoring
- Department management

#### Accountant (Level 2)
- Financial data access
- Payroll management
- Expense approvals
- Financial reporting
- Budget tracking

#### Employee (Level 3)
- Personal task management
- Attendance marking
- Leave request submission
- Expense submission
- View own payroll data

#### Customer (Level 3)
- View assigned projects
- Limited system access
- Communication with project teams

## Installation & Setup

### Prerequisites
- Python 3.8+
- Django 4.2+
- SQLite (default) or PostgreSQL/MySQL

### Quick Start

1. **Clone and Setup**
   ```bash
   cd /path/to/your/project
   python3 -m pip install django pillow
   ```

2. **Database Setup**
   ```bash
   python3 manage.py migrate
   python3 manage.py setup_sample_data
   ```

3. **Run Development Server**
   ```bash
   python3 manage.py runserver
   ```

4. **Access the System**
   - Open http://localhost:8000
   - Use the demo accounts provided below

### Demo Accounts

| Role | Username | Password | Access Level |
|------|----------|----------|--------------|
| Super Admin | superadmin | admin123 | Level 1 - Full Access |
| Admin | admin | admin123 | Level 2 - Management |
| HR Manager | hr_manager | admin123 | Level 2 - HR Functions |
| Accountant | accountant | admin123 | Level 2 - Financial |
| Employee | employee1 | emp123 | Level 3 - Limited |
| Employee | employee2 | emp123 | Level 3 - Limited |
| Customer | customer1 | cust123 | Level 3 - Customer |

## System Architecture

### Models Overview

#### User Management
- **User**: Extended Django user with role-based permissions
- **UserProfile**: Additional user information and preferences
- **Department**: Organizational departments
- **LoginHistory**: Track user login activities

#### Core Business Logic
- **Company**: Company information and settings
- **Project**: Project management with team assignments
- **Task**: Individual tasks within projects
- **Attendance**: Employee attendance tracking
- **LeaveRequest**: Leave request management with approval workflow
- **Payroll**: Employee salary and payroll information
- **Expense**: Expense tracking and approval system
- **Notification**: System-wide notification management

### Permission System

The system uses a 3-level hierarchical permission structure:

```
Level 1 (Super Admin)
├── Can manage all users
├── Full system access
└── All data visibility

Level 2 (Management)
├── Can manage Level 3 users
├── Department/team management
├── Approval workflows
└── Limited financial access

Level 3 (Staff/Customers)
├── Personal data access
├── Task execution
├── Request submissions
└── Limited system visibility
```

### Key Features by Role

#### Dashboard Views
- **Super Admin Dashboard**: System-wide statistics and management tools
- **Management Dashboard**: Team overview and management functions
- **Employee Dashboard**: Personal tasks and information

#### Access Control
- Role-based view restrictions
- Data filtering based on user level
- Hierarchical user management
- Secure permission decorators

## File Structure

```
company_management/
├── accounts/                 # User management app
│   ├── models.py            # User, Profile, Department models
│   ├── views.py             # Authentication and user management
│   ├── forms.py             # User-related forms
│   ├── admin.py             # Admin interface configuration
│   ├── decorators.py        # Permission decorators
│   └── templates/           # User interface templates
├── core/                    # Core business logic app
│   ├── models.py            # Business models (Project, Task, etc.)
│   ├── views.py             # Business logic views
│   ├── forms.py             # Business forms
│   ├── admin.py             # Admin configuration
│   └── templates/           # Business interface templates
├── company_management/      # Project settings
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL routing
│   └── wsgi.py              # WSGI configuration
├── static/                  # Static files (CSS, JS, images)
├── media/                   # User uploaded files
└── manage.py                # Django management script
```

## API Endpoints

### Authentication
- `/accounts/login/` - User login
- `/accounts/logout/` - User logout
- `/accounts/dashboard/` - Role-based dashboard

### User Management
- `/accounts/users/` - User list (management only)
- `/accounts/users/create/` - Create new user
- `/accounts/users/<id>/` - User profile view
- `/accounts/profile/` - Current user profile

### Core Features
- `/core/projects/` - Project management
- `/core/tasks/` - Task management
- `/core/attendance/` - Attendance tracking
- `/core/leaves/` - Leave management
- `/core/expenses/` - Expense tracking
- `/core/payroll/` - Payroll management

## Customization

### Adding New Roles
1. Update `User.ROLE_CHOICES` in `accounts/models.py`
2. Modify permission methods in the User model
3. Update view decorators and templates
4. Add role-specific dashboard logic

### Extending Models
1. Add new fields to existing models
2. Create and run migrations
3. Update forms and admin interfaces
4. Modify templates as needed

### Custom Permissions
1. Create new decorator functions in `accounts/decorators.py`
2. Apply decorators to views
3. Update template conditionals
4. Test permission boundaries

## Security Features

- **Role-based Access Control**: Hierarchical permission system
- **Data Isolation**: Users can only access appropriate data
- **Secure Authentication**: Django's built-in authentication system
- **CSRF Protection**: Cross-site request forgery protection
- **Input Validation**: Form validation and sanitization
- **Login Tracking**: Monitor user access patterns

## Development

### Running Tests
```bash
python3 manage.py test
```

### Creating Migrations
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### Admin Interface
Access the Django admin at `/admin/` with superuser credentials.

### Adding Sample Data
```bash
python3 manage.py setup_sample_data
```

## Production Deployment

### Environment Variables
Set the following environment variables for production:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to False
- `ALLOWED_HOSTS`: Your domain names
- `DATABASE_URL`: Database connection string

### Static Files
```bash
python3 manage.py collectstatic
```

### Database
Configure your production database in `settings.py` and run migrations.

## Support & Documentation

### Key Components
- **Django 4.2**: Web framework
- **Bootstrap 5**: Frontend framework
- **Font Awesome**: Icons
- **SQLite**: Default database (development)

### Troubleshooting
1. **Permission Denied**: Check user role and level
2. **Template Not Found**: Verify template paths
3. **Database Errors**: Run migrations
4. **Static Files**: Run collectstatic

## License

This project is developed for educational and business purposes. Please ensure compliance with your organization's policies and applicable laws.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Note**: This is a comprehensive company management system with role-based access control. Always test thoroughly before deploying to production and ensure proper security measures are in place.
# agency_react_django
