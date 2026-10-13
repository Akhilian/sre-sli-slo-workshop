import { describe, expect, it, vi } from 'vitest'
import { createTracker } from '../src/tracking.js'

function memoryStorage() {
  const items = new Map()
  return {
    getItem: (key) => items.get(key) ?? null,
    setItem: (key, value) => items.set(key, value),
  }
}

function setup({ statuses = {}, storage = memoryStorage() } = {}) {
  let clock = 1_000_000
  const api = {
    getDocument: vi.fn(async (id) => ({ id, status: statuses[id] ?? 'pending' })),
  }
  const tracker = createTracker({ api, storage, now: () => clock })
  return { tracker, api, storage, advance: (ms) => { clock += ms }, statuses }
}

describe('suivi des documents', () => {
  it('passe un document à done et mesure le temps depuis le dépôt', async () => {
    const { tracker, advance, statuses } = setup()
    tracker.add({ id: 1, title: 'Rapport', uploadedAt: 1_000_000 })

    advance(1000)
    await tracker.tick()
    expect(tracker.state.documents[0].status).toBe('pending')

    statuses[1] = 'done'
    advance(2000)
    await tracker.tick()

    const doc = tracker.state.documents[0]
    expect(doc.status).toBe('done')
    expect(doc.doneAt - doc.uploadedAt).toBe(3000)
  })

  it('arrête d\'interroger après 60 s et signale le document bloqué', async () => {
    const { tracker, api, advance } = setup()
    tracker.add({ id: 1, title: 'Rapport', uploadedAt: 1_000_000 })

    advance(61_000)
    await tracker.tick()
    expect(tracker.state.documents[0].status).toBe('stuck')

    api.getDocument.mockClear()
    advance(1000)
    await tracker.tick()
    expect(api.getDocument).not.toHaveBeenCalled()
  })

  it('relance le suivi d\'un document bloqué', async () => {
    const { tracker, advance, statuses } = setup()
    tracker.add({ id: 1, title: 'Rapport', uploadedAt: 1_000_000 })
    advance(61_000)
    await tracker.tick()

    tracker.retry(1)
    statuses[1] = 'done'
    await tracker.tick()

    expect(tracker.state.documents[0].status).toBe('done')
  })

  it('continue malgré une API en erreur', async () => {
    const { tracker, api, advance, statuses } = setup()
    tracker.add({ id: 1, title: 'Rapport', uploadedAt: 1_000_000 })

    api.getDocument.mockRejectedValueOnce(new Error('Erreur du serveur (500)'))
    await tracker.tick()
    expect(tracker.state.documents[0].status).toBe('pending')

    statuses[1] = 'done'
    advance(1000)
    await tracker.tick()
    expect(tracker.state.documents[0].status).toBe('done')
  })

  it('conserve la liste après un rechargement et reprend le suivi', async () => {
    const storage = memoryStorage()
    const first = setup({ storage })
    first.tracker.add({ id: 1, title: 'Rapport', uploadedAt: 1_000_000 })
    first.tracker.add({ id: 2, title: 'Budget', uploadedAt: 1_000_000 })
    first.statuses[2] = 'done'
    await first.tracker.tick()

    const second = setup({ storage, statuses: { 1: 'done' } })
    expect(second.tracker.state.documents.map((d) => [d.id, d.status])).toEqual([[2, 'done'], [1, 'pending']])

    await second.tracker.tick()
    expect(second.tracker.state.documents[1].status).toBe('done')
  })

  it('garde au plus 50 documents, les plus récents en tête', () => {
    const { tracker } = setup()
    for (let id = 1; id <= 55; id++) tracker.add({ id, title: `Doc ${id}`, uploadedAt: 0 })

    expect(tracker.state.documents).toHaveLength(50)
    expect(tracker.state.documents[0].id).toBe(55)
  })

  it('fonctionne sans stockage disponible', () => {
    const broken = { getItem: () => { throw new Error('bloqué') }, setItem: () => { throw new Error('bloqué') } }
    const { tracker } = setup({ storage: broken })

    tracker.add({ id: 1, title: 'Rapport', uploadedAt: 0 })

    expect(tracker.state.documents).toHaveLength(1)
  })
})
