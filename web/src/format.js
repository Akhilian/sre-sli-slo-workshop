// Mise en forme des tailles, dates et types de fichiers, en français.

const UNITS = ['o', 'Ko', 'Mo', 'Go']

export function formatSize(bytes) {
  if (bytes == null) return '—'
  let value = bytes
  let unit = 0
  while (value >= 1024 && unit < UNITS.length - 1) {
    value /= 1024
    unit++
  }
  const digits = unit === 0 || value >= 10 ? 0 : 1
  return `${value.toLocaleString('fr-FR', { maximumFractionDigits: digits })} ${UNITS[unit]}`
}

const relative = new Intl.RelativeTimeFormat('fr', { numeric: 'auto' })
const clock = new Intl.DateTimeFormat('fr-FR', { hour: '2-digit', minute: '2-digit' })

export function formatWhen(timestamp, now) {
  const seconds = Math.round((now - timestamp) / 1000)
  if (seconds < 45) return 'à l’instant'
  if (seconds < 3600) return relative.format(-Math.round(seconds / 60), 'minute')
  return clock.format(timestamp)
}

export function formatDuration(ms) {
  const seconds = Math.max(0, Math.round(ms / 1000))
  return seconds < 60 ? `${seconds} s` : `${Math.floor(seconds / 60)} min ${String(seconds % 60).padStart(2, '0')} s`
}

const TEXT = /\.(txt|md|csv|json)$/i
const IMAGE = /\.(png|jpe?g|gif|webp|svg)$/i

export function fileKind(name) {
  if (TEXT.test(name)) return 'text'
  if (IMAGE.test(name)) return 'image'
  return 'other'
}
