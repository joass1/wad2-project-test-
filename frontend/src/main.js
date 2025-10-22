import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './styles/styles.scss'

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'
import VueApexCharts from 'vue3-apexcharts'


const vuetify = createVuetify({
  components, directives,
  theme: {
    defaultTheme: 'sbLight',
    themes: {
      sbLight: {
        dark: false,
        colors: {
          primary: '#6A7A5A',     // Axolotl
          secondary: '#8DAF9B',   // Morning Blue
          accent: '#BED2BA',      // Jet Stream
          info: '#AAC4BC',        // Opal
          warning: '#D7CBB2',     // Dark Vanilla
          background: '#F7F9F8',
          surface: '#FFFFFF',
        }
      },
      sbDark: {
        dark: true,
        colors: {
          primary: '#8DAF9B',
          secondary: '#BED2BA',
          accent: '#D7CBB2',
          background: '#0F1115',
          surface: '#1E2126',
        }
      }
    }
  }
})

createApp(App).use(router).use(vuetify).use(VueApexCharts).component('apexchart', VueApexCharts).mount('#app')
