<template>
  <!--
    Navbar: Fixed top bar present on all pages.
    - Transparent on landing page, solid on other pages
    - Shows auth links (login/signup) or user menu (chat/profile/logout)
    - Language toggle always visible
    - Mobile hamburger menu
  -->
  <nav
    class="fixed top-0 inset-x-0 z-50 transition-all duration-300"
    :class="navClasses"
  >
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-2 group">
       <div class="w-10 h-10 rounded-xl flex items-center justify-center transition-transform group-hover:scale-105" 
       style="background: rgba(37,99,235,0.12); border: 1px solid rgba(59,130,246,0.3);">
       <img src="@/assets/icons/bot.png" class="w-7 h-7 object-contain" />

          </div>
          <span class="text-lg font-bold tracking-tight" :class="isLanding ? 'text-white' : 'text-stone-900'">
            {{ $t('app.name') }}
          </span>
        </router-link>

        <!-- Desktop nav -->
        <div class="hidden md:flex items-center gap-2">
          <template v-if="authStore.isAuthenticated">
            <router-link
              to="/chat"
              class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
              :class="linkClass"
            >{{ $t('nav.chat') }}</router-link>
            <router-link
              to="/profile"
              class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
              :class="linkClass"
            >{{ $t('nav.profile') }}</router-link>
            <button
              @click="handleLogout"
              class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors cursor-pointer"
              :class="linkClass"
            >{{ $t('nav.logout') }}</button>
          </template>
          <template v-else>
            <router-link
              to="/login"
              class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
              :class="linkClass"
            >{{ $t('nav.login') }}</router-link>
            <router-link
              to="/signup"
              class="px-4 py-1.5 rounded-lg text-sm font-semibold bg-indigo-600 text-white
                     hover:bg-indigo-700 transition-colors shadow-sm"
            >{{ $t('nav.signup') }}</router-link>
          </template>
          <LanguageToggle :text-class="isLanding ? 'text-white' : 'text-stone-700'" />
        </div>

        <!-- Mobile hamburger -->
        <div class="md:hidden flex items-center gap-2">
          <LanguageToggle :text-class="isLanding ? 'text-white' : 'text-stone-700'" />
          <button
            @click="mobileOpen = !mobileOpen"
            class="p-2 rounded-lg transition-colors cursor-pointer"
            :class="isLanding ? 'text-white hover:bg-white/10' : 'text-stone-700 hover:bg-stone-100'"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="!mobileOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile menu panel -->
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div v-if="mobileOpen" class="md:hidden border-t"
           :class="isLanding ? 'bg-stone-900/95 border-white/10' : 'bg-white border-stone-200'">
        <div class="px-4 py-3 space-y-1">
          <template v-if="authStore.isAuthenticated">
            <router-link @click="mobileOpen=false" to="/chat" class="block px-3 py-2 rounded-lg text-sm" :class="mobileLinkClass">{{ $t('nav.chat') }}</router-link>
            <router-link @click="mobileOpen=false" to="/profile" class="block px-3 py-2 rounded-lg text-sm" :class="mobileLinkClass">{{ $t('nav.profile') }}</router-link>
            <button @click="handleLogout" class="block w-full text-start px-3 py-2 rounded-lg text-sm cursor-pointer" :class="mobileLinkClass">{{ $t('nav.logout') }}</button>
          </template>
          <template v-else>
            <router-link @click="mobileOpen=false" to="/login" class="block px-3 py-2 rounded-lg text-sm" :class="mobileLinkClass">{{ $t('nav.login') }}</router-link>
            <router-link @click="mobileOpen=false" to="/signup" class="block px-3 py-2 rounded-lg text-sm" :class="mobileLinkClass">{{ $t('nav.signup') }}</router-link>
          </template>
        </div>
      </div>
    </transition>
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LanguageToggle from '@/components/common/LanguageToggle.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const mobileOpen = ref(false)

const isLanding = computed(() => route.name === 'landing')

const navClasses = computed(() =>
  isLanding.value
    ? 'bg-transparent'
    : 'bg-white/80 backdrop-blur-md border-b border-stone-200/60 shadow-sm'
)
const linkClass = computed(() =>
  isLanding.value
    ? 'text-white/80 hover:text-white hover:bg-white/10'
    : 'text-stone-600 hover:text-stone-900 hover:bg-stone-100'
)
const mobileLinkClass = computed(() =>
  isLanding.value
    ? 'text-white/80 hover:text-white hover:bg-white/10'
    : 'text-stone-600 hover:text-stone-900 hover:bg-stone-50'
)

async function handleLogout() {
  mobileOpen.value = false
  await authStore.logout()
  router.push('/')
}
</script>
