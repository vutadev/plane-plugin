import {PlaneAPI} from './api.js'

export async function resolveIssueId(
  api: PlaneAPI,
  workspace: string,
  id: string,
  projectId?: string,
): Promise<{issueId: string; projectId: string;}> {
  // Check if it's already a UUID
  if (isUUID(id)) {
    if (!projectId) {
      throw new Error('project-id required when using UUID')
    }

    return {issueId: id, projectId}
  }

  // Parse PROJECT-123 format
  const match = id.match(/^([A-Z]+)-(\d+)$/)
  if (!match) {
    throw new Error(`Invalid issue ID format: ${id}. Use UUID or PROJECT-123 format.`)
  }

  const [, identifier, sequence] = match

  // Find project by identifier
  const {results: projects} = await api.listProjects(workspace)
  const project = projects.find((p) => p.identifier === identifier)

  if (!project) {
    throw new Error(`Project not found: ${identifier}`)
  }

  // Get issue by sequence_id
  const {results: issues} = await api.listIssues(workspace, project.id)
  const issue = issues.find((i) => i.sequence_id === Number.parseInt(sequence, 10))

  if (!issue) {
    throw new Error(`Issue ${id} not found`)
  }

  return {issueId: issue.id, projectId: project.id}
}

function isUUID(str: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(str)
}
