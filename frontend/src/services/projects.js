import api from './api';

export const projectService = {
  // Get all projects
  async getProjects(params = {}) {
    const response = await api.get('/core/projects/', { params });
    return response.data;
  },

  // Get project by ID
  async getProject(id) {
    const response = await api.get(`/core/projects/${id}/`);
    return response.data;
  },

  // Create project
  async createProject(projectData) {
    const response = await api.post('/core/projects/', projectData);
    return response.data;
  },

  // Update project
  async updateProject(id, projectData) {
    const response = await api.patch(`/core/projects/${id}/`, projectData);
    return response.data;
  },

  // Delete project
  async deleteProject(id) {
    await api.delete(`/core/projects/${id}/`);
  },

  // Get tasks
  async getTasks(params = {}) {
    const response = await api.get('/core/tasks/', { params });
    return response.data;
  },

  // Get task by ID
  async getTask(id) {
    const response = await api.get(`/core/tasks/${id}/`);
    return response.data;
  },

  // Create task
  async createTask(taskData) {
    const response = await api.post('/core/tasks/', taskData);
    return response.data;
  },

  // Update task
  async updateTask(id, taskData) {
    const response = await api.patch(`/core/tasks/${id}/`, taskData);
    return response.data;
  },

  // Delete task
  async deleteTask(id) {
    await api.delete(`/core/tasks/${id}/`);
  },
};
