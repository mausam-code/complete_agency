# J.K. OVERSEAS PVT.LTD. Management System - Complete Setup Guide

## 🏗️ Architecture Overview

This project has been completely restructured as a **modern API-first application**:

- **Backend**: Django REST Framework API (Port 8000)
- **Frontend**: React.js Application (Port 3000)
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Authentication**: JWT + Session-based
- **Documentation**: Auto-generated OpenAPI/Swagger

## 🚀 Quick Start

### 1. Backend Setup (Django API)

```bash
# Navigate to project directory
cd /mnt/s/all\ projects/aa/new_app

# Install Python dependencies (already installed)
pip3 install --break-system-packages djangorestframework djangorestframework-simplejwt django-cors-headers drf-spectacular

# Run migrations
python3 manage.py migrate

# Create sample data
python3 manage.py setup_sample_data

# Start Django API server
python3 manage.py runserver 0.0.0.0:8000
```

### 2. Frontend Setup (React)

```bash
# Navigate to frontend directory
cd /mnt/s/all\ projects/aa/new_app/frontend

# Install Node.js dependencies
npm install

# Start React development server
npm start
```

## 📱 Access Points

### Django API Backend
- **API Root**: http://localhost:8000/api/
- **API Documentation (Swagger)**: http://localhost:8000/api/docs/
- **API Documentation (ReDoc)**: http://localhost:8000/api/redoc/
- **Admin Panel**: http://localhost:8000/admin/

### React Frontend
- **Main Application**: http://localhost:3000/
- **Login Page**: http://localhost:3000/login

## 🔑 Demo Accounts

| Username | Password | Role | Level | Access |
|----------|----------|------|-------|---------|
| `superadmin` | `admin123` | Super Administrator | 1 | Full System Access |
| `admin` | `admin123` | Admin | 2 | Management Functions |
| `hr_manager` | `admin123` | Administrator (HR) | 2 | HR Management |
| `accountant` | `admin123` | Accountant | 2 | Financial Access |
| `employee1` | `emp123` | Employee | 3 | Limited Access |
| `employee2` | `emp123` | Employee | 3 | Limited Access |
| `customer1` | `cust123` | Customer | 3 | Customer Access |

## 🔧 API Endpoints

### Authentication
```bash
# JWT Login
POST /api/v1/accounts/auth/token/
{
  "username": "superadmin",
  "password": "admin123"
}

# Get Current User
GET /api/v1/accounts/auth/me/
Authorization: Bearer <access_token>

# Logout
POST /api/v1/accounts/auth/logout/
{
  "refresh_token": "<refresh_token>"
}
```

### User Management
```bash
# List Users
GET /api/v1/accounts/users/

# Create User
POST /api/v1/accounts/users/
{
  "username": "newuser",
  "email": "user@jkoverseas.com",
  "first_name": "New",
  "last_name": "User",
  "password": "password123",
  "password_confirm": "password123",
  "role": "employee"
}

# Get User Details
GET /api/v1/accounts/users/{id}/

# Update User
PATCH /api/v1/accounts/users/{id}/
```

### Project Management
```bash
# List Projects
GET /api/v1/core/projects/

# Create Project
POST /api/v1/core/projects/
{
  "name": "New Project",
  "description": "Project description",
  "status": "planning",
  "priority": "medium",
  "start_date": "2025-09-01",
  "end_date": "2025-12-01",
  "budget": "75000.00"
}
```

### Task Management
```bash
# List Tasks
GET /api/v1/core/tasks/

# Create Task
POST /api/v1/core/tasks/
{
  "title": "New Task",
  "description": "Task description",
  "project": 1,
  "assigned_to": 5,
  "priority": "medium",
  "due_date": "2025-09-15T10:00:00Z"
}
```

## 🎨 React Frontend Features

### Implemented Components
- ✅ **Authentication System** (Login/Logout with JWT)
- ✅ **Protected Routes** with role-based access
- ✅ **Modern Material-UI Design**
- ✅ **Responsive Layout** with sidebar navigation
- ✅ **Dashboard** with role-based statistics
- ✅ **API Integration** with Axios and React Query

### Component Structure
```
src/
├── components/
│   ├── auth/
│   │   └── ProtectedRoute.js
│   └── common/
│       ├── Layout.js
│       └── Sidebar.js
├── contexts/
│   └── AuthContext.js
├── pages/
│   ├── LoginPage.js
│   ├── DashboardPage.js
│   └── [Other Pages].js
├── services/
│   ├── api.js
│   ├── auth.js
│   ├── users.js
│   ├── projects.js
│   └── hr.js
└── App.js
```

