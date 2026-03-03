import {PlaneConfig} from '../types/config.js'
import {
  CreateCycleRequest,
  CreateInitiativeRequest,
  CreateIntakeRequest,
  CreateIssueRequest,
  CreateLabelRequest,
  CreateModuleRequest,
  CreatePageRequest,
  CreateProjectRequest,
  CreateStateRequest,
  Cycle,
  Initiative,
  Intake,
  Issue,
  Label,
  ListFilters,
  Member,
  Module,
  Page,
  Project,
  SearchResult,
  State,
  UpdateCycleRequest,
  UpdateIssueRequest,
  UpdateLabelRequest,
  UpdateModuleRequest,
  UpdateProjectRequest,
  User,
} from '../types/plane.js'
import {APIError} from './errors.js'

export class PlaneAPI {
  private authHeader: {'x-api-key': string} | {Authorization: string}
  private baseUrl: string

  constructor(config: PlaneConfig) {
    this.baseUrl = config.baseUrl || 'https://api.plane.so/api/v1'

    if (config.apiKey) {
      this.authHeader = {'x-api-key': config.apiKey}
    } else if (config.accessToken) {
      this.authHeader = {Authorization: `Bearer ${config.accessToken}`}
    } else {
      throw new Error('No API key or access token configured')
    }
  }

  async addIssuesToCycle(
    workspace: string,
    projectId: string,
    cycleId: string,
    issueIds: string[],
  ): Promise<void> {
    return this.request('POST', `/workspaces/${workspace}/projects/${projectId}/cycles/${cycleId}/add-issues/`, {
      issues: issueIds,
    })
  }

  async addIssuesToModule(
    workspace: string,
    projectId: string,
    moduleId: string,
    issueIds: string[],
  ): Promise<void> {
    return this.request('POST', `/workspaces/${workspace}/projects/${projectId}/modules/${moduleId}/add-issues/`, {
      issues: issueIds,
    })
  }

  async archiveCycle(workspace: string, cycleId: string): Promise<Cycle> {
    return this.request('POST', `/workspaces/${workspace}/cycles/${cycleId}/archive/`)
  }

  async archiveModule(workspace: string, moduleId: string): Promise<Module> {
    return this.request('POST', `/workspaces/${workspace}/modules/${moduleId}/archive/`)
  }

  async createCycle(workspace: string, projectId: string, data: CreateCycleRequest): Promise<Cycle> {
    return this.request('POST', `/workspaces/${workspace}/projects/${projectId}/cycles/`, data)
  }

  async createInitiative(workspace: string, data: CreateInitiativeRequest): Promise<Initiative> {
    return this.request('POST', `/workspaces/${workspace}/initiatives/`, data)
  }

  async createIntake(workspace: string, projectId: string, data: CreateIntakeRequest): Promise<Intake> {
    return this.request('POST', `/workspaces/${workspace}/projects/${projectId}/intakes/`, data)
  }

  async createIssue(workspace: string, projectId: string, data: CreateIssueRequest): Promise<Issue> {
    return this.request('POST', `/workspaces/${workspace}/projects/${projectId}/issues/`, data)
  }

  async createLabel(workspace: string, projectId: string, data: CreateLabelRequest): Promise<Label> {
    return this.request('POST', `/workspaces/${workspace}/projects/${projectId}/labels/`, data)
  }

  async createModule(workspace: string, projectId: string, data: CreateModuleRequest): Promise<Module> {
    return this.request('POST', `/workspaces/${workspace}/projects/${projectId}/modules/`, data)
  }

  async createProject(workspace: string, data: CreateProjectRequest): Promise<Project> {
    return this.request('POST', `/workspaces/${workspace}/projects/`, data)
  }

  async createProjectPage(workspace: string, projectId: string, data: CreatePageRequest): Promise<Page> {
    return this.request('POST', `/workspaces/${workspace}/projects/${projectId}/pages/`, data)
  }

  async createState(workspace: string, projectId: string, data: CreateStateRequest): Promise<State> {
    return this.request('POST', `/workspaces/${workspace}/projects/${projectId}/states/`, data)
  }

  async createWorkspacePage(workspace: string, data: CreatePageRequest): Promise<Page> {
    return this.request('POST', `/workspaces/${workspace}/pages/`, data)
  }

  async deleteCycle(workspace: string, cycleId: string): Promise<void> {
    return this.request('DELETE', `/workspaces/${workspace}/cycles/${cycleId}/`)
  }

