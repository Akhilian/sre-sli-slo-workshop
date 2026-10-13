import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError, fileUrl, TIMEOUT_MS } from '../src/api.js'

function reply(status, body) {
  return Promise.resolve(new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } }))
}

describe('api', () => {
  let fetchMock

  beforeEach(() => {
    fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.useRealTimers()
  })

  it('envoie le fichier en multipart sur /api/documents', async () => {
    fetchMock.mockReturnValue(reply(202, { id: 7 }))
    const file = new File(['contenu'], 'rapport.txt', { type: 'text/plain' })

    expect(await api.upload(file)).toEqual({ id: 7 })

    const [url, options] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/documents')
    expect(options.method).toBe('POST')
    expect(options.body).toBeInstanceOf(FormData)
    expect(options.body.get('file').name).toBe('rapport.txt')
    // Pas de Content-Type : le navigateur ajoute lui-même la frontière multipart.
    expect(options.headers).toBeUndefined()
  })

  it('envoie du JSON pour le pilotage des pannes', async () => {
    fetchMock.mockReturnValue(reply(200, { stale_index: 1 }))

    await api.setFault('stale_index', 1)

    const [url, options] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/admin/faults')
    expect(options.headers).toEqual({ 'Content-Type': 'application/json' })
    expect(JSON.parse(options.body)).toEqual({ name: 'stale_index', value: 1 })
  })

  it('donne le lien de téléchargement d\'un document', () => {
    expect(fileUrl(7)).toBe('/api/documents/7/file')
  })

  it('encode la requête de recherche', async () => {
    fetchMock.mockReturnValue(reply(200, { results: [] }))

    await api.search('doc-1a2b c&d')

    expect(fetchMock.mock.calls[0][0]).toBe('/api/search?q=doc-1a2b%20c%26d')
  })

  it('transforme une 5xx en ApiError', async () => {
    fetchMock.mockReturnValue(reply(500, { detail: 'Erreur interne simulée' }))

    const error = await api.upload(new File(['x'], 'a.txt')).catch((e) => e)

    expect(error).toBeInstanceOf(ApiError)
    expect(error.status).toBe(500)
    expect(error.message).toBe('Erreur du serveur (500)')
  })

  it('reprend le détail d\'une 422', async () => {
    fetchMock.mockReturnValue(reply(422, { detail: "Panne inconnue, valeurs possibles : ['stale_index']" }))
    await expect(api.setFault('x', 1)).rejects.toThrow('Panne inconnue')

    fetchMock.mockReturnValue(reply(422, { detail: [{ msg: 'Field required' }] }))
    await expect(api.faults()).rejects.toThrow('Field required')
  })

  it('reprend le détail d\'une 413', async () => {
    fetchMock.mockReturnValue(reply(413, { detail: 'Fichier trop volumineux (5 Mio au plus)' }))

    await expect(api.upload(new File(['x'], 'gros.bin'))).rejects.toThrow('Fichier trop volumineux (5 Mio au plus)')
  })

  it('signale une API injoignable', async () => {
    fetchMock.mockRejectedValue(new TypeError('Failed to fetch'))

    const error = await api.faults().catch((e) => e)

    expect(error.status).toBe(0)
    expect(error.message).toBe('API injoignable')
  })

  it('abandonne après 10 s', async () => {
    vi.useFakeTimers()
    fetchMock.mockImplementation((url, { signal }) => new Promise((resolve, reject) => {
      signal.addEventListener('abort', () => reject(new DOMException('aborted', 'AbortError')))
    }))

    const pending = api.getDocument(1).catch((e) => e)
    await vi.advanceTimersByTimeAsync(TIMEOUT_MS)

    expect((await pending).message).toBe('Délai dépassé (10 s)')
  })
})
