<template>
  <div class="min-h-screen flex items-center justify-center bg-stone-50 px-4">
    <Navbar />

    <div class="w-full max-w-md animate-fade-up">
      <div class="bg-white rounded-2xl shadow-sm border border-stone-100 p-20">
        <div class="text-center mb-8">
          
                      <div 
            class="w-10 h-10 rounded-xl flex items-center justify-center mx-auto mb-4"
            style="background: rgba(37,99,235,0.12); border: 1px solid rgba(59,130,246,0.3);"
          >
            <img src="@/assets/icons/bot.png" class="w-7 h-7 object-contain" alt="Logo" />
          </div>
          
          <h1 class="text-2xl font-bold text-stone-900" style="font-family: var(--font-display)">
            {{ $t('auth.signup_title') }}
          </h1>
          <p class="mt-1 text-sm text-stone-500">{{ $t('auth.signup_subtitle') }}</p>
        </div>

        <!-- Error -->
        <div v-if="error"
             class="mb-4 p-3 rounded-lg bg-red-50 border border-red-100 text-sm text-red-600">
          {{ error }}
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-stone-700 mb-1">{{ $t('auth.username') }}</label>
            <input v-model="form.username" type="text" :placeholder="$t('auth.username')"
                   class="w-full px-4 py-2.5 rounded-xl border border-stone-200 bg-stone-50 text-sm
                          focus:outline-none focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-400 transition-all" />
          </div>
          <div>
            <label class="block text-sm font-medium text-stone-700 mb-1">{{ $t('auth.email') }}</label>
            <input v-model="form.email" type="email" :placeholder="$t('auth.email')"
                   class="w-full px-4 py-2.5 rounded-xl border border-stone-200 bg-stone-50 text-sm
                          focus:outline-none focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-400 transition-all" />
          </div>
          <div>
            <label class="block text-sm font-medium text-stone-700 mb-1">{{ $t('auth.password') }}</label>
            <input v-model="form.password" type="password" :placeholder="$t('auth.password')"
                   class="w-full px-4 py-2.5 rounded-xl border border-stone-200 bg-stone-50 text-sm
                          focus:outline-none focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-400 transition-all" />
          </div>
          <div>
            <label class="block text-sm font-medium text-stone-700 mb-1">{{ $t('auth.confirm_password') }}</label>
            <input v-model="form.confirmPassword" type="password" :placeholder="$t('auth.confirm_password')"
                   class="w-full px-4 py-2.5 rounded-xl border border-stone-200 bg-stone-50 text-sm
                          focus:outline-none focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-400 transition-all"
                   @keydown.enter="handleSignup" />
          </div>

          <button
            @click="handleSignup"
            :disabled="authStore.loading"
            class="w-full py-2.5 rounded-xl bg-indigo-600 text-white font-semibold text-sm
                   hover:bg-indigo-700 disabled:opacity-50 transition-all cursor-pointer
                   shadow-sm shadow-indigo-600/20"
          >
            <LoadingSpinner v-if="authStore.loading" size="sm" container-class="py-0.5" />
            <span v-else>{{ $t('auth.submit_signup') }}</span>
          </button>
        </div>

        <p class="mt-6 text-center text-sm text-stone-500">
          {{ $t('auth.has_account') }}
          <router-link to="/login" class="text-indigo-600 font-medium hover:underline">
            {{ $t('nav.login') }}
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import Navbar from '@/components/layout/Navbar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()
const error = ref('')

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

async function handleSignup() {
  error.value = ''
  if (!form.username || !form.email || !form.password) {
    error.value = t('auth.error_required')
    return
  }
  if (form.password !== form.confirmPassword) {
    error.value = t('auth.error_mismatch')
    return
  }
  try {
    await authStore.signup({
      username: form.username,
      email: form.email,
      password: form.password,
    })
    router.push('/chat')
  } catch (err) {
    error.value = authStore.error || t('common.error')
  }
}
</script>
