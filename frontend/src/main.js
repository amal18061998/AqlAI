import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import './assets/styles/main.css'

/**
 * App Bootstrap
 *
 * Plugin order matters:
 * 1. Pinia (state management) — stores are used by router guards
 * 2. Router — depends on Pinia for auth checks
 * 3. i18n — provides $t() globally to all components
 */

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)

app.mount('#app')
