<template>
  <div class="min-h-screen bg-stone-50">
    <Navbar />

    <div class="max-w-2xl mx-auto px-4 pt-24 pb-16">
      <h1 class="text-2xl font-bold text-stone-900 mb-8" style="font-family: var(--font-display)">
        {{ $t('profile.title') }}
      </h1>

      <LoadingSpinner v-if="!authStore.currentUser" size="lg" container-class="py-20" />

      <template v-else>
        <!-- User card -->
        <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-6 mb-6">
          <div class="flex items-center gap-4 mb-6">
            <div class="w-14 h-14 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600
                        flex items-center justify-center text-white text-xl font-bold shadow-lg shadow-indigo-500/20">
              {{ authStore.currentUser.username?.charAt(0).toUpperCase() }}
            </div>
            <div>
              <h2 class="text-lg font-semibold text-stone-900">{{ authStore.currentUser.username }}</h2>
              <p class="text-sm text-stone-500">{{ authStore.currentUser.email }}</p>
            </div>
          </div>

          <!-- Stats grid -->
          <div class="grid grid-cols-3 gap-4">
            <div class="text-center p-3 rounded-xl bg-stone-50">
              <p class="text-2xl font-bold text-indigo-600">{{ stats.totalChats }}</p>
              <p class="text-xs text-stone-500 mt-1">{{ $t('profile.total_chats') }}</p>
            </div>
            <div class="text-center p-3 rounded-xl bg-stone-50">
              <p class="text-2xl font-bold text-indigo-600">{{ stats.totalMessages }}</p>
              <p class="text-xs text-stone-500 mt-1">{{ $t('profile.total_messages') }}</p>
            </div>
            <div class="text-center p-3 rounded-xl bg-stone-50">
              <p class="text-sm font-semibold text-indigo-600">{{ memberSince }}</p>
              <p class="text-xs text-stone-500 mt-1">{{ $t('profile.member_since') }}</p>
            </div>
          </div>
        </div>

        <!-- AI Summary -->
        <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-6 mb-6">
          <div class="flex items-center gap-2 mb-4">
            <div class="w-8 h-8 rounded-lg bg-purple-50 flex items-center justify-center">
              <svg class="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
              </svg>
            </div>
            <h3 class="text-base font-semibold text-stone-900">{{ $t('profile.summary_title') }}</h3>
          </div>
          <p class="text-sm text-stone-600 leading-relaxed">
            {{ authStore.currentUser.ai_summary || $t('profile.summary_empty') }}
          </p>
        </div>

        <!-- Language preference -->
        <!-- <div class="bg-white rounded-2xl border border-stone-100 shadow-sm p-6">
          <h3 class="text-base font-semibold text-stone-900 mb-4">{{ $t('profile.language_pref') }}</h3>
          <div class="flex gap-3">
            <button
              v-for="lang in languages"
              :key="lang.code"
              @click="switchLanguage(lang.code)"
              class="flex-1 py-3 rounded-xl border text-sm font-medium transition-all cursor-pointer"
              :class="currentLang === lang.code
                ? 'border-indigo-300 bg-indigo-50 text-indigo-700'
                : 'border-stone-200 hover:bg-stone-50 text-stone-600'"
            >
              <span class="text-lg">{{ lang.flag }}</span>
              <span class="block mt-1">{{ lang.label }}</span>
            </button>
          </div>
        </div> -->
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import Navbar from '@/components/layout/Navbar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

const { locale } = useI18n()
const authStore = useAuthStore()
const chatStore = useChatStore()

const currentLang = computed(() => locale.value)

const languages = [
  { code: 'en', label: 'English', flag: '🇬🇧' },
  { code: 'ar', label: 'العربية', flag: '🇸🇦' },
]

const stats = computed(() => ({
  totalChats: chatStore.conversations.length,
  totalMessages: chatStore.conversations.reduce((sum, c) => sum + (c.message_count || 0), 0),
}))

const memberSince = computed(() => {
  const d = authStore.currentUser?.date_joined
  if (!d) return '—'
  return new Date(d).toLocaleDateString(undefined, { month: 'short', year: 'numeric' })
})

function switchLanguage(lang) {
  locale.value = lang
  localStorage.setItem('locale', lang)
  document.documentElement.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr')
  document.documentElement.setAttribute('lang', lang)
  authStore.updateLanguage(lang)
}
</script>
