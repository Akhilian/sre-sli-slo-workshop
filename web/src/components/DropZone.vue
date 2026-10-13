<script setup>
import { reactive, ref } from 'vue'
import { api } from '../api.js'

const emit = defineEmits(['uploaded'])

const dragging = ref(false)
const picker = ref(null)
// Envois en cours ou en échec. Un envoi réussi quitte la zone et rejoint « Mes documents ».
const uploads = ref([])
let nextKey = 0

function send(files) {
  for (const file of files) {
    const upload = reactive({ key: nextKey++, file, error: '' })
    uploads.value.push(upload)
    start(upload)
  }
}

async function start(upload) {
  upload.error = ''
  const uploadedAt = Date.now()
  try {
    const { id } = await api.upload(upload.file)
    uploads.value = uploads.value.filter((u) => u.key !== upload.key)
    emit('uploaded', { id, title: upload.file.name, uploadedAt })
  } catch (e) {
    // Le fichier reste dans la zone pour réessayer.
    upload.error = e.message
  }
}

function dismiss(upload) {
  uploads.value = uploads.value.filter((u) => u.key !== upload.key)
}

function onDrop(event) {
  dragging.value = false
  send(event.dataTransfer.files)
}

function onPick(event) {
  send(event.target.files)
  event.target.value = '' // pour pouvoir choisir à nouveau le même fichier
}
</script>

<template>
  <section class="panel">
    <h2>Déposer des fichiers</h2>
    <div
      :class="['dropzone', { 'dropzone-active': dragging }]"
      @dragenter.prevent="dragging = true"
      @dragover.prevent="dragging = true"
      @dragleave.prevent="dragging = false"
      @drop.prevent="onDrop"
    >
      <p class="dropzone-text">Glissez vos fichiers ici</p>
      <p class="hint">Les fichiers texte sont aussi recherchables par leur contenu. 5 Mio au plus par fichier.</p>
      <button type="button" class="button-primary" @click="picker.click()">Choisir des fichiers</button>
      <input ref="picker" type="file" multiple hidden @change="onPick" />
    </div>
    <ul v-if="uploads.length" class="list uploads">
      <li v-for="upload in uploads" :key="upload.key" class="list-item">
        <span class="doc-title">{{ upload.file.name }}</span>
        <div v-if="upload.error" class="list-meta">
          <span class="status status-stuck">Échec</span>
          <span class="message-inline-error">{{ upload.error }}</span>
          <button type="button" class="button-quiet" @click="start(upload)">Réessayer</button>
          <button type="button" class="button-quiet" @click="dismiss(upload)">Retirer</button>
        </div>
        <span v-else class="status status-pending">Envoi en cours…</span>
      </li>
    </ul>
  </section>
</template>
