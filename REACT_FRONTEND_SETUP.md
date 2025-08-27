# React Frontend Setup Guide

## 🚀 Quick Start

### 1. Create React App
```bash
# In a separate directory (e.g., frontend/)
npx create-react-app jk-overseas-frontend
cd jk-overseas-frontend

# Install additional dependencies
npm install axios react-router-dom @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material @mui/x-data-grid date-fns
npm install react-query @tanstack/react-query
```

### 2. Environment Configuration
Create `.env` file in React app root:
```env
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_API_DOCS_URL=http://localhost:8000/api/docs
```

### 3. API Service Setup
Create `src/services/api.js`:
```javascript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_BASE_URL}/accounts/auth/token/refresh/`, {
          refresh: refreshToken,
        });
        
        const { access } = response.data;
        localStorage.setItem('access_token', access);
        
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

### 4. Authentication Service
Create `src/services/auth.js`:
```javascript
import api from './api';

export const authService = {
  // Login with JWT
  async loginJWT(username, password) {
    const response = await api.post('/accounts/auth/token/', {
      username,
      password,
    });
    
    const { access, refresh, user } = response.data;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('user', JSON.stringify(user));
    
    return { access, refresh, user };
  },

  // Login with session
  async loginSession(username, password) {
    const response = await api.post('/accounts/auth/login/', {
      username,
      password,
    });
    
    const { user, session_id } = response.data;
    localStorage.setItem('user', JSON.stringify(user));
    localStorage.setItem('session_id', session_id);
    
    return { user, session_id };
  },

  // Logout
  async logout() {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      await api.post('/accounts/auth/logout/', {
        refresh_token: refreshToken,
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      localStorage.removeItem('session_id');
    }
  },

  // Get current user
  async getCurrentUser() {
    const response = await api.get('/accounts/auth/me/');
    return response.data;
  },

  // Check if user is authenticated
  isAuthenticated() {
    return !!localStorage.getItem('access_token') || !!localStorage.getItem('session_id');
  },

  // Get user from localStorage
  getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },
};
```

### 5. API Services for Each Module
Create `src/services/users.js`:
```javascript
import api from './api';

export const userService = {
  // Get all users
  async getUsers(params = {}) {
    const response = await api.get('/accounts/users/', { params });
    return response.data;
  },

  // Search users
  async searchUsers(searchParams) {
    const response = await api.get('/accounts/users/search/', { params: searchParams });
    return response.data;
  },

  // Get user by ID
  async getUser(id) {
    const response = await api.get(`/accounts/users/${id}/`);
    return response.data;
  },

  // Create user
  async createUser(userData) {
    const response = await api.post('/accounts/users/', userData);
    return response.data;
  },

  // Update user
  async updateUser(id, userData) {
    const response = await api.patch(`/accounts/users/${id}/`, userData);
    return response.data;
  },

  // Delete user
  async deleteUser(id) {
    await api.delete(`/accounts/users/${id}/`);
  },

  // Get dashboard stats
  async getDashboardStats() {
    const response = await api.get('/accounts/stats/dashboard/');
    return response.data;
  },
};
```

### 6. React Components Structure
```
src/
├── components/
│   ├── common/
│   │   ├── Layout.js
│   │   ├── Sidebar.js
│   │   ├── Header.js
│   │   └── LoadingSpinner.js
│   ├── auth/
│   │   ├── LoginForm.js
│   │   └── ProtectedRoute.js
│   ├── dashboard/
│   │   ├── SuperAdminDashboard.js
│   │   ├── ManagementDashboard.js
│   │   └── EmployeeDashboard.js
│   ├── users/
│   │   ├── UserList.js
│   │   ├── UserForm.js
│   │   └── UserProfile.js
│   └── projects/
│       ├── ProjectList.js
│       ├── ProjectForm.js
│       └── ProjectDetail.js
├── services/
│   ├── api.js
│   ├── auth.js
│   ├── users.js
│   ├── projects.js
│   └── tasks.js
├── hooks/
│   ├── useAuth.js
│   ├── useUsers.js
│   └── useProjects.js
├── contexts/
│   └── AuthContext.js
└── utils/
    ├── constants.js
    └── helpers.js
```

