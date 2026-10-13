<script setup>
import { computed, ref } from 'vue'
import { CloudUpload, Download, Upload } from 'lucide-vue-next'
import { fileUrl } from '../api.js'
import { formatSize, formatWhen } from '../format.js'
import FileName from './FileName.vue'
import FileTrack from './FileTrack.vue'

const props = defineProps({
  documents: { type: Array, required: true },
  now: { type: Number, required: true },
})
defineEmits(['pick', 'retry', 'clear'])

const confirming = ref(false)

const summary = computed(() => {
  const count = (status) => props.documents.filter((d) => d.status === status).length
  return [
    { status: 'done', n: count('done'), label: (n) => (n > 1 ? 'disponibles' : 'disponible') },
    { status: 'pending', n: count('pending'), label: () => 'en traitement' },
    { status: 'stuck', n: count('stuck'), label: (n) => (n > 1 ? 'bloqués' : 'bloqué') },
  ].filter((s) => s.n > 0)
})
</script>

<template>
  <section class="files" aria-labelledby="files-title">
    <div class="page-head">
      <div>
        <h1 id="files-title">Mes fichiers</h1>
        <p v-if="summary.length" class="summary">
          <span v-for="s in summary" :key="s.status" :class="['summary-item', `summary-${s.status}`]">
            <span class="summary-dot" aria-hidden="true"></span>{{ s.n }} {{ s.label(s.n) }}
          </span>
        </p>
      </div>
      <button type="button" class="button-primary" @click="$emit('pick')">
        <Upload :size="20" aria-hidden="true" />Déposer des fichiers
      </button>
    </div>

    <div v-if="!documents.length" class="empty-drop">
      <CloudUpload class="empty-icon" :size="48" :stroke-width="1.5" aria-hidden="true" />
      <p class="empty-title">Glissez vos fichiers ici pour les partager</p>
      <p class="empty-text">
        Ils seront traités puis disponibles au téléchargement. Les fichiers texte se retrouvent aussi par leur contenu.
      </p>
      <button type="button" class="button-secondary" @click="$emit('pick')">Choisir sur mon ordinateur</button>
    </div>

    <template v-else>
      <p class="track-legend-compact">Trajet de chaque fichier : Envoyé → Traitement → Disponible</p>
      <table class="file-table">
        <thead>
          <tr>
            <th scope="col">Nom</th>
            <th scope="col" class="col-track">
              <span class="visually-hidden">Trajet : envoyé, traitement, disponible</span>
              <span class="track-legend" aria-hidden="true"><span>Envoyé</span><span>Traitement</span><span>Disponible</span></span>
            </th>
            <th scope="col" class="col-num">Taille</th>
            <th scope="col" class="col-num">Déposé</th>
            <th scope="col"><span class="visually-hidden">Action</span></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="doc in documents" :key="doc.id" :class="`row-${doc.status}`">
            <td class="cell-name"><FileName :id="doc.id" :title="doc.title" /></td>
            <td class="cell-track"><FileTrack :doc="doc" :now="now" @retry="$emit('retry', $event)" /></td>
            <td class="col-num cell-meta">{{ formatSize(doc.size) }}</td>
            <td class="col-num cell-meta">{{ formatWhen(doc.uploadedAt, now) }}</td>
            <td class="col-num cell-action">
              <a v-if="doc.status === 'done'" class="button-ghost" :href="fileUrl(doc.id)" download>
                <Download :size="18" aria-hidden="true" />Télécharger<span class="visually-hidden"> {{ doc.title }}</span>
              </a>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="table-foot">
        <span>Fichiers déposés depuis ce navigateur · 50 au plus</span>
        <span v-if="confirming" class="confirm">
          Effacer l’historique ? Les fichiers restent disponibles par la recherche.
          <button type="button" class="link-button" @click="$emit('clear'); confirming = false">Effacer</button>
          <button type="button" class="link-button" @click="confirming = false">Annuler</button>
        </span>
        <button v-else type="button" class="link-button" @click="confirming = true">Effacer l’historique</button>
      </div>
    </template>
  </section>
</template>