  async deleteInitiative(workspace: string, initiativeId: string): Promise<void> {
    return this.request('DELETE', `/workspaces/${workspace}/initiatives/${initiativeId}/`)
  }

  async deleteIntake(workspace: string, projectId: string, intakeId: string): Promise<void> {
    return this.request('DELETE', `/workspaces/${workspace}/projects/${projectId}/intakes/${intakeId}/`)
  }

  async deleteIssue(workspace: string, projectId: string, id: string): Promise<void> {
    return this.request('DELETE', `/workspaces/${workspace}/projects/${projectId}/issues/${id}/`)
  }

  async deleteLabel(workspace: string, projectId: string, labelId: string): Promise<void> {
    return this.request('DELETE', `/workspaces/${workspace}/projects/${projectId}/labels/${labelId}/`)
  }

  async deleteModule(workspace: string, moduleId: string): Promise<void> {
    return this.request('DELETE', `/workspaces/${workspace}/modules/${moduleId}/`)
  }

  async deleteProject(workspace: string, id: string): Promise<void> {
    return this.request('DELETE', `/workspaces/${workspace}/projects/${id}/`)
  }

  async deleteState(workspace: string, projectId: string, stateId: string): Promise<void> {
    return this.request('DELETE', `/workspaces/${workspace}/projects/${projectId}/states/${stateId}/`)
  }

  // Users
  async getCurrentUser(): Promise<User> {
    return this.request('GET', '/users/me/')
  }

  async getCycle(workspace: string, cycleId: string): Promise<Cycle> {
    return this.request('GET', `/workspaces/${workspace}/cycles/${cycleId}/`)
  }

  async getIssue(workspace: string, projectId: string, id: string): Promise<Issue> {
    return this.request('GET', `/workspaces/${workspace}/projects/${projectId}/issues/${id}/`)
  }

  async getModule(workspace: string, moduleId: string): Promise<Module> {
    return this.request('GET', `/workspaces/${workspace}/modules/${moduleId}/`)
  }

  async getProject(workspace: string, id: string): Promise<Project> {
    return this.request('GET', `/workspaces/${workspace}/projects/${id}/`)
  }

  async getProjectPage(workspace: string, projectId: string, pageId: string): Promise<Page> {
    return this.request('GET', `/workspaces/${workspace}/projects/${projectId}/pages/${pageId}/`)
  }

  // Pages
  async getWorkspacePage(workspace: string, pageId: string): Promise<Page> {
    return this.request('GET', `/workspaces/${workspace}/pages/${pageId}/`)
  }

  // Cycles
  async listCycles(
    workspace: string,
    projectId: string,
    archived?: boolean,
  ): Promise<{count: number; results: Cycle[];}> {
    const params = new URLSearchParams()
    if (archived !== undefined) params.append('archived', String(archived))

    const query = params.toString()
    const path = `/workspaces/${workspace}/projects/${projectId}/cycles/${query ? `?${query}` : ''}`
    return this.request('GET', path)
  }

  // Initiatives
  async listInitiatives(workspace: string): Promise<{count: number; results: Initiative[];}> {
    return this.request('GET', `/workspaces/${workspace}/initiatives/`)
  }

  // Intake
  async listIntake(
    workspace: string,
    projectId: string,
    status?: string,
  ): Promise<{count: number; results: Intake[];}> {
    const params = new URLSearchParams()
    if (status) params.append('status', status)

    const query = params.toString()
    const path = `/workspaces/${workspace}/projects/${projectId}/intakes/${query ? `?${query}` : ''}`
    return this.request('GET', path)
  }

  // Issues
  async listIssues(
    workspace: string,
    projectId: string,
    filters?: ListFilters,
  ): Promise<{count: number; results: Issue[];}> {
    const params = new URLSearchParams()
    if (filters?.cycle) params.append('cycle', filters.cycle)
    if (filters?.module) params.append('module', filters.module)
    if (filters?.state) params.append('state', filters.state)
    if (filters?.assignee) params.append('assignees', filters.assignee)
    if (filters?.limit) params.append('per_page', String(filters.limit))

    const query = params.toString()
    const path = `/workspaces/${workspace}/projects/${projectId}/issues/${query ? `?${query}` : ''}`
    return this.request('GET', path)
  }

  // Labels
  async listLabels(workspace: string, projectId: string): Promise<{count: number; results: Label[];}> {
    return this.request('GET', `/workspaces/${workspace}/projects/${projectId}/labels/`)
  }

