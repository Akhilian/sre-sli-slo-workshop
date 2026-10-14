// Annonces pour les lecteurs d'écran : une région aria-live unique, alimentée par l'application.
// Les messages proches sont regroupés : déposer huit fichiers ne doit pas en effacer sept.
import { ref } from 'vue'

export const announcement = ref('')

const pending = []
let timer = null

export function announce(message) {
  pending.push(message)
  clearTimeout(timer)
  timer = setTimeout(() => {
    announcement.value = ''
    const text = pending.splice(0).join('. ')
    // Vider puis réécrire : un message identique au précédent est quand même annoncé.
    setTimeout(() => {
      announcement.value = text
    }, 50)
  }, 400)
}
