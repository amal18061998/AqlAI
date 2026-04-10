import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

/**
 * Auth Store (Pinia)
 * 
 * Manages:
 * - JWT access/refresh tokens in localStorage
 * - Current user object (fetched from /api/auth/me/)
 * - Login, signup, logout flows
 * - isAuthenticated computed getter
 */

export const useAuthStore = defineStore('auth', () => {
  // ── State ──
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // ── Getters ──
  const isAuthenticated = computed(() => !!localStorage.getItem('access_token'))
  const currentUser = computed(() => user.value)

  // ── Actions ──
  async function login(credentials) {
    loading.value = true
    error.value = null
    try {
      const { data } = await authApi.login(credentials)
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      await fetchProfile()
    } catch (err) {
      error.value = err.response?.data?.detail || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function signup(formData) {
    loading.value = true
    error.value = null
    try {
      await authApi.signup(formData)
      // Auto-login after signup
      await login({ username: formData.username, password: formData.password })
    } catch (err) {
      error.value = err.response?.data?.detail || 'Signup failed'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  async function logout() {
    try {
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) await authApi.logout(refresh)
    } catch {
      // Ignore logout API errors
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      user.value = null
    }
  }

  async function fetchProfile() {
    try {
      const { data } = await authApi.getProfile()
      user.value = data
    } catch {
      user.value = null
    }
  }

  async function updateLanguage(lang) {
    try {
      await authApi.updateProfile({ language: lang })
      if (user.value) user.value.language = lang
    } catch {
      // Fail silently — language is also saved in localStorage
    }
  }

  // Attempt to restore session on store creation
  async function init() {
    if (isAuthenticated.value) {
      await fetchProfile()
    }
  }

  return {
    user, loading, error,
    isAuthenticated, currentUser,
    login, signup, logout, fetchProfile, updateLanguage, init,
  }
})
