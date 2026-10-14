<script setup>
import { computed } from 'vue'
import { formatDuration } from '../format.js'

// Le trajet d'un fichier en trois cases : Envoyé, Traitement, Disponible.
// L'écran montre ce que ressent l'utilisateur, pas un chronomètre de fraîcheur.
const props = defineProps({
  doc: { type: Object, required: true },
  now: { type: Number, required: true },
})
defineEmits(['retry'])

const cells = computed(() => ({
  pending: ['passed', 'current', 'todo'],
  stuck: ['passed', 'stuck', 'todo'],
  done: ['passed', 'passed', 'passed'],
})[props.doc.status])

const label = computed(() => {
  if (props.doc.status === 'done') return 'Disponible'
  if (props.doc.status === 'stuck') return 'Bloqué en traitement'
  return `En traitement depuis ${formatDuration(props.now - props.doc.uploadedAt)}`
})
</script>

<template>
  <div :class="['track', `track-${doc.status}`]">
    <span class="cells" aria-hidden="true">
      <i v-for="(cell, n) in cells" :key="n" :class="['cell', `cell-${cell}`]"></i>
    </span>
    <span class="track-text"><span class="visually-hidden">État : </span>{{ label }}</span>
    <button v-if="doc.status === 'stuck'" type="button" class="link-button" @click="$emit('retry', doc.id)">
      Vérifier à nouveau
    </button>
  </div>
</template>