### 7. Authentication Context
Create `src/contexts/AuthContext.js`:
```javascript
import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/auth';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      try {
        if (authService.isAuthenticated()) {
          const userData = await authService.getCurrentUser();
          setUser(userData);
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        // Clear invalid tokens
        await authService.logout();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (username, password, useJWT = true) => {
    try {
      const result = useJWT 
        ? await authService.loginJWT(username, password)
        : await authService.loginSession(username, password);
      
      setUser(result.user);
      return result;
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
  };

  const value = {
    user,
    login,
    logout,
    loading,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
```

### 8. Main App Component
Update `src/App.js`:
```javascript
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import UsersPage from './pages/UsersPage';
import ProjectsPage from './pages/ProjectsPage';
import Layout from './components/common/Layout';

const queryClient = new QueryClient();

const theme = createTheme({
  palette: {
    primary: {
      main: '#667eea',
    },
    secondary: {
      main: '#764ba2',
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AuthProvider>
          <Router>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/" element={
                <ProtectedRoute>
                  <Layout>
                    <Routes>
                      <Route path="/" element={<DashboardPage />} />
                      <Route path="/dashboard" element={<DashboardPage />} />
                      <Route path="/users/*" element={<UsersPage />} />
                      <Route path="/projects/*" element={<ProjectsPage />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              } />
            </Routes>
          </Router>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
```

## 🔗 API Endpoints

### Authentication
- `POST /api/v1/accounts/auth/login/` - Session login
- `POST /api/v1/accounts/auth/token/` - JWT login
- `POST /api/v1/accounts/auth/logout/` - Logout
- `GET /api/v1/accounts/auth/me/` - Current user info

### Users
- `GET /api/v1/accounts/users/` - List users
- `POST /api/v1/accounts/users/` - Create user
- `GET /api/v1/accounts/users/{id}/` - Get user
- `PATCH /api/v1/accounts/users/{id}/` - Update user

### Projects
- `GET /api/v1/core/projects/` - List projects
- `POST /api/v1/core/projects/` - Create project
- `GET /api/v1/core/projects/{id}/` - Get project

### Tasks
- `GET /api/v1/core/tasks/` - List tasks
- `POST /api/v1/core/tasks/` - Create task

## 📚 API Documentation

Once the Django server is running, access:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## 🔧 Development Workflow

1. **Start Django API Server**:
   ```bash
   cd /path/to/django/project
   python3 manage.py runserver
   ```

2. **Start React Development Server**:
   ```bash
   cd /path/to/react/project
   npm start
   ```

3. **Access Applications**:
   - Django Web Interface: http://localhost:8000
   - React Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/api/docs/

## 🚀 Production Deployment

### Django API (Backend)
- Use production WSGI server (Gunicorn, uWSGI)
- Configure proper CORS settings
- Set up proper database (PostgreSQL)
- Configure static/media file serving

### React Frontend
- Build production bundle: `npm run build`
- Serve with Nginx or CDN
- Configure environment variables for production API URL

## 🔐 Security Considerations

1. **JWT vs Session Authentication**:
   - JWT: Better for mobile apps and microservices
   - Session: Better for web apps with server-side rendering

2. **CORS Configuration**:
   - Restrict allowed origins in production
   - Configure proper headers

3. **API Rate Limiting**:
   - Implement rate limiting for API endpoints
   - Use Django REST framework throttling

4. **Input Validation**:
   - Validate all inputs on both frontend and backend
   - Use serializers for data validation

This setup provides a complete separation between frontend and backend, making it easy to scale and maintain both parts independently.
