<template>
  <div class="min-h-screen flex flex-col">
    <Navbar />

    <!-- HERO -->
    <section class="py-24 bg-gradient-to-br from-indigo-900 to-gray-900 text-white text-center">
      <div class="max-w-4xl mx-auto px-6">
        <h1 class="text-5xl font-bold leading-tight">
          {{ $t('landing.hero_title') }}
        </h1>

        <p class="mt-6 text-lg text-gray-300">
          {{ $t('landing.hero_subtitle') }}
        </p>

        <div class="mt-8 flex justify-center gap-4">
          <router-link
            to="/signup"
            class="px-7 py-3 bg-indigo-600 rounded-lg font-semibold hover:bg-indigo-500 transition"
          >
            {{ $t('landing.cta_start') }}
          </router-link>

          <a
            href="#features"
            class="px-7 py-3 border border-white/20 rounded-lg hover:bg-white/10 transition"
          >
            {{ $t('landing.cta_learn') }}
          </a>
        </div>
      </div>
    </section>

    <!-- FEATURES -->
    <section id="features" class="py-20 bg-white">
      <div class="max-w-6xl mx-auto px-6">
        <div class="grid md:grid-cols-3 gap-8">
          <div
            v-for="(feature, i) in features"
            :key="i"
            class="p-6 rounded-xl border hover:shadow-md transition"
          >
            <component :is="feature.icon" class="w-8 h-8 mb-4 text-indigo-600" />
            <h3 class="text-lg font-semibold mb-2">
              {{ $t(feature.titleKey) }}
            </h3>
            <p class="text-gray-500 text-sm">
              {{ $t(feature.descKey) }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ABOUT -->
    <section class="py-20 bg-gray-50 text-center">
      <div class="max-w-3xl mx-auto px-6">
        <!-- <h2 class="text-3xl font-bold mb-4">
          {{ $t('landing.about_title') }}
        </h2>

        <p class="text-gray-600">
          {{ $t('landing.about_desc') }}
        </p> -->

        <!-- <router-link
          to="/signup"
          class="inline-block mt-6 px-7 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition"
        >
          {{ $t('landing.cta_start') }}
        </router-link> -->
      </div>
    </section>

    <!-- FOOTER -->
    <footer class="py-6 text-center text-sm text-gray-500 bg-white">
      &copy; {{ new Date().getFullYear() }} AqlAI
    </footer>
  </div>
</template>

<script setup>
import { h } from 'vue'
import Navbar from '@/components/layout/Navbar.vue'

// const IconModels = {
//   render: () =>
//     h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
//       h('path', {
//         d: 'M4 4h16v16H4z',
//         'stroke-width': '1.5',
//       }),
//     ]),
// }

// const IconBilingual = {
//   render: () =>
//     h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
//       h('path', {
//         d: 'M3 5h12M12 21l5-10 5 10',
//         'stroke-width': '1.5',
//       }),
//     ]),
// }

// const IconHistory = {
//   render: () =>
//     h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
//       h('path', {
//         d: 'M12 8v4l3 3',
//         'stroke-width': '1.5',
//       }),
//     ]),
// }
const baseProps = {
  fill: 'none',
  stroke: 'currentColor',
  'stroke-width': '1.8',
  'stroke-linecap': 'round',
  'stroke-linejoin': 'round',
  viewBox: '0 0 24 24',
}

const IconModels = {
  render: () =>
    h('svg', baseProps, [
      // layers / stack icon
      h('path', { d: 'M12 3 3 7l9 4 9-4-9-4Z' }),
      h('path', { d: 'M3 12l9 4 9-4' }),
      h('path', { d: 'M3 17l9 4 9-4' }),
    ]),
}

const IconBilingual = {
  render: () =>
    h('svg', baseProps, [
      // left text lines
      h('path', { d: 'M4 6h7M4 10h5M4 14h6' }),
      // right translation / language symbol
      h('path', { d: 'M14 6h6M17 6v12' }),
      h('path', { d: 'M14 18l3-4 3 4' }),
    ]),
}

const IconHistory = {
  render: () =>
    h('svg', baseProps, [
      // clock circle
      h('path', { d: 'M12 8v4l3 2' }),
      h('circle', { cx: '12', cy: '12', r: '9' }),
      // refresh arrow
      h('path', { d: 'M4 12a8 8 0 0 1 2-5' }),
      h('path', { d: 'M4 4v4h4' }),
    ]),
}

const features = [
  {
    titleKey: 'landing.feature_PDF',
    descKey: 'landing.feature_PDF_desc',
    icon: IconModels,
  },
  {
    titleKey: 'landing.feature_bilingual',
    descKey: 'landing.feature_bilingual_desc',
    icon: IconBilingual,
  },
  {
    titleKey: 'landing.feature_history',
    descKey: 'landing.feature_history_desc',
    icon: IconHistory,
  },
]
</script>