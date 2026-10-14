<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'
import { Check, ChevronDown, ChevronUp, LoaderCircle, RotateCw, TriangleAlert, X } from 'lucide-vue-next'

// Panneau d'envois ancré en bas à droite, comme dans les gestionnaires de fichiers.
const props = defineProps({
  items: { type: Array, required: true },
  counts: { type: Object, required: true },
})
defineEmits(['retry', 'dismiss', 'close'])

const open = ref(true)
const tray = ref(null)

// Le panneau est fixe : la page réserve sa hauteur pour qu'il ne masque jamais la dernière ligne.
const observer = new ResizeObserver(([entry]) => {
  document.documentElement.style.setProperty('--tray-space', `${entry.target.offsetHeight + 24}px`)
})
watch(tray, (el, previous) => {
  if (previous) observer.unobserve(previous)
  if (el) observer.observe(el)
  else document.documentElement.style.removeProperty('--tray-space')
})
onUnmounted(() => {
  observer.disconnect()
  document.documentElement.style.removeProperty('--tray-space')
})

// Les fichiers envoyés rejoignent « Mes fichiers » : le panneau ne garde que ce qui demande l'attention.
const visible = computed(() => props.items.filter((i) => i.status !== 'sent'))

const title = computed(() => {
  const { sending, sent, failed } = props.counts
  if (sending) return `Envoi de ${sending} ${sending > 1 ? 'fichiers' : 'fichier'}…`
  if (failed) return `${failed} ${failed > 1 ? 'envois ont échoué' : 'envoi a échoué'}`
  return `${sent} ${sent > 1 ? 'fichiers envoyés' : 'fichier envoyé'}`
})

const detail = computed(() => {
  const { sending, sent, failed } = props.counts
  if (!sent || (!sending && !failed)) return ''
  return `${sent} ${sent > 1 ? 'envoyés' : 'envoyé'}`
})
</script>

<template>
  <aside v-if="items.length" ref="tray" :class="['tray', { 'tray-failed': counts.failed && !counts.sending }]" aria-label="Envois">
    <div class="tray-head">
      <p class="tray-title">{{ title }}<span v-if="detail" class="tray-detail"> · {{ detail }}</span></p>
      <button type="button" class="icon-button" :aria-expanded="open" aria-label="Détail des envois" @click="open = !open">
        <ChevronDown v-if="open" :size="20" aria-hidden="true" />
        <ChevronUp v-else :size="20" aria-hidden="true" />
      </button>
      <button
        type="button"
        class="icon-button"
        aria-label="Fermer le panneau des envois"
        :disabled="counts.sending > 0"
        @click="$emit('close')"
      >
        <X :size="20" aria-hidden="true" />
      </button>
    </div>
    <ul v-show="open && visible.length" class="tray-list">
      <li v-for="item in visible" :key="item.key" :class="['tray-item', `tray-${item.status}`]">
        <span class="tray-state" aria-hidden="true">
          <LoaderCircle v-if="item.status === 'sending'" class="spin" :size="18" />
          <Check v-else-if="item.status === 'sent'" :size="18" />
          <TriangleAlert v-else :size="18" />
        </span>
        <span class="tray-body">
          <span class="tray-name">{{ item.file.name }}</span>
          <span v-if="item.status === 'failed'" class="tray-error">{{ item.error }}</span>
        </span>
        <template v-if="item.status === 'failed'">
          <button type="button" class="icon-button" :aria-label="`Réessayer ${item.file.name}`" @click="$emit('retry', item)">
            <RotateCw :size="18" aria-hidden="true" />
          </button>
          <button type="button" class="icon-button" :aria-label="`Retirer ${item.file.name}`" @click="$emit('dismiss', item)">
            <X :size="18" aria-hidden="true" />
          </button>
        </template>
      </li>
    </ul>
  </aside>
</template>
