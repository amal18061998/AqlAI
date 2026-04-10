import { createRouter, createWebHistory } from 'vue-router'

/**
 * Router Configuration
 * 
 * - Public routes: landing, login, signup
 * - Protected routes: chat, profile (require auth)
 * - Navigation guard checks localStorage for JWT token
 */

const routes = [
  {
    path: '/',
    name: 'landing',
    component: () => import('@/views/LandingPage.vue'),
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { guest: true },
  },
  {
    path: '/signup',
    name: 'signup',
    component: () => import('@/views/SignupView.vue'),
    meta: { guest: true },
  },
  {
    path: '/chat',
    name: 'chat',
    component: () => import('@/views/ChatView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard
router.beforeEach((to, from) => {
  const token = localStorage.getItem('access_token')

  if (to.meta.requiresAuth && !token) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.guest && token) {
    return { name: 'chat' }
  }
})

export default router
