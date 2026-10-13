<script setup>
import { CloudUpload } from 'lucide-vue-next'
</script>

<template>
  <div class="drop-overlay" aria-hidden="true">
    <div class="drop-target">
      <CloudUpload :size="56" :stroke-width="1.5" />
      <p>Déposez vos fichiers pour les envoyer</p>
    </div>
  </div>
</template>
