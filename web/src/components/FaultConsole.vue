<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api } from '../api.js'

// Mêmes pannes que app/adapters/faults.py, avec le SLI que chacune dégrade.
const FAULTS = [
  { name: 'upload_latency', sli: 'Latence', unit: 'secondes', example: 2 },
  { name: 'upload_error_rate', sli: 'Disponibilité', unit: 'proportion de 0 à 1', example: 0.5 },
  { name: 'worker_slow', sli: 'Fraîcheur', unit: 'facteur', example: 10 },
  { name: 'stale_index', sli: 'Qualité', unit: '1 pour activer', example: 1 },
  { name: 'notifier_drop', sli: 'Couverture', unit: 'proportion de 0 à 1', example: 0.2 },
]

const active = ref({})
const drafts = reactive(Object.fromEntries(FAULTS.map((f) => [f.name, f.example])))
const busy = ref(false)
const error = ref('')

async function run(action) {
  busy.value = true
  error.value = ''
  try {
    active.value = await action()
  } catch (e) {
    error.value = e.message
  } finally {
    busy.value = false
  }
}

const refresh = () => run(() => api.faults())
const apply = (name) => run(() => api.setFault(name, Number(drafts[name])))
const stop = (name) => run(() => api.setFault(name, 0))

onMounted(refresh)
</script>

<template>
  <section class="panel panel-admin">
    <div class="panel-header">
      <h2>Pupitre des pannes</h2>
      <button type="button" class="button-quiet" :disabled="busy" @click="refresh">Actualiser</button>
    </div>
    <p class="hint">Réservé à l'animateur. Les pannes s'appliquent immédiatement à toute l'équipe.</p>
    <p v-if="error" class="message-error" role="alert">{{ error }}</p>
    <table class="fault-table">
      <thead>
        <tr>
          <th>Panne</th>
          <th>SLI dégradé</th>
          <th>État</th>
          <th>Valeur</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="fault in FAULTS" :key="fault.name">
          <td><code>{{ fault.name }}</code></td>
          <td>{{ fault.sli }}</td>
          <td>
            <span v-if="active[fault.name]" class="status status-active">Active : {{ active[fault.name] }}</span>
            <span v-else class="status status-off">Coupée</span>
          </td>
          <td>
            <input v-model="drafts[fault.name]" type="number" min="0" step="any" :aria-label="`Valeur de ${fault.name}`" />
            <small class="unit">{{ fault.unit }}</small>
          </td>
          <td class="fault-actions">
            <button type="button" class="button-primary" :disabled="busy" @click="apply(fault.name)">Appliquer</button>
            <button type="button" class="button-quiet" :disabled="busy || !active[fault.name]" @click="stop(fault.name)">Couper</button>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
