import { createApp } from 'vue'
import App from '@/App.vue'
import router from '@/router/index.ts'


//import css
import '@/assets/css/calendar.css'
import '@/assets/css/main.css'
import '@fortawesome/fontawesome-free/css/all.min.css'
import '@/assets/css/fontawesome-all.min.css'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { VCalendar } from 'vuetify/labs/VCalendar'


const vuetify = createVuetify({
  components: {
    ...components,
    VCalendar,
  },
  directives,
})


// Création et montage de l’application
const app = createApp(App)
app.use(router)
app.use(vuetify)
app.mount('#app')
