import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// ── Dashboard ──
export const dashboardApi = {
  getSummary: () => api.get('/dashboard/summary'),
  getModelTypes: () => api.get('/dashboard/model-types'),
  getGiniOverview: () => api.get('/dashboard/gini-overview'),
  getDevelopmentProgress: () => api.get('/dashboard/development-progress'),
}

// ── Models ──
export const modelsApi = {
  list: (params) => api.get('/models/', { params }),
  get: (id) => api.get(`/models/${id}`),
  create: (data) => api.post('/models/', data),
  update: (id, data) => api.put(`/models/${id}`, data),
  delete: (id) => api.delete(`/models/${id}`),

  // Technical Guide
  listTechnical: (modelId) => api.get(`/models/${modelId}/technical`),
  createTechnical: (modelId, data) => api.post(`/models/${modelId}/technical`, data),
  updateTechnical: (modelId, guideId, data) => api.put(`/models/${modelId}/technical/${guideId}`, data),
  deleteTechnical: (modelId, guideId) => api.delete(`/models/${modelId}/technical/${guideId}`),

  // Validation Reports
  listValidations: (modelId) => api.get(`/models/${modelId}/validations`),
  createValidation: (modelId, data) => api.post(`/models/${modelId}/validations`, data),
  deleteValidation: (modelId, reportId) => api.delete(`/models/${modelId}/validations/${reportId}`),

  // Gini History
  listGiniHistory: (modelId) => api.get(`/models/${modelId}/gini-history`),
  createGiniRecord: (modelId, data) => api.post(`/models/${modelId}/gini-history`, data),
  deleteGiniRecord: (modelId, recordId) => api.delete(`/models/${modelId}/gini-history/${recordId}`),
}

// ── Development ──
export const developmentApi = {
  listProjects: (params) => api.get('/development/projects', { params }),
  getProject: (id) => api.get(`/development/projects/${id}`),
  createProject: (data) => api.post('/development/projects', data),
  updateProject: (id, data) => api.put(`/development/projects/${id}`, data),
  deleteProject: (id) => api.delete(`/development/projects/${id}`),

  // Stages
  createStage: (projectId, data) => api.post(`/development/projects/${projectId}/stages`, data),
  updateStage: (projectId, stageId, data) => api.put(`/development/projects/${projectId}/stages/${stageId}`, data),
  deleteStage: (projectId, stageId) => api.delete(`/development/projects/${projectId}/stages/${stageId}`),

  // Tasks
  createTask: (stageId, data) => api.post(`/development/stages/${stageId}/tasks`, data),
  updateTask: (stageId, taskId, data) => api.put(`/development/stages/${stageId}/tasks/${taskId}`, data),
  deleteTask: (stageId, taskId) => api.delete(`/development/stages/${stageId}/tasks/${taskId}`),

  // Owners
  listOwners: () => api.get('/development/owners'),
}

export default api
