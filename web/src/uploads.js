// Envois en cours : un envoi par fichier, chacun réussit ou échoue seul.
import { computed, reactive } from 'vue'

export function createUploader({ api, onUploaded = () => {}, onFailed = () => {} }) {
  const items = reactive([])
  let nextKey = 0

  function send(files) {
    for (const file of files) {
      const item = reactive({ key: nextKey++, file, status: 'sending', error: '' })
      items.unshift(item)
      start(item)
    }
  }

  async function start(item) {
    item.status = 'sending'
    item.error = ''
    const uploadedAt = Date.now()
    try {
      const { id } = await api.upload(item.file)
      item.status = 'sent'
      onUploaded({ id, title: item.file.name, size: item.file.size, uploadedAt })
    } catch (e) {
      item.status = 'failed'
      item.error = e.message
      onFailed(item)
    }
  }

  function dismiss(item) {
    items.splice(items.indexOf(item), 1)
  }

  // Les échecs restent tant qu'on ne les retire pas : ils attendent un nouvel essai.
  function clearFinished() {
    for (const item of [...items]) {
      if (item.status === 'sent') dismiss(item)
    }
  }

  const counts = computed(() => ({
    sending: items.filter((i) => i.status === 'sending').length,
    sent: items.filter((i) => i.status === 'sent').length,
    failed: items.filter((i) => i.status === 'failed').length,
  }))

  return { items, counts, send, retry: start, dismiss, clearFinished }
}
