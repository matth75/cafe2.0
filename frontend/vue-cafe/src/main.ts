import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
//import css
import '@/assets/css/calendar.css'
import '@/assets/css/main.css'

// Import direct des vues principales
import Home from './views/Home.vue'
import Calendar from './views/Calendar.vue'
import Contact from './views/Contact.vue'
//import Kawa from './views/Kawa.vue'


// Configuration du routeur
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: Home },
    { path: '/calendar', name: 'calendar', component: Calendar },
    //{ path: '/kawa', name: 'kawa', component: Kawa },
    { path: '/contact', name: 'contact', component: Contact },
    //{ path: '/stage', name: 'stage', component: Stage },
  ],
})

// Import global de ton CSS principal
import '@/assets/css/main.css'
import '@/assets/css/fontawesome-all.min.css'

// Création et montage de l’application
createApp(App).use(router).mount('#app')
