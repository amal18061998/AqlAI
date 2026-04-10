<template>
  <div class="min-h-screen flex items-center justify-center bg-stone-50 px-4">
    <Navbar />

    <div class="w-full max-w-md animate-fade-up">
      <!-- Card -->
      <div class="bg-white rounded-2xl shadow-sm border border-stone-100 p-8">
        <!-- Header -->
        <div class="text-center mb-8">
           <!-- Icon -->
           <div 
            class="w-10 h-10 rounded-xl flex items-center justify-center mx-auto mb-4"
            style="background: rgba(37,99,235,0.12); border: 1px solid rgba(59,130,246,0.3);"
          >
            <img src="@/assets/icons/bot.png" class="w-7 h-7 object-contain" alt="Logo" />
          </div>
          <h1 class="text-2xl font-bold text-stone-900" style="font-family: var(--font-display)">
            {{ $t('auth.login_title') }}
          </h1>
          <p class="mt-1 text-sm text-stone-500">{{ $t('auth.login_subtitle') }}</p>
        </div>

        <!-- Error -->
        <div v-if="authStore.error"
             class="mb-4 p-3 rounded-lg bg-red-50 border border-red-100 text-sm text-red-600">
          {{ authStore.error }}
        </div>

        <!-- Form -->
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-stone-700 mb-1">{{ $t('auth.username') }}</label>
            <input
              v-model="form.username"
              type="text"
              :placeholder="$t('auth.username')"
              class="w-full px-4 py-2.5 rounded-xl border border-stone-200 bg-stone-50
                     text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-400
                     transition-all"
              @keydown.enter="handleLogin"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-stone-700 mb-1">{{ $t('auth.password') }}</label>
            <input
              v-model="form.password"
              type="password"
              :placeholder="$t('auth.password')"
              class="w-full px-4 py-2.5 rounded-xl border border-stone-200 bg-stone-50
                     text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-400
                     transition-all"
              @keydown.enter="handleLogin"
            />
          </div>

          <button
            @click="handleLogin"
            :disabled="authStore.loading"
            class="w-full py-2.5 rounded-xl bg-indigo-600 text-white font-semibold text-sm
                   hover:bg-indigo-700 disabled:opacity-50 transition-all cursor-pointer
                   shadow-sm shadow-indigo-600/20"
          >
            <LoadingSpinner v-if="authStore.loading" size="sm" container-class="py-0.5" />
            <span v-else>{{ $t('auth.submit_login') }}</span>
          </button>
        </div>

        <!-- Signup link -->
        <p class="mt-6 text-center text-sm text-stone-500">
          {{ $t('auth.no_account') }}
          <router-link to="/signup" class="text-indigo-600 font-medium hover:underline">
            {{ $t('nav.signup') }}
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Navbar from '@/components/layout/Navbar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = reactive({ username: '', password: '' })

async function handleLogin() {
  if (!form.username || !form.password) return
  try {
    await authStore.login(form)
    const redirect = route.query.redirect || '/chat'
    router.push(redirect)
  } catch {
    // Error already set in store
  }
}
</script>
