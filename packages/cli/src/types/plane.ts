export interface Project {
  created_at: string
  description?: string
  id: string
  identifier: string
  name: string
  network: number
  updated_at: string
  workspace: string
}

export interface Issue {
  assignees: string[]
  created_at: string
  description_html?: string
  id: string
  labels: string[]
  name: string
  priority: 'high' | 'low' | 'medium' | 'none' | 'urgent'
  project_id: string
  sequence_id: number
  state: string
  state_id: string
  updated_at: string
  workspace_id: string
}

export interface Cycle {
  archived: boolean
  created_at: string
  description?: string
  end_date?: string
  id: string
  name: string
  project_id: string
  start_date?: string
  updated_at: string
  workspace_id: string
}

export interface Module {
  archived: boolean
  created_at: string
  description?: string
  id: string
  name: string
  project_id: string
  start_date?: string
  target_date?: string
  updated_at: string
  workspace_id: string
}

export interface Label {
  color: string
  created_at: string
  id: string
  name: string
  project_id: string
  updated_at: string
  workspace_id: string
}

export interface State {
  color: string
  created_at: string
  default: boolean
  group: string
  id: string
  name: string
  project_id: string
  sequence: number
  updated_at: string
  workspace_id: string
}

export interface Intake {
  created_at: string
  description_html?: string
  id: string
  name: string
  project_id: string
  status: string
  updated_at: string
  workspace_id: string
}

export interface Initiative {
  created_at: string
  description?: string
  id: string
  name: string
  updated_at: string
  workspace_id: string
}

export interface Page {
  created_at: string
  description_html?: string
  id: string
  name: string
  owned_by: string
  project_id?: string
  updated_at: string
  workspace_id: string
}

export interface User {
  avatar_url?: string
  created_at: string
  display_name?: string
  email: string
  id: string
  updated_at: string
}

export interface Member {
  display_name?: string
  email: string
  id: string
  role: string
  status: string
}

// Request types
export interface CreateProjectRequest {
  description?: string
  identifier: string
  name: string
  network?: number
}

export interface UpdateProjectRequest {
  description?: string
  name?: string
}

export interface CreateIssueRequest {
  assignees?: string[]
  description_html?: string
  labels?: string[]
  name: string
  priority?: 'high' | 'low' | 'medium' | 'none' | 'urgent'
  state?: string
}

export interface UpdateIssueRequest {
  assignees?: string[]
  description_html?: string
  labels?: string[]
  name?: string
  priority?: 'high' | 'low' | 'medium' | 'none' | 'urgent'
  state?: string
}

export interface CreateCycleRequest {
  description?: string
  end_date?: string
  name: string
  start_date?: string
}

export interface UpdateCycleRequest {
  description?: string
  end_date?: string
  name?: string
  start_date?: string
}

export interface CreateModuleRequest {
  description?: string
  name: string
  start_date?: string
  target_date?: string
}

export interface UpdateModuleRequest {
  description?: string
  name?: string
  start_date?: string
  target_date?: string
}

export interface CreateLabelRequest {
  color: string
  name: string
}

export interface UpdateLabelRequest {
  color?: string
  name?: string
}

export interface CreateStateRequest {
  color: string
  group: string
  name: string
}

export interface CreateIntakeRequest {
  description_html?: string
  name: string
}

export interface CreateInitiativeRequest {
  description?: string
  name: string
}

export interface CreatePageRequest {
  description_html?: string
  name: string
}

export interface SearchResult {
  human_id: string
  id: string
  name: string
  priority: string
  project_identifier: string
}

export interface ListFilters {
  assignee?: string
  cycle?: string
  limit?: number
  module?: string
  state?: string
}
