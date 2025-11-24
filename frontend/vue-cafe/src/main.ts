import { createApp } from 'vue'
import App from '@/App.vue'
import router from '@/router/index.ts'


//import css
import '@/assets/css/calendar.css'
import '@/assets/css/main.css'
import '@/assets/css/main.css'
import '@fortawesome/fontawesome-free/css/all.min.css'
import '@/assets/css/fontawesome-all.min.css'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'


const vuetify = createVuetify({
  components,
  directives,
})


// Création et montage de l’application
createApp(App).use(router).mount('#app')
// createApp(App).use(vuetify).mount('#app')
