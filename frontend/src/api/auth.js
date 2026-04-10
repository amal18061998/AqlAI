import client from './client'

/**
 * Auth API endpoints.
 * Maps to Django: /api/auth/signup/, /api/auth/login/, etc.
 */

export const authApi = {
  signup(data) {
    return client.post('/auth/signup/', data)
  },

  login(credentials) {
    return client.post('/auth/login/', credentials)
  },

  logout(refreshToken) {
    return client.post('/auth/logout/', { refresh: refreshToken })
  },

  getProfile() {
    return client.get('/auth/me/')
  },

  updateProfile(data) {
    return client.patch('/auth/me/', data)
  },
}
