<script setup>
import { ArrowLeft, Download, SearchX } from 'lucide-vue-next'
import { fileUrl } from '../api.js'
import FileName from './FileName.vue'

defineProps({
  query: { type: String, required: true },
  results: { type: Array, default: null }, // null : recherche en cours
  error: { type: String, default: '' },
})
defineEmits(['back'])
</script>

<template>
  <section class="files" aria-labelledby="results-title" :aria-busy="results === null && !error">
    <div class="page-head">
      <div>
        <button type="button" class="link-button back" @click="$emit('back')">
          <ArrowLeft :size="18" aria-hidden="true" />Mes fichiers
        </button>
        <h1 id="results-title">Résultats pour « {{ query }} »</h1>
        <p v-if="results" class="summary">{{ results.length }} {{ results.length > 1 ? 'fichiers' : 'fichier' }}</p>
      </div>
    </div>

    <p v-if="error" class="notice notice-error" role="alert">{{ error }}</p>

    <div v-else-if="results === null" class="file-table skeleton" aria-hidden="true">
      <div v-for="n in 3" :key="n" class="skeleton-row"></div>
    </div>

    <div v-else-if="!results.length" class="empty-drop empty-quiet">
      <SearchX class="empty-icon" :size="44" :stroke-width="1.5" aria-hidden="true" />
      <p class="empty-title">Aucun résultat</p>
      <p class="empty-text">Essayez un autre mot du nom ou du contenu du fichier.</p>
    </div>

    <table v-else class="file-table">
      <thead class="visually-hidden">
        <tr>
          <th scope="col">Nom</th>
          <th scope="col">Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="doc in results" :key="doc.id">
          <td class="cell-name"><FileName :id="doc.id" :title="doc.title" /></td>
          <td class="col-num">
            <a class="button-ghost" :href="fileUrl(doc.id)" download>
              <Download :size="18" aria-hidden="true" />Télécharger<span class="visually-hidden"> {{ doc.title }}</span>
            </a>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
