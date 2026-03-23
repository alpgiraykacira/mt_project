import axios from 'axios'

// CodeServer proxy: /codeserver/proxy/5000 -> localhost:5000
// Detect if running behind CodeServer proxy
function getBaseURL() {
  if (import.meta.env.VITE_API_URL) return import.meta.env.VITE_API_URL
  const { origin, pathname } = window.location
  // If accessed via CodeServer proxy (e.g., /codeserver/proxy/5173/)
  // then API is at /codeserver/proxy/5000/api
  const csMatch = pathname.match(/^(\/codeserver\/proxy\/)(\d+)/)
  if (csMatch) return `${origin}${csMatch[1]}5000/api`
  return '/api'
}

const api = axios.create({
  baseURL: getBaseURL(),
  headers: {
    'Content-Type': 'application/json',
  },
})

// ── Simple in-memory cache with TTL for read-only endpoints ──
const _cache = new Map()
const CACHE_TTL_MS = 30_000  // 30 seconds

function cachedGet(url) {
  const entry = _cache.get(url)
  if (entry && Date.now() - entry.ts < CACHE_TTL_MS) {
    return Promise.resolve(entry.data)
  }
  return api.get(url).then(res => {
    _cache.set(url, { data: res, ts: Date.now() })
    return res
  })
}

export function invalidateDashboardCache() {
  _cache.clear()
}

// ── Dashboard ──
export const dashboardApi = {
  getSummary: () => cachedGet('/dashboard/summary'),
  getGiniOverview: () => cachedGet('/dashboard/gini-overview'),
  getDevelopmentProgress: () => cachedGet('/dashboard/development-progress'),
  getGiniAlerts: () => cachedGet('/dashboard/gini-alerts'),
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
  uploadValidation: (modelId, formData) => api.post(`/models/${modelId}/validations`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  downloadValidation: (modelId, reportId) => `${api.defaults.baseURL}/models/${modelId}/validations/${reportId}/download`,
  deleteValidation: (modelId, reportId) => api.delete(`/models/${modelId}/validations/${reportId}`),

  // Gini History
  listGiniHistory: (modelId, params) => api.get(`/models/${modelId}/gini-history`, { params }),
  createGiniRecord: (modelId, data) => api.post(`/models/${modelId}/gini-history`, data),

  // Rollout (İmplementasyon Kademeleri)
  listRollout: (modelId) => api.get(`/models/${modelId}/rollout`),
  createRollout: (modelId, data) => api.post(`/models/${modelId}/rollout`, data),
  updateRollout: (modelId, stageId, data) => api.put(`/models/${modelId}/rollout/${stageId}`, data),
  deleteRollout: (modelId, stageId) => api.delete(`/models/${modelId}/rollout/${stageId}`),

  // Model Variables (Feature Importance)
  listVariables: (modelId) => api.get(`/models/${modelId}/variables`),
  createVariable: (modelId, data) => api.post(`/models/${modelId}/variables`, data),
  updateVariable: (modelId, varId, data) => api.put(`/models/${modelId}/variables/${varId}`, data),
  deleteVariable: (modelId, varId) => api.delete(`/models/${modelId}/variables/${varId}`),
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
