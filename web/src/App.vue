<script setup>
import { onMounted, onUnmounted, reactive, ref } from 'vue'
import { announce, announcement } from './announce.js'
import { api } from './api.js'
import { createTracker } from './tracking.js'
import { createUploader } from './uploads.js'
import DropOverlay from './components/DropOverlay.vue'
import FaultConsole from './components/FaultConsole.vue'
import FilesView from './components/FilesView.vue'
import SearchResults from './components/SearchResults.vue'
import TopBar from './components/TopBar.vue'
import UploadTray from './components/UploadTray.vue'

// Pupitre des pannes : seulement avec ?admin dans l'URL. Ce n'est pas une sécurité.
const admin = new URLSearchParams(window.location.search).has('admin')

const tracker = createTracker({
  api,
  onChange: (doc) =>
    announce(doc.status === 'done' ? `${doc.title} est disponible` : `${doc.title} est bloqué en traitement`),
})

const uploader = createUploader({
  api,
  onUploaded: (doc) => {
    tracker.add(doc)
    announce(`${doc.title} envoyé, traitement en cours`)
  },
  onFailed: (item) => announce(`Échec de l’envoi de ${item.file.name}`),
})

// --- Dépôt : bouton, ou glisser n'importe où sur la page ---------------------

const picker = ref(null)
const dragging = ref(false)
let dragDepth = 0

function hasFiles(event) {
  return [...(event.dataTransfer?.types ?? [])].includes('Files')
}

function onDragEnter(event) {
  if (!hasFiles(event)) return
  event.preventDefault()
  dragDepth++
  dragging.value = true
}

function onDragLeave(event) {
  if (!hasFiles(event)) return
  dragDepth = Math.max(0, dragDepth - 1)
  if (dragDepth === 0) dragging.value = false
}

function onDragOver(event) {
  // Sans cela, un fichier lâché hors d'une zone ouvrirait le fichier à la place de l'application.
  if (hasFiles(event)) event.preventDefault()
}

function onDrop(event) {
  if (!hasFiles(event)) return
  event.preventDefault()
  dragDepth = 0
  dragging.value = false
  uploader.send(event.dataTransfer.files)
}

function onPick(event) {
  uploader.send(event.target.files)
  event.target.value = '' // pour pouvoir choisir à nouveau le même fichier
}

function closeTray() {
  uploader.clearFinished()
  for (const item of [...uploader.items]) uploader.dismiss(item)
}

// --- Recherche ----------------------------------------------------------------

const search = reactive({ query: '', results: null, error: '' })
let searchRun = 0

async function runSearch(q) {
  const run = ++searchRun
  Object.assign(search, { query: q, results: null, error: '' })
  try {
    // Une réponse vide s'affiche comme telle, même si l'API a masqué une erreur : c'est l'exercice.
    const { results } = await api.search(q)
    if (run !== searchRun) return
    search.results = results
    announce(`${results.length} ${results.length > 1 ? 'résultats' : 'résultat'} pour ${q}`)
  } catch (e) {
    if (run !== searchRun) return
    search.error = `La recherche n’a pas abouti : ${e.message}. Réessayez dans un instant.`
  }
}

function clearSearch() {
  searchRun++
  Object.assign(search, { query: '', results: null, error: '' })
}

onMounted(() => {
  tracker.start()
  window.addEventListener('dragenter', onDragEnter)
  window.addEventListener('dragleave', onDragLeave)
  window.addEventListener('dragover', onDragOver)
  window.addEventListener('drop', onDrop)
})

onUnmounted(() => {
  tracker.stop()
  window.removeEventListener('dragenter', onDragEnter)
  window.removeEventListener('dragleave', onDragLeave)
  window.removeEventListener('dragover', onDragOver)
  window.removeEventListener('drop', onDrop)
})
</script>

<template>
  <TopBar :query="search.query" @search="runSearch" @clear="clearSearch" />

  <main class="workspace">
    <SearchResults
      v-if="search.query"
      :query="search.query"
      :results="search.results"
      :error="search.error"
      @back="clearSearch"
    />
    <FilesView
      v-else
      :documents="tracker.state.documents"
      :now="tracker.state.now"
      @pick="picker.click()"
      @retry="tracker.retry"
      @clear="tracker.clear"
    />

    <FaultConsole v-if="admin" />
  </main>

  <input ref="picker" type="file" multiple hidden @change="onPick" />
  <UploadTray
    :items="uploader.items"
    :counts="uploader.counts.value"
    @retry="uploader.retry"
    @dismiss="uploader.dismiss"
    @close="closeTray"
  />
  <DropOverlay v-if="dragging" />
  <p class="visually-hidden" aria-live="polite">{{ announcement }}</p>
</template>
