<script setup>
import { computed } from 'vue'
import { File, FileImage, FileText } from 'lucide-vue-next'
import { fileUrl } from '../api.js'
import { fileKind } from '../format.js'

const props = defineProps({
  id: { type: Number, required: true },
  title: { type: String, required: true },
})

// Coupure au milieu : le début du nom se tronque, l'extension reste toujours visible.
const parts = computed(() => {
  const dot = props.title.lastIndexOf('.')
  return dot > 0 && props.title.length - dot <= 6
    ? { base: props.title.slice(0, dot), ext: props.title.slice(dot) }
    : { base: props.title, ext: '' }
})

const icon = computed(() => ({ text: FileText, image: FileImage }[fileKind(props.title)] ?? File))
</script>

<template>
  <a class="file-name" :href="fileUrl(id)" download :title="`Télécharger ${title}`">
    <component :is="icon" class="file-icon" :size="22" aria-hidden="true" />
    <span class="file-title"><span class="file-base">{{ parts.base }}</span><span v-if="parts.ext">{{ parts.ext }}</span></span>
  </a>
</template>
