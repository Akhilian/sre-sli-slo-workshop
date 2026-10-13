// Seul module qui parle à l'API. Tout passe par /api, relayé vers l'API par nginx (ou Vite en dev).

export const TIMEOUT_MS = 10_000

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status // 0 : pas de réponse (réseau, délai dépassé)
  }
}

export async function request(path, { method = 'GET', body } = {}) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS)
  let response
  try {
    // Un FormData part tel quel : le navigateur pose lui-même l'en-tête multipart.
    const isForm = body instanceof FormData
    response = await fetch(`/api${path}`, {
      method,
      headers: body && !isForm ? { 'Content-Type': 'application/json' } : undefined,
      body: isForm ? body : body && JSON.stringify(body),
      signal: controller.signal,
    })
  } catch (error) {
    throw new ApiError(error.name === 'AbortError' ? 'Délai dépassé (10 s)' : 'API injoignable', 0)
  } finally {
    clearTimeout(timer)
  }
  if (!response.ok) {
    throw new ApiError(await describe(response), response.status)
  }
  return response.json()
}

async function describe(response) {
  if (response.status >= 500) {
    return 'Le service n’a pas répondu. Réessayez dans un instant.'
  }
  try {
    const { detail } = await response.json()
    // FastAPI : chaîne pour une HTTPException, liste d'erreurs pour une validation.
    if (Array.isArray(detail)) return detail.map((error) => error.msg).join(', ')
    if (detail) return detail
  } catch {
    // corps absent ou non JSON
  }
  return `Requête refusée (${response.status})`
}

export function fileUrl(id) {
  return `/api/documents/${id}/file`
}

export const api = {
  upload: (file) => {
    const form = new FormData()
    form.append('file', file) // titre par défaut : le nom du fichier
    return request('/documents', { method: 'POST', body: form })
  },
  getDocument: (id) => request(`/documents/${id}`),
  search: (q) => request(`/search?q=${encodeURIComponent(q)}`),
  faults: () => request('/admin/faults'),
  setFault: (name, value) => request('/admin/faults', { method: 'POST', body: { name, value } }),
}