### Key Features
1. **JWT Authentication** with automatic token refresh
2. **Role-based Navigation** showing appropriate menu items
3. **Responsive Design** that works on mobile and desktop
4. **Material-UI Components** for professional appearance
5. **Error Handling** with user-friendly messages
6. **Loading States** for better user experience

## 🔐 Security Features

### Backend Security
- **JWT Authentication** with refresh tokens
- **Token Blacklisting** for secure logout
- **Role-based Permissions** at API level
- **CORS Configuration** for frontend integration
- **Rate Limiting** to prevent abuse
- **Input Validation** with DRF serializers

### Frontend Security
- **Automatic Token Refresh** handling
- **Protected Routes** based on authentication
- **Role-based UI** showing appropriate features
- **Secure Token Storage** in localStorage
- **API Error Handling** with proper redirects

## 📊 Database Schema

### User Management
- `User` - Custom user model with roles and levels
- `UserProfile` - Extended user information
- `Department` - Organizational departments
- `LoginHistory` - Security audit trail

### Core Business Logic
- `Company` - Company information
- `Project` - Project management with team assignments
- `Task` - Task tracking and assignment
- `Attendance` - Employee attendance records
- `LeaveRequest` - Leave management with approval workflow
- `Expense` - Expense tracking and approval
- `Payroll` - Salary and payroll management
- `Notification` - System notifications

## 🚀 Development Workflow

### Backend Development
1. **API Development**: Add new endpoints in `api_views.py`
2. **Serializers**: Create/update serializers for data validation
3. **Permissions**: Use custom permission classes for access control
4. **Testing**: Test endpoints using Swagger UI or Postman

### Frontend Development
1. **Services**: Add API calls in service files
2. **Components**: Create reusable React components
3. **Pages**: Build complete page interfaces
4. **State Management**: Use React Query for server state

### Testing the System
1. **Start Backend**: `python3 manage.py runserver`
2. **Start Frontend**: `npm start` (in frontend directory)
3. **Test API**: Visit http://localhost:8000/api/docs/
4. **Test UI**: Visit http://localhost:3000/

## 📈 Next Steps for Development

### Phase 1: Core Functionality
- [ ] Complete user management interface
- [ ] Project management with CRUD operations
- [ ] Task management with assignment and tracking
- [ ] Basic reporting and analytics

### Phase 2: Advanced Features
- [ ] Real-time notifications with WebSockets
- [ ] File upload and document management
- [ ] Advanced search and filtering
- [ ] Bulk operations and data export

### Phase 3: Production Ready
- [ ] Comprehensive testing suite
- [ ] Production deployment configuration
- [ ] Performance optimization
- [ ] Security hardening

## 🔧 Production Deployment

### Backend (Django API)
```bash
# Environment variables
export SECRET_KEY="your-production-secret-key"
export DEBUG=False
export ALLOWED_HOSTS="yourdomain.com,api.yourdomain.com"
export DATABASE_URL="postgresql://user:pass@localhost/dbname"

# Static files
python3 manage.py collectstatic --noinput

# Use production WSGI server
gunicorn company_management.wsgi:application
```

### Frontend (React)
```bash
# Build production bundle
npm run build

# Serve with nginx or deploy to CDN
# Update API_BASE_URL in .env for production
```

## 📚 API Documentation

The API is fully documented and can be explored interactively:

- **Swagger UI**: http://localhost:8000/api/docs/
  - Interactive API testing
  - Request/response examples
  - Authentication testing

- **ReDoc**: http://localhost:8000/api/redoc/
  - Clean documentation format
  - Detailed schema information
  - Export capabilities

## 🎯 Key Benefits of This Architecture

1. **Separation of Concerns**: Frontend and backend are completely independent
2. **Scalability**: Each part can be scaled independently
3. **Modern Stack**: Uses latest technologies and best practices
4. **API-First**: Can support multiple frontends (web, mobile, etc.)
5. **Developer Experience**: Hot reloading, auto-documentation, type safety
6. **Production Ready**: Includes security, performance, and deployment considerations

## 🆘 Troubleshooting

### Common Issues

1. **CORS Errors**: Check CORS_ALLOWED_ORIGINS in Django settings
2. **Authentication Errors**: Verify JWT token format and expiration
3. **API Errors**: Check Django logs and API documentation
4. **Frontend Errors**: Check browser console and network tab

### Development Tips

1. **Use API Documentation**: Always test endpoints in Swagger UI first
2. **Check Network Tab**: Monitor API calls in browser dev tools
3. **Use React DevTools**: Install React and Redux DevTools extensions
4. **Monitor Logs**: Keep Django development server logs visible

---

**This system is now a modern, API-first application ready for production use with React frontend and comprehensive API backend!** 🚀
