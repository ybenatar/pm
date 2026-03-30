// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  srcDir: '.',
  ssr: false,
  devtools: { enabled: false },
  css: ['~/assets/css/main.css'],
})
