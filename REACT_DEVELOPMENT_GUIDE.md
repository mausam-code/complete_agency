# React Frontend Development Guide
## J.K. OVERSEAS PVT.LTD. Management System

## 🏗️ Architecture Overview

This React frontend is built with modern best practices and provides a complete user interface for the company management system.

### Tech Stack
- **React 18** - Modern React with hooks
- **Material-UI (MUI)** - Professional UI components
- **React Router** - Client-side routing
- **React Query** - Server state management
- **Axios** - HTTP client for API calls
- **JWT Authentication** - Secure token-based auth

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Django API server running on port 8000

### Setup Commands
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## 📁 Project Structure

```
frontend/
├── public/
│   └── index.html              # HTML template
├── src/
│   ├── components/             # Reusable components
│   │   ├── auth/
│   │   │   └── ProtectedRoute.js
│   │   ├── common/
│   │   │   ├── Layout.js       # Main layout wrapper
│   │   │   └── Sidebar.js      # Navigation sidebar
│   │   ├── users/
│   │   │   ├── UserList.js     # User management table
│   │   │   └── UserForm.js     # User create/edit form
│   │   └── projects/
│   │       └── ProjectList.js  # Project cards view
│   ├── contexts/
│   │   └── AuthContext.js      # Authentication state
│   ├── pages/
│   │   ├── LoginPage.js        # Login interface
│   │   ├── DashboardPage.js    # Role-based dashboard
│   │   ├── UsersPage.js        # User management page
│   │   └── ProjectsPage.js     # Project management page
│   ├── services/
│   │   ├── api.js              # Axios configuration
│   │   ├── auth.js             # Authentication API
│   │   ├── users.js            # User management API
│   │   ├── projects.js         # Project management API
│   │   └── hr.js               # HR functions API
│   ├── App.js                  # Main app component
│   └── index.js                # React entry point
├── package.json                # Dependencies and scripts
└── .env                        # Environment variables
```

## 🔐 Authentication System

### JWT Token Management
```javascript
// Automatic token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Attempt token refresh
      const refreshToken = localStorage.getItem('refresh_token');
      const response = await axios.post('/api/v1/accounts/auth/token/refresh/', {
        refresh: refreshToken,
      });
      // Retry original request with new token
      return api(originalRequest);
    }
  }
);
```

### Protected Routes
```javascript
<ProtectedRoute requiredLevel={2}>
  <ManagementOnlyComponent />
</ProtectedRoute>
```

### Role-Based Access
```javascript
const { user, hasPermission, canManageUsers } = useAuth();

// Check user level (1=Super Admin, 2=Management, 3=Staff)
if (hasPermission(2)) {
  // Show management features
}

// Check specific permissions
if (canManageUsers()) {
  // Show user management
}
```

## 🎨 UI Components

### Material-UI Theme
```javascript
const theme = createTheme({
  palette: {
    primary: { main: '#667eea' },
    secondary: { main: '#764ba2' },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
        },
      },
    },
  },
});
```

### Responsive Layout
- **Desktop**: Sidebar navigation with main content area
- **Mobile**: Collapsible drawer with overlay
- **Tablet**: Adaptive layout with touch-friendly controls

### Component Examples

#### User Management Table
```javascript
<Table>
  <TableHead>
    <TableRow>
      <TableCell>User</TableCell>
      <TableCell>Role</TableCell>
      <TableCell>Department</TableCell>
      <TableCell>Actions</TableCell>
    </TableRow>
  </TableHead>
  <TableBody>
    {users.map((user) => (
      <TableRow key={user.id}>
        <TableCell>
          <Box display="flex" alignItems="center">
            <Avatar>{user.first_name[0]}</Avatar>
            <Box ml={2}>
              <Typography variant="subtitle2">
                {user.full_name}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {user.email}
              </Typography>
            </Box>
          </Box>
        </TableCell>
        {/* ... other cells */}
      </TableRow>
    ))}
  </TableBody>
</Table>
```

#### Project Cards
```javascript
<Grid container spacing={3}>
  {projects.map((project) => (
    <Grid item xs={12} md={6} lg={4} key={project.id}>
      <Card>
        <CardContent>
          <Typography variant="h6">{project.name}</Typography>
          <LinearProgress 
            value={project.progress_percentage} 
            variant="determinate" 
          />
          <Chip 
            label={project.status_display} 
            color={getStatusColor(project.status)} 
          />
        </CardContent>
      </Card>
    </Grid>
  ))}
</Grid>
```

## 🔄 State Management

### React Query for Server State
```javascript
// Fetch data with caching and background updates
const { data: users, isLoading, error } = useQuery({
  queryKey: ['users', searchTerm],
  queryFn: () => userService.searchUsers({ search: searchTerm }),
});

// Mutations for data updates
const createUserMutation = useMutation({
  mutationFn: userService.createUser,
  onSuccess: () => {
    queryClient.invalidateQueries(['users']);
  },
});
```

### Context for Global State
```javascript
// Authentication context
const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  
  const login = async (username, password) => {
    const result = await authService.login(username, password);
    setUser(result.user);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
```

## 🌐 API Integration

### Service Layer Pattern
```javascript
// users.js
export const userService = {
  async getUsers(params = {}) {
    const response = await api.get('/accounts/users/', { params });
    return response.data;
  },

  async createUser(userData) {
    const response = await api.post('/accounts/users/', userData);
    return response.data;
  },

  async updateUser(id, userData) {
    const response = await api.patch(`/accounts/users/${id}/`, userData);
    return response.data;
  },
};
```

