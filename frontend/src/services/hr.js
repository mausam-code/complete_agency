import api from './api';

export const hrService = {
  // Attendance
  async getAttendance(params = {}) {
    const response = await api.get('/core/attendance/', { params });
    return response.data;
  },

  async markAttendanceToday(attendanceData) {
    const response = await api.post('/core/attendance/mark-today/', attendanceData);
    return response.data;
  },

  async updateAttendance(id, attendanceData) {
    const response = await api.patch(`/core/attendance/${id}/`, attendanceData);
    return response.data;
  },

  // Leave Requests
  async getLeaveRequests(params = {}) {
    const response = await api.get('/core/leave-requests/', { params });
    return response.data;
  },

  async createLeaveRequest(leaveData) {
    const response = await api.post('/core/leave-requests/', leaveData);
    return response.data;
  },

  async getLeaveRequest(id) {
    const response = await api.get(`/core/leave-requests/${id}/`);
    return response.data;
  },

  async approveLeaveRequest(id, action, rejectionReason = '') {
    const response = await api.post(`/core/leave-requests/${id}/approve/`, {
      action,
      rejection_reason: rejectionReason,
    });
    return response.data;
  },

  // Expenses
  async getExpenses(params = {}) {
    const response = await api.get('/core/expenses/', { params });
    return response.data;
  },

  async createExpense(expenseData) {
    const formData = new FormData();
    Object.keys(expenseData).forEach(key => {
      if (expenseData[key] !== null && expenseData[key] !== undefined) {
        formData.append(key, expenseData[key]);
      }
    });

    const response = await api.post('/core/expenses/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getExpense(id) {
    const response = await api.get(`/core/expenses/${id}/`);
    return response.data;
  },

  async approveExpense(id, action) {
    const response = await api.post(`/core/expenses/${id}/approve/`, {
      action,
    });
    return response.data;
  },

  // Payroll
  async getPayroll(params = {}) {
    const response = await api.get('/core/payroll/', { params });
    return response.data;
  },

  async getMyPayroll() {
    const response = await api.get('/core/payroll/my/');
    return response.data;
  },

  async createPayroll(payrollData) {
    const response = await api.post('/core/payroll/', payrollData);
    return response.data;
  },

  async updatePayroll(id, payrollData) {
    const response = await api.patch(`/core/payroll/${id}/`, payrollData);
    return response.data;
  },

  // Notifications
  async getNotifications(params = {}) {
    const response = await api.get('/core/notifications/', { params });
    return response.data;
  },

  async markNotificationRead(id) {
    const response = await api.post(`/core/notifications/${id}/mark-read/`);
    return response.data;
  },

  async markAllNotificationsRead() {
    const response = await api.post('/core/notifications/mark-all-read/');
    return response.data;
  },
};
