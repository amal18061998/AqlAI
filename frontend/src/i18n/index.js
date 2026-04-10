import { createI18n } from 'vue-i18n'
import en from './en.json'
import ar from './ar.json'

/**
 * i18n configuration using vue-i18n with JSON translation files.
 * 
 * - Reads saved locale from localStorage (persists across sessions)
 * - Falls back to 'en' if nothing saved
 * - Sets document `dir` attribute for RTL support
 */

const savedLocale = localStorage.getItem('locale') || 'en'

const i18n = createI18n({
  legacy: false,            // Use Composition API mode
  locale: savedLocale,
  fallbackLocale: 'en',
  messages: { en, ar },
})

// Apply direction on initial load
document.documentElement.setAttribute('dir', savedLocale === 'ar' ? 'rtl' : 'ltr')
document.documentElement.setAttribute('lang', savedLocale)

export default i18n
