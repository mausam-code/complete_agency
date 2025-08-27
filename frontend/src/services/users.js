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

  // Get user stats
  async getUserStats() {
    const response = await api.get('/accounts/stats/users/');
    return response.data;
  },

  // Get departments
  async getDepartments() {
    const response = await api.get('/accounts/departments/');
    return response.data;
  },

  // Create department
  async createDepartment(departmentData) {
    const response = await api.post('/accounts/departments/', departmentData);
    return response.data;
  },

  // Update department
  async updateDepartment(id, departmentData) {
    const response = await api.patch(`/accounts/departments/${id}/`, departmentData);
    return response.data;
  },

  // Delete department
  async deleteDepartment(id) {
    await api.delete(`/accounts/departments/${id}/`);
  },

  // Get login history
  async getLoginHistory(params = {}) {
    const response = await api.get('/accounts/login-history/', { params });
    return response.data;
  },
};
