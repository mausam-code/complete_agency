# J.K. OVERSEAS PVT.LTD. Management API Documentation

## 🌐 Base URL
```
http://localhost:8000/api/v1/
```

## 🔐 Authentication

The API supports both JWT and Session-based authentication:

### JWT Authentication (Recommended for React/Mobile)
```bash
# Login to get tokens
POST /api/v1/accounts/auth/token/
{
  "username": "your_username",
  "password": "your_password"
}

# Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "level": 2
  }
}

# Use in headers
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Session Authentication (For Django Web Interface)
```bash
# Login
POST /api/v1/accounts/auth/login/
{
  "username": "your_username",
  "password": "your_password"
}

# Response
{
  "message": "Login successful",
  "user": {...},
  "session_id": "abc123..."
}
```

## 👥 User Management API

### List Users
```bash
GET /api/v1/accounts/users/
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)

**Response:**
```json
{
  "count": 7,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "superadmin",
      "email": "superadmin@jkoverseas.com",
      "first_name": "Super",
      "last_name": "Admin",
      "full_name": "Super Admin",
      "role": "superadmin",
      "role_display": "Super Administrator",
      "level": 1,
      "level_display": "Level 1 - Super Admin",
      "employee_id": "SA001",
      "department": "IT Department",
      "is_active": true,
      "created_at": "2025-08-27T16:00:00Z"
    }
  ]
}
```

### Create User
```bash
POST /api/v1/accounts/users/
{
  "username": "newuser",
  "email": "newuser@jkoverseas.com",
  "first_name": "New",
  "last_name": "User",
  "password": "securepassword123",
  "password_confirm": "securepassword123",
  "role": "employee",
  "department": "IT Department",
  "employee_id": "EMP003"
}
```

### Get User Details
```bash
GET /api/v1/accounts/users/{id}/
```

### Update User
```bash
PATCH /api/v1/accounts/users/{id}/
{
  "first_name": "Updated",
  "last_name": "Name",
  "department": "HR Department"
}
```

### Search Users
```bash
GET /api/v1/accounts/users/search/?search=john&role=employee&department=IT
```

**Query Parameters:**
- `search`: Search in name, username, email, employee_id
- `role`: Filter by role
- `department`: Filter by department
- `is_active`: Filter by active status (true/false)

## 📊 Dashboard Statistics

### Get Dashboard Stats
```bash
GET /api/v1/accounts/stats/dashboard/
```

**Response varies by user role:**

**Super Admin:**
```json
{
  "total_users": 7,
  "active_users": 7,
  "total_projects": 1,
  "active_projects": 1,
  "pending_expenses": 0,
  "pending_leaves": 0,
  "level_1_users": 1,
  "level_2_users": 3,
  "level_3_users": 3
}
```

**Management:**
```json
{
  "team_members": 3,
  "my_projects": 1,
  "pending_tasks": 2,
  "pending_leaves": 0
}
```

**Employee:**
```json
{
  "my_tasks": 3,
  "pending_tasks": 2,
  "my_projects": 1,
  "my_leaves": 0
}
```

## 🏢 Project Management API

### List Projects
```bash
GET /api/v1/core/projects/
```

