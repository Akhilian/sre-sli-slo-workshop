<script setup>
import { onMounted, onUnmounted } from 'vue'
import { api } from './api.js'
import { createTracker } from './tracking.js'
import DocumentList from './components/DocumentList.vue'
import DropZone from './components/DropZone.vue'
import FaultConsole from './components/FaultConsole.vue'
import SearchBox from './components/SearchBox.vue'

// Pupitre des pannes : seulement avec ?admin dans l'URL. Ce n'est pas une sécurité.
const admin = new URLSearchParams(window.location.search).has('admin')

const tracker = createTracker({ api })
onMounted(tracker.start)
onUnmounted(tracker.stop)
</script>

<template>
  <header class="app-header">
    <h1>DocShare</h1>
    <p class="tagline">Déposez des fichiers, suivez leur traitement, retrouvez-les et partagez-les.</p>
  </header>
  <main class="app-main">
    <FaultConsole v-if="admin" class="span-all" />
    <div class="column">
      <DropZone @uploaded="tracker.add" />
      <SearchBox />
    </div>
    <DocumentList
      class="column"
      :documents="tracker.state.documents"
      :now="tracker.state.now"
      @retry="tracker.retry"
      @clear="tracker.clear"
    />
  </main>
</template>
