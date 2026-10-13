<script setup>
import { computed } from 'vue'
import { Check, TriangleAlert } from 'lucide-vue-next'
import { formatDuration } from '../format.js'

// Le trajet d'un fichier, comme un suivi de colis : Envoyé, En traitement, Disponible.
const props = defineProps({
  doc: { type: Object, required: true },
  now: { type: Number, required: true },
})
defineEmits(['retry'])

const label = computed(() => {
  const { status, uploadedAt, doneAt } = props.doc
  if (status === 'done') return `Disponible en ${formatDuration(doneAt - uploadedAt)}`
  if (status === 'stuck') return 'Bloqué en traitement'
  return `En traitement · ${formatDuration(props.now - uploadedAt)}`
})
</script>

<template>
  <div :class="['track', `track-${doc.status}`]">
    <ol class="track-steps" aria-hidden="true">
      <li class="step step-done"><Check :size="14" :stroke-width="3" /></li>
      <li class="step step-processing">
        <TriangleAlert v-if="doc.status === 'stuck'" :size="14" :stroke-width="2.5" />
        <Check v-else-if="doc.status === 'done'" :size="14" :stroke-width="3" />
      </li>
      <li class="step step-available"><Check v-if="doc.status === 'done'" :size="14" :stroke-width="3" /></li>
    </ol>
    <p class="track-label">
      <span class="track-text"><span class="visually-hidden">État : </span>{{ label }}</span>
      <button v-if="doc.status === 'stuck'" type="button" class="link-button" @click="$emit('retry', doc.id)">
        Vérifier à nouveau
      </button>
    </p>
  </div>
</template>