**Response:**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "name": "Website Redesign Project",
      "description": "Complete redesign of the company website",
      "status": "in_progress",
      "status_display": "In Progress",
      "priority": "high",
      "priority_display": "High",
      "start_date": "2025-07-28",
      "end_date": "2025-10-26",
      "budget": "50000.00",
      "actual_cost": "15000.00",
      "manager": 2,
      "manager_name": "John Admin",
      "client": 7,
      "client_name": "David Customer",
      "team_count": 2,
      "progress_percentage": 33.33,
      "created_at": "2025-08-27T16:00:00Z"
    }
  ]
}
```

### Create Project
```bash
POST /api/v1/core/projects/
{
  "name": "New Project",
  "description": "Project description",
  "status": "planning",
  "priority": "medium",
  "start_date": "2025-09-01",
  "end_date": "2025-12-01",
  "budget": "75000.00",
  "client": 7,
  "team_members": [5, 6]
}
```

### Get Project Details
```bash
GET /api/v1/core/projects/{id}/
```

**Response:**
```json
{
  "id": 1,
  "name": "Website Redesign Project",
  "description": "Complete redesign of the company website",
  "status": "in_progress",
  "manager_name": "John Admin",
  "client_name": "David Customer",
  "team_members_details": [
    {
      "id": 5,
      "name": "Alice Smith",
      "role": "Employee",
      "employee_id": "EMP001"
    }
  ],
  "progress_percentage": 33.33,
  "is_over_budget": false,
  "task_count": 3
}
```

## ✅ Task Management API

### List Tasks
```bash
GET /api/v1/core/tasks/
```

**Query Parameters:**
- `project`: Filter by project ID
- `status`: Filter by status (todo, in_progress, review, completed)
- `priority`: Filter by priority (low, medium, high, urgent)

### Create Task
```bash
POST /api/v1/core/tasks/
{
  "title": "New Task",
  "description": "Task description",
  "project": 1,
  "assigned_to": 5,
  "priority": "medium",
  "due_date": "2025-09-15T10:00:00Z",
  "estimated_hours": "8.00"
}
```

### Update Task
```bash
PATCH /api/v1/core/tasks/{id}/
{
  "status": "completed",
  "actual_hours": "6.50",
  "completed_date": "2025-08-27T15:30:00Z"
}
```

## 🕐 Attendance API

### List Attendance
```bash
GET /api/v1/core/attendance/
```

**Query Parameters:**
- `employee`: Filter by employee ID
- `date`: Filter by specific date (YYYY-MM-DD)

### Mark Today's Attendance
```bash
POST /api/v1/core/attendance/mark-today/
{
  "status": "present",
  "check_in_time": "09:00:00",
  "check_out_time": "17:30:00",
  "notes": "Regular working day"
}
```

## 📅 Leave Request API

### List Leave Requests
```bash
GET /api/v1/core/leave-requests/
```

**Query Parameters:**
- `employee`: Filter by employee ID
- `status`: Filter by status (pending, approved, rejected)

### Create Leave Request
```bash
POST /api/v1/core/leave-requests/
{
  "leave_type": "vacation",
  "start_date": "2025-09-15",
  "end_date": "2025-09-20",
  "reason": "Family vacation"
}
```

### Approve/Reject Leave Request
```bash
POST /api/v1/core/leave-requests/{id}/approve/
{
  "action": "approve"  // or "reject"
  "rejection_reason": "Insufficient leave balance"  // only for reject
}
```

## 💰 Expense Management API

### List Expenses
```bash
GET /api/v1/core/expenses/
```

### Create Expense
```bash
POST /api/v1/core/expenses/
{
  "title": "Office Supplies",
  "description": "Purchased office supplies for the team",
  "category": "office_supplies",
  "amount": "150.00",
  "date": "2025-08-27",
  "project": 1
}
```

### Approve/Reject Expense
```bash
POST /api/v1/core/expenses/{id}/approve/
{
  "action": "approve"  // or "reject"
}
```

## 💼 Payroll API

### List Payroll Records (Financial Access Required)
```bash
GET /api/v1/core/payroll/
```

### Get My Payroll
```bash
GET /api/v1/core/payroll/my/
```

## 🔔 Notifications API

### List Notifications
```bash
GET /api/v1/core/notifications/
```

**Query Parameters:**
- `is_read`: Filter by read status (true/false)

### Mark Notification as Read
```bash
POST /api/v1/core/notifications/{id}/mark-read/
```

### Mark All Notifications as Read
```bash
POST /api/v1/core/notifications/mark-all-read/
```

## 🏢 Department API

### List Departments
```bash
GET /api/v1/accounts/departments/
```

### Create Department
```bash
POST /api/v1/accounts/departments/
{
  "name": "New Department",
  "description": "Department description",
  "head": 2
}
```

## 🔍 Error Responses

### Authentication Error (401)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Permission Error (403)
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### Validation Error (400)
```json
{
  "field_name": [
    "This field is required."
  ],
  "non_field_errors": [
    "Passwords don't match."
  ]
}
```

### Not Found Error (404)
```json
{
  "detail": "Not found."
}
```

## 📋 User Roles & Permissions

### Level 1 - Super Admin
- Full API access
- Can manage all users and data
- Access to all endpoints

### Level 2 - Management (Admin, Administrator, Accountant)
- Can manage Level 3 users
- Project and task management
- Approval workflows
- Limited financial access (Accountant has full financial access)

### Level 3 - Staff/Customers (Employee, Customer)
- Personal data access only
- Can view assigned projects/tasks
- Can submit requests (leave, expense)
- Limited system visibility

## 🔧 Rate Limiting

API endpoints are rate-limited based on user authentication:
- **Authenticated users**: 1000 requests/hour
- **Anonymous users**: 100 requests/hour

## 📱 Mobile App Integration

The API is designed to work seamlessly with mobile applications:

1. **Use JWT Authentication** for mobile apps
2. **Implement token refresh** logic
3. **Handle offline scenarios** with local storage
4. **Use pagination** for large data sets
5. **Implement push notifications** for real-time updates

## 🌐 CORS Configuration

For frontend applications, CORS is configured to allow:
- `http://localhost:3000` (React development)
- `http://localhost:3001` (Alternative port)
- Production domains (configure in settings)

## 📊 API Monitoring

Monitor API usage with:
- **Response times** for performance optimization
- **Error rates** for reliability tracking
- **Usage patterns** for capacity planning
- **Security events** for threat detection

## 🚀 Interactive API Documentation

Access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

These interfaces allow you to:
- Test API endpoints directly
- View request/response schemas
- Understand authentication requirements
- Download API specifications

---

**Note**: This API follows REST principles and provides comprehensive access to the J.K. OVERSEAS PVT.LTD. management system. All endpoints require proper authentication and respect the hierarchical permission system.
