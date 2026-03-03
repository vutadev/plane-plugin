import {expect} from 'chai'

import {PlaneAPI} from '../../src/lib/api.js'
import {APIError} from '../../src/lib/errors.js'

function mockJsonResponse(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    headers: {'Content-Type': 'application/json'},
    status,
  })
}

describe('PlaneAPI', () => {
  const mockConfig = {
    apiKey: 'test-api-key',
    baseUrl: 'https://api.test.com/api/v1',
    workspace: 'test-workspace',
  }

  let originalFetch: typeof globalThis.fetch
  let fetchCalls: Array<{init: RequestInit; url: string;}> = []

  beforeEach(() => {
    fetchCalls = []
    originalFetch = globalThis.fetch
  })

  afterEach(() => {
    globalThis.fetch = originalFetch
  })

  function mockFetch(response: Response): void {
    globalThis.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = input.toString()
      fetchCalls.push({init: init ?? {}, url})
      return response
    }
  }

  describe('constructor', () => {
    it('throws error when no API key or access token provided', () => {
      expect(() => new PlaneAPI({workspace: 'test'})).to.throw('No API key or access token configured')
    })

    it('accepts API key', () => {
      const api = new PlaneAPI(mockConfig)
      expect(api).to.be.instanceOf(PlaneAPI)
    })

    it('accepts access token', () => {
      const api = new PlaneAPI({
        accessToken: 'test-token',
        baseUrl: 'https://api.test.com/api/v1',
        workspace: 'test',
      })
      expect(api).to.be.instanceOf(PlaneAPI)
    })
  })

  describe('listProjects', () => {
    it('fetches projects from workspace', async () => {
      const mockProjects = {
        count: 2,
        results: [
          {id: 'proj-1', identifier: 'P1', name: 'Project 1'},
          {id: 'proj-2', identifier: 'P2', name: 'Project 2'},
        ],
      }
      mockFetch(mockJsonResponse(mockProjects))

      const api = new PlaneAPI(mockConfig)
      const result = await api.listProjects('test-workspace')

      expect(result.results).to.have.lengthOf(2)
      expect(result.count).to.equal(2)
      expect(fetchCalls[0].url).to.include('/workspaces/test-workspace/projects/')
    })
  })

  describe('getProject', () => {
    it('fetches a specific project', async () => {
      const mockProject = {id: 'proj-1', identifier: 'P1', name: 'Project 1'}
      mockFetch(mockJsonResponse(mockProject))

      const api = new PlaneAPI(mockConfig)
      const result = await api.getProject('test-workspace', 'proj-1')

      expect(result.id).to.equal('proj-1')
      expect(fetchCalls[0].url).to.include('/workspaces/test-workspace/projects/proj-1/')
    })
  })

  describe('createProject', () => {
    it('posts project data to API', async () => {
      const mockProject = {id: 'new-proj', identifier: 'NEW', name: 'New Project'}
      mockFetch(mockJsonResponse(mockProject))

      const api = new PlaneAPI(mockConfig)
      const result = await api.createProject('test-workspace', {
        identifier: 'NEW',
        name: 'New Project',
      })

      expect(result.name).to.equal('New Project')
      expect(fetchCalls[0].init.method).to.equal('POST')
      expect(fetchCalls[0].url).to.include('/workspaces/test-workspace/projects/')
    })
  })

  describe('listIssues', () => {
    it('fetches issues for a project', async () => {
      const mockIssues = {
        count: 2,
        results: [
          {id: 'issue-1', name: 'Issue 1', sequence_id: 1},
          {id: 'issue-2', name: 'Issue 2', sequence_id: 2},
        ],
      }
      mockFetch(mockJsonResponse(mockIssues))

      const api = new PlaneAPI(mockConfig)
      const result = await api.listIssues('test-workspace', 'proj-1')

      expect(result.results).to.have.lengthOf(2)
      expect(fetchCalls[0].url).to.include('/workspaces/test-workspace/projects/proj-1/issues/')
    })

    it('applies filters when provided', async () => {
      mockFetch(mockJsonResponse({count: 0, results: []}))

      const api = new PlaneAPI(mockConfig)
      await api.listIssues('test-workspace', 'proj-1', {
        cycle: 'cycle-1',
        limit: 10,
        state: 'backlog',
      })

      expect(fetchCalls[0].url).to.include('cycle=cycle-1')
      expect(fetchCalls[0].url).to.include('state=backlog')
      expect(fetchCalls[0].url).to.include('per_page=10')
    })
  })

  describe('error handling', () => {
    it('throws APIError on non-ok response', async () => {
      mockFetch(new Response('Not found', {status: 404}))

      const api = new PlaneAPI(mockConfig)
      try {
        await api.getProject('test-workspace', 'nonexistent')
        expect.fail('Should have thrown')
      } catch (error) {
        expect(error).to.be.instanceOf(APIError)
        expect((error as APIError).status).to.equal(404)
      }
    })

    it('includes correct auth header for API key', async () => {
      mockFetch(mockJsonResponse({count: 0, results: []}))

      const api = new PlaneAPI(mockConfig)
      await api.listProjects('test-workspace')

      const headers = fetchCalls[0].init.headers as Record<string, string>
      expect(headers['x-api-key']).to.equal('test-api-key')
    })

    it('includes correct auth header for access token', async () => {
      mockFetch(mockJsonResponse({count: 0, results: []}))

      const api = new PlaneAPI({
        accessToken: 'test-token',
        baseUrl: 'https://api.test.com/api/v1',
        workspace: 'test',
      })
      await api.listProjects('test-workspace')

      const headers = fetchCalls[0].init.headers as Record<string, string>
      expect(headers.Authorization).to.equal('Bearer test-token')
    })
  })

  describe('cycles', () => {
    it('lists cycles for a project', async () => {
      mockFetch(mockJsonResponse({count: 0, results: []}))

      const api = new PlaneAPI(mockConfig)
      await api.listCycles('test-workspace', 'proj-1')

      expect(fetchCalls[0].url).to.include('/workspaces/test-workspace/projects/proj-1/cycles/')
    })

    it('archives a cycle', async () => {
      mockFetch(mockJsonResponse({archived: true, id: 'cycle-1'}))

      const api = new PlaneAPI(mockConfig)
      await api.archiveCycle('test-workspace', 'cycle-1')

      expect(fetchCalls[0].init.method).to.equal('POST')
      expect(fetchCalls[0].url).to.include('/cycles/cycle-1/archive/')
    })
  })

  describe('modules', () => {
    it('lists modules for a project', async () => {
      mockFetch(mockJsonResponse({count: 0, results: []}))

      const api = new PlaneAPI(mockConfig)
      await api.listModules('test-workspace', 'proj-1')

      expect(fetchCalls[0].url).to.include('/workspaces/test-workspace/projects/proj-1/modules/')
    })
  })
})
