import api from './api';

export const authService = {
  // Login with JWT
  async login(username, password) {
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

  // Logout
  async logout() {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        await api.post('/accounts/auth/logout/', {
          refresh_token: refreshToken,
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  },

  // Get current user
  async getCurrentUser() {
    const response = await api.get('/accounts/auth/me/');
    const user = response.data;
    localStorage.setItem('user', JSON.stringify(user));
    return user;
  },

  // Change password
  async changePassword(oldPassword, newPassword, confirmPassword) {
    const response = await api.post('/accounts/auth/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
      confirm_password: confirmPassword,
    });
    return response.data;
  },

  // Check if user is authenticated
  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  },

  // Get user from localStorage
  getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  // Get user role
  getUserRole() {
    const user = this.getUser();
    return user?.role || null;
  },

  // Get user level
  getUserLevel() {
    const user = this.getUser();
    return user?.level || 3;
  },

  // Check if user has permission
  hasPermission(requiredLevel) {
    const userLevel = this.getUserLevel();
    return userLevel <= requiredLevel;
  },

  // Check if user can manage users
  canManageUsers() {
    const user = this.getUser();
    return user?.level <= 2;
  },

  // Check if user can view financial data
  canViewFinancialData() {
    const user = this.getUser();
    return user?.role === 'superadmin' || user?.role === 'accountant';
  },
};
