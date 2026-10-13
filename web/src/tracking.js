// Suivi des documents déposés depuis ce navigateur : statut, temps jusqu'à « done », état bloqué.
import { reactive } from 'vue'

const STORAGE_KEY = 'docshare.documents'
const MAX_DOCUMENTS = 50

export function createTracker({
  api,
  storage = globalThis.localStorage,
  now = Date.now,
  interval = 1000, // une interrogation par seconde
  timeout = 60_000, // comme le FOLLOW_TIMEOUT de k6
  onChange = () => {}, // appelé à chaque passage à « done » ou « stuck »
}) {
  const state = reactive({ documents: load(), now: now() })
  const inFlight = new Set()
  let timer = null

  // Après un rechargement, le suivi des documents en attente repart de zéro.
  for (const doc of state.documents) {
    if (doc.status === 'pending') doc.since = now()
  }

  function load() {
    try {
      return JSON.parse(storage.getItem(STORAGE_KEY)) || []
    } catch {
      return []
    }
  }

  function save() {
    try {
      storage.setItem(STORAGE_KEY, JSON.stringify(state.documents))
    } catch {
      // stockage indisponible (navigation privée) : le suivi reste en mémoire
    }
  }

  function add({ id, title, uploadedAt, size = null }) {
    state.documents.unshift({ id, title, size, status: 'pending', uploadedAt, doneAt: null, since: now() })
    state.documents.splice(MAX_DOCUMENTS)
    save()
  }

  function retry(id) {
    const doc = state.documents.find((d) => d.id === id)
    if (doc && doc.status === 'stuck') {
      doc.status = 'pending'
      doc.since = now()
      save()
    }
  }

  function clear() {
    state.documents.splice(0)
    save()
  }

  async function check(doc) {
    if (inFlight.has(doc.id)) return
    inFlight.add(doc.id)
    try {
      const { status } = await api.getDocument(doc.id)
      if (status === 'done' && doc.status === 'pending') {
        doc.status = 'done'
        doc.doneAt = now()
        save()
        onChange(doc)
      }
    } catch {
      // API en erreur : on réessaie à la seconde suivante, jusqu'au délai maximal
    } finally {
      inFlight.delete(doc.id)
    }
  }

  async function tick() {
    state.now = now()
    const checks = []
    for (const doc of state.documents) {
      if (doc.status !== 'pending') continue
      if (state.now - doc.since > timeout) {
        doc.status = 'stuck'
        save()
        onChange(doc)
      } else {
        checks.push(check(doc))
      }
    }
    await Promise.all(checks)
  }

  return {
    state,
    add,
    retry,
    clear,
    tick,
    start: () => {
      timer ??= setInterval(tick, interval)
    },
    stop: () => {
      clearInterval(timer)
      timer = null
    },
  }
}
