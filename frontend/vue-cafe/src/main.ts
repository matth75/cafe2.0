import { createApp } from 'vue'
import App from '@/App.vue'
import router from '@/router/index.ts'


//import css
import '@/assets/css/calendar.css'
import '@/assets/css/main.css'
import '@/assets/css/main.css'
import '@fortawesome/fontawesome-free/css/all.min.css'
import '@/assets/css/fontawesome-all.min.css'


// Création et montage de l’application
createApp(App).use(router).mount('#app')