### Error Handling
```javascript
// Global error handling in API interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 403) {
      // Handle permission errors
      toast.error('You don\'t have permission for this action');
    }
    return Promise.reject(error);
  }
);

// Component-level error handling
const { data, error, isLoading } = useQuery({
  queryKey: ['users'],
  queryFn: userService.getUsers,
  onError: (error) => {
    console.error('Failed to load users:', error);
  },
});

if (error) {
  return <Alert severity="error">Failed to load data</Alert>;
}
```

## 📱 Responsive Design

### Breakpoints
- **xs**: 0px - 599px (Mobile)
- **sm**: 600px - 959px (Tablet)
- **md**: 960px - 1279px (Desktop)
- **lg**: 1280px - 1919px (Large Desktop)
- **xl**: 1920px+ (Extra Large)

### Mobile-First Approach
```javascript
// Responsive grid
<Grid container spacing={3}>
  <Grid item xs={12} sm={6} md={4} lg={3}>
    <Card>...</Card>
  </Grid>
</Grid>

// Conditional rendering for mobile
const isMobile = useMediaQuery(theme.breakpoints.down('md'));

{isMobile ? (
  <MobileComponent />
) : (
  <DesktopComponent />
)}
```

## 🎯 Features Implemented

### ✅ Core Features
- **Authentication System** with JWT tokens
- **Role-based Access Control** (3 levels)
- **Responsive Layout** with sidebar navigation
- **User Management** (CRUD operations)
- **Project Management** (List view with cards)
- **Dashboard** with role-specific statistics
- **Error Handling** and loading states
- **Form Validation** with real-time feedback

### ✅ UI/UX Features
- **Material Design** components
- **Dark/Light theme** support
- **Loading animations** and skeletons
- **Toast notifications** for user feedback
- **Confirmation dialogs** for destructive actions
- **Search and filtering** capabilities
- **Pagination** for large datasets

## 🔧 Development Workflow

### Component Development
1. **Create component** in appropriate directory
2. **Add to parent** page or component
3. **Implement API integration** with React Query
4. **Add error handling** and loading states
5. **Test responsive behavior**
6. **Add accessibility features**

### API Integration Steps
1. **Add service function** in appropriate service file
2. **Use React Query** for data fetching
3. **Handle loading and error states**
4. **Implement optimistic updates** where appropriate
5. **Add proper TypeScript types** (if using TypeScript)

### Testing Strategy
```bash
# Unit tests
npm test

# E2E tests (if implemented)
npm run test:e2e

# Build verification
npm run build
```

## 🚀 Production Deployment

### Build Process
```bash
# Create production build
npm run build

# Serve with static server
npx serve -s build

# Or deploy to CDN/hosting service
```

### Environment Configuration
```bash
# .env.production
REACT_APP_API_BASE_URL=https://api.yourdomain.com/api/v1
REACT_APP_COMPANY_NAME=J.K. OVERSEAS PVT.LTD.
```

### Performance Optimization
- **Code splitting** with React.lazy()
- **Image optimization** and lazy loading
- **Bundle analysis** with webpack-bundle-analyzer
- **Caching strategies** for API responses
- **Service worker** for offline functionality

## 🔍 Debugging Tips

### Development Tools
- **React DevTools** - Component inspection
- **Redux DevTools** - State debugging (if using Redux)
- **Network tab** - API call monitoring
- **Console logs** - Error tracking

### Common Issues
1. **CORS errors** - Check Django CORS settings
2. **Authentication failures** - Verify token format
3. **Component not updating** - Check React Query cache
4. **Styling issues** - Verify Material-UI theme

## 📈 Future Enhancements

### Phase 1 (Next Sprint)
- [ ] Complete all CRUD forms
- [ ] Add data tables with sorting/filtering
- [ ] Implement file upload functionality
- [ ] Add real-time notifications

### Phase 2 (Future)
- [ ] Progressive Web App (PWA) features
- [ ] Offline functionality
- [ ] Advanced charts and analytics
- [ ] Mobile app with React Native

### Phase 3 (Advanced)
- [ ] WebSocket integration for real-time updates
- [ ] Advanced search with Elasticsearch
- [ ] Multi-language support (i18n)
- [ ] Advanced reporting and exports

## 🆘 Troubleshooting

### Common Development Issues

#### 1. API Connection Issues
```bash
# Check if Django server is running
curl http://localhost:8000/api/

# Verify CORS settings in Django
# Check browser network tab for failed requests
```

#### 2. Authentication Problems
```javascript
// Check token in localStorage
console.log(localStorage.getItem('access_token'));

// Verify token format
const token = localStorage.getItem('access_token');
console.log(JSON.parse(atob(token.split('.')[1])));
```

#### 3. Component Not Rendering
```javascript
// Check React DevTools for component tree
// Verify props are being passed correctly
// Check for JavaScript errors in console
```

### Performance Issues
```javascript
// Use React.memo for expensive components
const ExpensiveComponent = React.memo(({ data }) => {
  return <ComplexVisualization data={data} />;
});

// Implement virtual scrolling for large lists
import { FixedSizeList as List } from 'react-window';
```

## 📚 Learning Resources

### React & JavaScript
- [React Documentation](https://react.dev/)
- [JavaScript MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [React Query Documentation](https://tanstack.com/query/latest)

### Material-UI
- [MUI Documentation](https://mui.com/)
- [MUI Templates](https://mui.com/store/)
- [Material Design Guidelines](https://material.io/design)

### Best Practices
- [React Best Practices](https://react.dev/learn/thinking-in-react)
- [JavaScript Clean Code](https://github.com/ryanmcdermott/clean-code-javascript)
- [Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

This React frontend provides a solid foundation for the J.K. OVERSEAS PVT.LTD. management system with modern architecture, professional UI, and comprehensive functionality. The codebase is structured for scalability and maintainability, making it easy to add new features and components as the system grows.

**Happy coding! 🚀**
