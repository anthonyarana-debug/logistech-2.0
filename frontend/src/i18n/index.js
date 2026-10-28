import en from './en.js'

// English is explicit: browser preferences never change the application's default.
export const defaultLocale = 'en'
export const catalogs = Object.freeze({ en: Object.freeze(en) })
export function t(key, values = {}) {
  const message = catalogs[defaultLocale][key]
  if (typeof message !== 'string') throw new Error(`Unknown message key: ${key}`)
  return message.replace(/\{([a-zA-Z][a-zA-Z0-9_]*)\}/g, (_, name) => {
    if (!Object.hasOwn(values, name)) throw new Error(`Missing message argument: ${name}`)
    return String(values[name])
  })
}
export function formatNumber(value) {
  return new Intl.NumberFormat(defaultLocale).format(value)
}
export function formatDate(value) {
  return new Intl.DateTimeFormat(defaultLocale, {
    dateStyle: 'medium', timeStyle: 'short', timeZone: 'America/Lima',
  }).format(new Date(value))
}
export function resultCount(count, boxes) {
  const one = new Intl.PluralRules(defaultLocale).select(count) === 'one'
  return t(one ? 'query_count_one' : 'query_count_other', {
    count: formatNumber(count),
    resource: t(boxes ? (one ? 'box_singular' : 'boxes_2') : (one ? 'category_singular' : 'categories_2')),
  })
}
