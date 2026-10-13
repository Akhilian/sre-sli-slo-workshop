<script setup>
import { fileUrl } from '../api.js'

defineProps({
  documents: { type: Array, required: true },
  now: { type: Number, required: true },
})
defineEmits(['retry', 'clear'])

const LABELS = { pending: 'En traitement', done: 'Traité', stuck: 'Bloqué' }

function seconds(ms) {
  return `${Math.round(ms / 1000)} s`
}
</script>

<template>
  <section class="panel">
    <div class="panel-header">
      <h2>Mes documents</h2>
      <button v-if="documents.length" type="button" class="button-quiet" @click="$emit('clear')">Vider la liste</button>
    </div>
    <p v-if="!documents.length" class="message-empty">Aucun document déposé depuis ce navigateur.</p>
    <ul v-else class="list">
      <li v-for="doc in documents" :key="doc.id" class="list-item">
        <div class="list-main">
          <span class="doc-id">#{{ doc.id }}</span>
          <a class="doc-title" :href="fileUrl(doc.id)" download>{{ doc.title }}</a>
        </div>
        <div class="list-meta">
          <span :class="['status', `status-${doc.status}`]">{{ LABELS[doc.status] }}</span>
          <span v-if="doc.status === 'done'" class="duration">en {{ seconds(doc.doneAt - doc.uploadedAt) }}</span>
          <span v-else-if="doc.status === 'pending'" class="duration">depuis {{ seconds(now - doc.uploadedAt) }}</span>
          <template v-else>
            <span class="duration">toujours en attente après 60 s</span>
            <button type="button" class="button-quiet" @click="$emit('retry', doc.id)">Relancer le suivi</button>
          </template>
        </div>
      </li>
    </ul>
  </section>
</template>
