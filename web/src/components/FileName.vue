<script setup>
import { computed } from 'vue'
import { fileUrl } from '../api.js'

// Le nom ne mène au fichier qu'une fois celui-ci disponible : un fichier en route ne se télécharge pas.
const props = defineProps({
  id: { type: Number, required: true },
  title: { type: String, required: true },
  available: { type: Boolean, default: true },
})

// Coupure au milieu : si le nom déborde, le début se tronque et l'extension reste visible.
const parts = computed(() => {
  const dot = props.title.lastIndexOf('.')
  return dot > 0 && props.title.length - dot <= 6
    ? { base: props.title.slice(0, dot), ext: props.title.slice(dot) }
    : { base: props.title, ext: '' }
})
</script>

<template>
  <a v-if="available" class="file-name" :href="fileUrl(id)" download tabindex="-1" :title="title">
    <span class="file-base">{{ parts.base }}</span><span>{{ parts.ext }}</span>
  </a>
  <span v-else class="file-name" :title="title">
    <span class="file-base">{{ parts.base }}</span><span>{{ parts.ext }}</span>
  </span>
</template>
