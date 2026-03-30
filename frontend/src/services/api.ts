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
  naturalQuery: (question: string, projectId?: string) => api.post('/graph/natural', { question: { question, project_id: projectId } }),
}

export const authService = {
  login: (data: { username: string; password: string }) => api.post('/auth/login', data),
  refresh: (refreshToken: string) => api.post('/auth/refresh', { refresh_token: refreshToken }),
}

export const sentimentService = {
  getIndustryOverview: (industries?: string[]) => api.get('/sentiment/industry-overview', { params: { industries } }),
  getCustomerNetwork: (customerId: string, depth?: number) => api.get(`/sentiment/customer-network/${customerId}`, { params: { depth } }),
  getEventEvolution: (eventId: string, includeArticles?: boolean) => api.get(`/sentiment/event-evolution/${eventId}`, { params: { include_articles: includeArticles } }),
  getHotspotClusters: (industry?: string, limit?: number) => api.get('/sentiment/hotspot-clusters', { params: { industry, limit } }),
  getEntitySentiment: (entityId: string) => api.get(`/sentiment/entity/${entityId}/sentiment`),
  getIndustryTrend: (industry: string, period?: string) => api.get(`/sentiment/industry/${industry}/trend`, { params: { period } }),
  getAlerts: (severity?: string, status?: string) => api.get('/sentiment/alerts', { params: { severity, status } }),
}

export const customerService = {
  getCustomers: (params?: any) => api.get('/customers', { params }),
  createCustomer: (data: any) => api.post('/customers', data),
}

export const articleService = {
  getArticles: (params?: any) => api.get('/sentiment/articles', { params }),
  createArticle: (data: any) => api.post('/sentiment/articles', data),
}

export const eventService = {
  getEvents: (params?: any) => api.get('/sentiment/events', { params }),
  createEvent: (data: any) => api.post('/sentiment/events', data),
}

export const sentimentTaskService = {
  startCollection: (source: string = 'rss') => api.post('/sentiment/tasks/collect', null, { params: { source } }),
  getCollectionStatus: (taskId: string) => api.get(`/sentiment/tasks/collect/${taskId}`),
  analyzeArticle: (articleId: string) => api.post(`/sentiment/tasks/analyze-article/${articleId}`),
  updateCustomerSentiment: (customerId: string) => api.post(`/sentiment/tasks/update-customer/${customerId}`),
}

export default api
