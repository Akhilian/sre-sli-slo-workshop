// Annonces pour les lecteurs d'écran : une région aria-live unique, alimentée par l'application.
import { ref } from 'vue'

export const announcement = ref('')

export function announce(message) {
  // Vider puis réécrire : un message identique au précédent est quand même annoncé.
  announcement.value = ''
  setTimeout(() => {
    announcement.value = message
  }, 50)
}
