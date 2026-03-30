export interface Project {
  id: string
  name: string
  description: string
  created_at: string
  updated_at?: string
}

export interface Document {
  id: string
  title: string
  format: string
  status: string
  content?: string
  project_id: string
  created_at: string
  updated_at?: string
}

export interface Entity {
  id: string
  name: string
  type: string
  confidence: number
  properties: Record<string, any>
  project_id: string
  created_at: string
}

export interface Triple {
  id: string
  head_id: string
  tail_id: string
  relation: string
  confidence: number
  valid: boolean
  project_id: string
  created_at: string
}

export interface Job {
  id: string
  type: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  current_step: string
  error_message?: string
  result?: Record<string, any>
  project_id: string
  created_at: string
  started_at?: string
  completed_at?: string
}

export interface GraphNode {
  id: string
  name: string
  type: string
}

export interface GraphEdge {
  id?: string
  source: string
  target: string
  relation: string
}

export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export interface User {
  id: string
  username: string
  email?: string
}

export interface AuthTokens {
  access_token: string
  refresh_token?: string
  token_type: string
}
