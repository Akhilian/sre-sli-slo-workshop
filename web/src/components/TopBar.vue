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
    <a class="brand" href="/" @click.prevent="clear">DocShare</a>
    <form class="search" role="search" @submit.prevent="submit">
      <Search class="search-icon" :size="18" aria-hidden="true" />
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
        <X :size="16" aria-hidden="true" />
      </button>
    </form>
  </header>
</template>
