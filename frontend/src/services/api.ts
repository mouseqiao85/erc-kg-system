import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const projectService = {
  getProjects: (params?: any) => api.get('/projects', { params }),
  getProject: (id: string) => api.get(`/projects/${id}`),
  createProject: (data: any) => api.post('/projects', data),
  deleteProject: (id: string) => api.delete(`/projects/${id}`),
}

export const documentService = {
  getDocuments: (params?: any) => api.get('/documents', { params }),
  getDocument: (id: string) => api.get(`/documents/${id}`),
  uploadDocument: (file: File, projectId: string) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('project_id', projectId)
    return api.post('/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  deleteDocument: (id: string) => api.delete(`/documents/${id}`),
}

export const entityService = {
  getEntities: (params?: any) => api.get('/entities', { params }),
  getEntity: (id: string) => api.get(`/entities/${id}`),
  createEntity: (data: any) => api.post('/entities', data),
  deleteEntity: (id: string) => api.delete(`/entities/${id}`),
}

export const tripleService = {
  getTriples: (params?: any) => api.get('/triples', { params }),
  createTriple: (data: any) => api.post('/triples', data),
  deleteTriple: (id: string) => api.delete(`/triples/${id}`),
}

export const jobService = {
  getJobs: (projectId?: string) => api.get('/jobs', { params: { project_id: projectId } }),
  getJob: (id: string) => api.get(`/jobs/${id}`),
  createJob: (data: any) => api.post('/jobs', data),
}

export const graphService = {
  getGraph: (projectId: string, limit?: number) => api.get('/graph', { params: { project_id: projectId, limit } }),
  getSubgraph: (entityId: string, depth?: number) => api.get('/graph/subgraph', { params: { entity_id: entityId, depth } }),
  queryCypher: (query: string) => api.post('/graph/cypher', { query }),
}

export const authService = {
  login: (data: { username: string; password: string }) => api.post('/auth/login', data),
  refresh: (refreshToken: string) => api.post('/auth/refresh', { refresh_token: refreshToken }),
}

export default api
