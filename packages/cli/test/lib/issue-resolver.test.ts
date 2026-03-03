import {expect} from 'chai'

import type {Issue, Project} from '../../src/types/plane.js'

import {resolveIssueId} from '../../src/lib/issue-resolver.js'
import {mockAPI} from '../helpers/mock-api.js'

describe('resolveIssueId', () => {
  const mockProject: Project = {
    created_at: '',
    id: '12345678-1234-1234-1234-123456789abc',
    identifier: 'MP',
    name: 'My Project',
    network: 1,
    updated_at: '',
    workspace: 'test-workspace',
  }

  const mockIssue: Issue = {
    assignees: [],
    created_at: '',
    id: 'abcdef12-3456-7890-abcd-ef1234567890',
    labels: [],
    name: 'Test Issue',
    priority: 'medium',
    project_id: '12345678-1234-1234-1234-123456789abc',
    sequence_id: 42,
    state: 'backlog',
    state_id: 'state-uuid',
    updated_at: '',
    workspace_id: 'test-workspace',
  }

  it('resolves UUID directly when projectId is provided', async () => {
    const api = mockAPI()
    const validUuid = 'abcdef12-3456-7890-abcd-ef1234567890'
    const result = await resolveIssueId(api, 'workspace', validUuid, '12345678-1234-1234-1234-123456789abc')

    expect(result).to.deep.equal({issueId: validUuid, projectId: '12345678-1234-1234-1234-123456789abc'})
  })

  it('throws when UUID is provided without projectId', async () => {
    const api = mockAPI()
    const validUuid = 'abcdef12-3456-7890-abcd-ef1234567890'

    try {
      await resolveIssueId(api, 'workspace', validUuid)
      expect.fail('Should have thrown')
    } catch (error) {
      expect((error as Error).message).to.include('project-id required')
    }
  })

  it('resolves PROJECT-123 format', async () => {
    const api = mockAPI({
      listIssues: async () => ({count: 1, results: [mockIssue]}),
      listProjects: async () => ({count: 1, results: [mockProject]}),
    })

    const result = await resolveIssueId(api, 'workspace', 'MP-42')

    expect(result).to.deep.equal({issueId: 'abcdef12-3456-7890-abcd-ef1234567890', projectId: '12345678-1234-1234-1234-123456789abc'})
  })

  it('throws on invalid format', async () => {
    const api = mockAPI()

    try {
      await resolveIssueId(api, 'workspace', 'invalid-format')
      expect.fail('Should have thrown')
    } catch (error) {
      expect((error as Error).message).to.include('Invalid issue ID format')
    }
  })

  it('throws when project not found', async () => {
    const api = mockAPI({
      listProjects: async () => ({count: 1, results: [mockProject]}),
    })

    try {
      await resolveIssueId(api, 'workspace', 'XX-1')
      expect.fail('Should have thrown')
    } catch (error) {
      expect((error as Error).message).to.include('Project not found')
    }
  })

  it('throws when issue not found', async () => {
    const api = mockAPI({
      listIssues: async () => ({count: 0, results: []}),
      listProjects: async () => ({count: 1, results: [mockProject]}),
    })

    try {
      await resolveIssueId(api, 'workspace', 'MP-999')
      expect.fail('Should have thrown')
    } catch (error) {
      expect((error as Error).message).to.include('Issue MP-999 not found')
    }
  })

  it('handles single letter identifiers', async () => {
    const projectP: Project = {
      ...mockProject,
      id: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
      identifier: 'P',
    }
    const issueForP: Issue = {
      ...mockIssue,
      id: 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
      project_id: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
      sequence_id: 1,
    }

    const api = mockAPI({
      listIssues: async () => ({count: 1, results: [issueForP]}),
      listProjects: async () => ({count: 1, results: [projectP]}),
    })

    const result = await resolveIssueId(api, 'workspace', 'P-1')

    expect(result.projectId).to.equal('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa')
  })

  it('accepts lowercase UUIDs', async () => {
    const api = mockAPI()
    const lowerUuid = 'abcdef12-3456-7890-abcd-ef1234567890'
    const result = await resolveIssueId(api, 'workspace', lowerUuid, '12345678-1234-1234-1234-123456789abc')

    expect(result.issueId).to.equal(lowerUuid)
  })

  it('accepts uppercase UUIDs', async () => {
    const api = mockAPI()
    const upperUuid = 'ABCDEF12-3456-7890-ABCD-EF1234567890'
    const result = await resolveIssueId(api, 'workspace', upperUuid, '12345678-1234-1234-1234-123456789abc')

    expect(result.issueId).to.equal(upperUuid)
  })
})
