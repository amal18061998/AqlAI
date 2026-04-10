<template>
  <div class="relative inline-block">
    <button
      @click="open = !open"
      class="px-4 py-2 rounded-full text-sm font-medium
             bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/20
             transition-all duration-200 cursor-pointer"
      :class="textClass"
    >
      {{ locale === 'en' ? 'EN' : 'عربي' }}
    </button>

    <!-- Dropdown -->
    <ul
      v-if="open"
      class="absolute mt-2 right-0 w-20 bg-white/10 border border-white/20 rounded-lg shadow-lg backdrop-blur-sm">
      <li
        v-for="lang in otherLanguages"
        :key="lang.code"
        @click="selectLanguage(lang.code)"
        class="px-4 py-2 hover:bg-white/20 cursor-pointer"
      >
        {{ lang.label }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'

defineProps({
  textClass: { type: String, default: 'text-white' },
})

const { locale } = useI18n()
const authStore = useAuthStore()
const open = ref(false)

const otherLanguages = computed(() => {
  return locale.value === 'en'
    ? [{ code: 'ar', label: 'عربي' }]
    : [{ code: 'en', label: 'english' }]
})

function selectLanguage(lang) {
  locale.value = lang
  localStorage.setItem('locale', lang)
  document.documentElement.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr')
  document.documentElement.setAttribute('lang', lang)
  if (authStore.isAuthenticated) {
    authStore.updateLanguage(lang)
  }
  open.value = false
}
</script>