  // Modules
  async listModules(
    workspace: string,
    projectId: string,
    archived?: boolean,
  ): Promise<{count: number; results: Module[];}> {
    const params = new URLSearchParams()
    if (archived !== undefined) params.append('archived', String(archived))

    const query = params.toString()
    const path = `/workspaces/${workspace}/projects/${projectId}/modules/${query ? `?${query}` : ''}`
    return this.request('GET', path)
  }

  async listProjectMembers(workspace: string, projectId: string): Promise<Member[]> {
    return this.request('GET', `/workspaces/${workspace}/projects/${projectId}/members/`)
  }

  // Projects
  async listProjects(workspace: string): Promise<{count: number; results: Project[];}> {
    return this.request('GET', `/workspaces/${workspace}/projects/`)
  }

  // States
  async listStates(workspace: string, projectId: string): Promise<{count: number; results: State[];}> {
    return this.request('GET', `/workspaces/${workspace}/projects/${projectId}/states/`)
  }

  // Workspace
  async listWorkspaceMembers(workspace: string): Promise<{count: number; results: Member[];}> {
    return this.request('GET', `/workspaces/${workspace}/members/`)
  }

  async removeIssueFromCycle(
    workspace: string,
    projectId: string,
    cycleId: string,
    issueId: string,
  ): Promise<void> {
    return this.request('POST', `/workspaces/${workspace}/projects/${projectId}/cycles/${cycleId}/remove-issue/`, {
      issue: issueId,
    })
  }

  async removeIssueFromModule(
    workspace: string,
    projectId: string,
    moduleId: string,
    issueId: string,
  ): Promise<void> {
    return this.request('POST', `/workspaces/${workspace}/projects/${projectId}/modules/${moduleId}/remove-issue/`, {
      issue: issueId,
    })
  }

  async searchIssues(
    workspace: string,
    params: {project_id?: string; query: string;},
  ): Promise<SearchResult[]> {
    const searchParams = new URLSearchParams()
    searchParams.append('search', params.query)
    if (params.project_id) searchParams.append('project_id', params.project_id)

    return this.request('GET', `/workspaces/${workspace}/search/issues/?${searchParams.toString()}`)
  }

  async transferCycleIssues(workspace: string, fromCycleId: string, toCycleId: string): Promise<void> {
    return this.request('POST', `/workspaces/${workspace}/cycles/${fromCycleId}/transfer-issues/`, {
      new_cycle_id: toCycleId,
    })
  }

  async unarchiveCycle(workspace: string, cycleId: string): Promise<Cycle> {
    return this.request('POST', `/workspaces/${workspace}/cycles/${cycleId}/unarchive/`)
  }

  async unarchiveModule(workspace: string, moduleId: string): Promise<Module> {
    return this.request('POST', `/workspaces/${workspace}/modules/${moduleId}/unarchive/`)
  }

  async updateCycle(workspace: string, cycleId: string, data: UpdateCycleRequest): Promise<Cycle> {
    return this.request('PATCH', `/workspaces/${workspace}/cycles/${cycleId}/`, data)
  }

  async updateIssue(
    workspace: string,
    projectId: string,
    id: string,
    data: UpdateIssueRequest,
  ): Promise<Issue> {
    return this.request('PATCH', `/workspaces/${workspace}/projects/${projectId}/issues/${id}/`, data)
  }

  async updateLabel(
    workspace: string,
    projectId: string,
    labelId: string,
    data: UpdateLabelRequest,
  ): Promise<Label> {
    return this.request('PATCH', `/workspaces/${workspace}/projects/${projectId}/labels/${labelId}/`, data)
  }

  async updateModule(workspace: string, moduleId: string, data: UpdateModuleRequest): Promise<Module> {
    return this.request('PATCH', `/workspaces/${workspace}/modules/${moduleId}/`, data)
  }

  async updateProject(workspace: string, id: string, data: UpdateProjectRequest): Promise<Project> {
    return this.request('PATCH', `/workspaces/${workspace}/projects/${id}/`, data)
  }

  private async request<T>(method: string, path: string, body?: unknown): Promise<T> {
    const url = `${this.baseUrl}${path}`
    const res = await fetch(url, {
      body: body ? JSON.stringify(body) : undefined,
      headers: {
        'Content-Type': 'application/json',
        ...this.authHeader,
      },
      method,
    })

    if (!res.ok) {
      const error = await res.text()
      throw new APIError(res.status, error, path)
    }

    // 204 No Content (e.g. DELETE responses) — no body to parse
    if (res.status === 204) {
      return undefined as T
    }

    return res.json() as Promise<T>
  }
}
