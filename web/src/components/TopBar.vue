<script setup>
import { ref, watch } from 'vue'
import { Search, X } from 'lucide-vue-next'

const props = defineProps({ query: { type: String, default: '' } })
const emit = defineEmits(['search', 'clear'])

const text = ref(props.query)
watch(() => props.query, (value) => { text.value = value })

function submit() {
  const q = text.value.trim()
  if (q) emit('search', q)
}

function clear() {
  text.value = ''
  emit('clear')
}
</script>

<template>
  <header class="topbar">
    <a class="brand" href="/" @click.prevent="clear">
      <svg class="brand-mark" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M6 2.5h8.5L19 7v13a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 5 20V4a1.5 1.5 0 0 1 1-1.5Z" />
        <path class="brand-fold" d="M14.5 2.5V7H19" />
        <path class="brand-arrow" d="M12 17.5v-6m0 0-2.75 2.75M12 11.5l2.75 2.75" />
      </svg>
      <span>DocShare</span>
    </a>
    <form class="search" role="search" @submit.prevent="submit">
      <Search class="search-icon" :size="20" aria-hidden="true" />
      <input
        v-model="text"
        type="search"
        name="q"
        placeholder="Rechercher dans DocShare"
        aria-label="Rechercher dans DocShare"
        autocomplete="off"
        @keydown.esc="clear"
      />
      <button v-if="text" type="button" class="search-clear icon-button" aria-label="Effacer la recherche" @click="clear">
        <X :size="18" aria-hidden="true" />
      </button>
    </form>
  </header>
</template>
