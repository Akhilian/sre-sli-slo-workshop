<script setup>
import { ref } from 'vue'
import { api, fileUrl } from '../api.js'

const query = ref('')
const results = ref(null) // null : aucune recherche lancée
const searching = ref(false)
const error = ref('')

async function search() {
  if (!query.value.trim() || searching.value) return
  searching.value = true
  error.value = ''
  try {
    // Une réponse vide s'affiche comme telle, même si l'API a masqué une erreur : c'est l'exercice.
    results.value = (await api.search(query.value.trim())).results
  } catch (e) {
    results.value = null
    error.value = `Recherche impossible : ${e.message}`
  } finally {
    searching.value = false
  }
}
</script>

<template>
  <section class="panel">
    <h2>Rechercher</h2>
    <form class="search-row" @submit.prevent="search">
      <input v-model="query" type="search" placeholder="Un mot du titre ou du contenu" aria-label="Recherche" />
      <button type="submit" class="button-primary" :disabled="!query.trim() || searching">
        {{ searching ? 'Recherche…' : 'Rechercher' }}
      </button>
    </form>
    <p v-if="error" class="message-error" role="alert">{{ error }}</p>
    <template v-else-if="results">
      <p v-if="!results.length" class="message-empty">Aucun résultat</p>
      <ul v-else class="list">
        <li v-for="doc in results" :key="doc.id" class="list-item">
          <div class="list-main">
            <span class="doc-id">#{{ doc.id }}</span>
            <a class="doc-title" :href="fileUrl(doc.id)" download>{{ doc.title }}</a>
          </div>
        </li>
      </ul>
    </template>
  </section>
</template>
