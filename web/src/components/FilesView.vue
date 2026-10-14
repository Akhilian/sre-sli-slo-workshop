<script setup>
import { computed, nextTick, ref } from 'vue'
import { Download, Upload } from 'lucide-vue-next'
import { fileUrl } from '../api.js'
import { formatSize, formatWhen } from '../format.js'
import FileName from './FileName.vue'
import FileTrack from './FileTrack.vue'

const props = defineProps({
  documents: { type: Array, required: true },
  now: { type: Number, required: true },
})
const emit = defineEmits(['pick', 'retry', 'clear'])

const confirming = ref(false)
const foot = ref(null)

const summary = computed(() => {
  const count = (status) => props.documents.filter((d) => d.status === status).length
  return [
    { status: 'done', n: count('done'), label: (n) => (n > 1 ? 'disponibles' : 'disponible') },
    { status: 'pending', n: count('pending'), label: () => 'en traitement' },
    { status: 'stuck', n: count('stuck'), label: (n) => (n > 1 ? 'bloqués' : 'bloqué') },
  ].filter((s) => s.n > 0)
})

// Le bouton cliqué disparaît : le focus va au contrôle suivant au lieu de retomber en haut de page.
async function ask() {
  confirming.value = true
  await nextTick()
  foot.value?.querySelector('.confirm button')?.focus()
}

async function settle(clear) {
  confirming.value = false
  if (clear) emit('clear')
  await nextTick()
  document.querySelector('.page-head .button-primary')?.focus()
}
</script>

<template>
  <section class="files" aria-labelledby="files-title">
    <div class="page-head">
      <h1 id="files-title">Mes fichiers</h1>
      <button type="button" class="button-primary" @click="$emit('pick')">
        <Upload :size="18" aria-hidden="true" />Déposer des fichiers
      </button>
      <p class="summary">
        <template v-if="summary.length">
          <span v-for="s in summary" :key="s.status" :class="`summary-${s.status}`">{{ s.n }} {{ s.label(s.n) }}</span>
        </template>
        <span v-else>5 Mio par fichier</span>
      </p>
    </div>

    <div v-if="!documents.length" class="empty-drop">
      <p class="empty-title">Glissez vos fichiers ici.</p>
      <button type="button" class="button-secondary" @click="$emit('pick')">Choisir sur mon ordinateur</button>
      <p class="empty-text">
        Ils sont traités puis disponibles au téléchargement. Les fichiers texte se retrouvent aussi par leur contenu.
      </p>
      <p class="empty-legend">Envoyé · Traitement · Disponible · plusieurs fichiers à la fois</p>
    </div>

    <template v-else>
      <table class="file-table">
        <thead>
          <tr>
            <th scope="col" class="col-name">Nom</th>
            <th scope="col" class="col-track">Envoyé · Traitement · Disponible</th>
            <th scope="col" class="col-num">Taille</th>
            <th scope="col" class="col-num">Déposé</th>
            <th scope="col" class="col-action"><span class="visually-hidden">Action</span></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="doc in documents" :key="doc.id" :class="`row-${doc.status}`">
            <td class="cell-name"><FileName :id="doc.id" :title="doc.title" :available="doc.status === 'done'" /></td>
            <td class="cell-track"><FileTrack :doc="doc" :now="now" @retry="$emit('retry', $event)" /></td>
            <td class="col-num cell-meta">{{ formatSize(doc.size) }}</td>
            <td class="col-num cell-meta">{{ formatWhen(doc.uploadedAt, now) }}</td>
            <td class="col-action">
              <a v-if="doc.status === 'done'" class="button-download" :href="fileUrl(doc.id)" download>
                <Download :size="16" aria-hidden="true" />Télécharger<span class="visually-hidden"> {{ doc.title }}</span>
              </a>
            </td>
          </tr>
        </tbody>
      </table>
      <div ref="foot" class="table-foot">
        <span>Fichiers déposés depuis ce navigateur · 50 au plus · 5 Mio par fichier</span>
        <span v-if="confirming" class="confirm">
          Effacer l’historique ? Les fichiers restent disponibles par la recherche.
          <button type="button" class="link-button" @click="settle(true)">Effacer</button>
          <button type="button" class="link-button" @click="settle(false)">Annuler</button>
        </span>
        <button v-else type="button" class="link-button" @click="ask">Effacer l’historique</button>
      </div>
    </template>
  </section>
</template>
