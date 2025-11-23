import { createRouter, createWebHistory } from 'vue-router'
import { getUsersInfo } from '@/api'
import HomeView from '@/views/Home.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes : [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/calendar',
    name: 'calendar',
    component: () => import('@/views/Calendar.vue'),
    meta: { requiresAuth: true }, // exemple: page privée
  },
  {
    path: '/contact',
    name: 'contact',
    component: () => import('@/views/Contact.vue'),
  },
  {
    path: '/kawa',
    name: 'kawa',
    component: () => import('@/views/Kawa.vue'),
  },
  {
    path: '/superuser',
    name: 'superuser',
    component: () => import('@/views/Superuser.vue'),
    meta: { requiresSuperuser: true },
  },
  {
    path: '/stage',
    name: 'stage',
    component: () => import('@/views/Stage.vue'),
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/Register.vue'),
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
  },

  // Route dynamique exemple
  {
    path: '/users/:id',
    name: 'user-detail',
    component: () => import('@/views/UserDetail.vue'), 
    props: true,
  },
  // 404 / catch-all
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFound.vue'),
  },
],
})

router.beforeEach(async (to) => {
  if (!to.meta?.requiresSuperuser) {
    return true
  }

  if (typeof window === 'undefined') {
    return { name: 'login' }
  }

  const token = localStorage.getItem('cafe_token')
  if (!token) {
    return {
      name: 'login',
      query: { redirect: to.fullPath },
    }
  }

  try {
    const rawUser = await getUsersInfo(token)
    const profile = Array.isArray(rawUser) && rawUser.length > 0 ? rawUser[0] : rawUser
    const isSuperuser =
      String(profile?.superuser ?? '').toLowerCase() === 'true' ||
      profile?.superuser === true

    if (isSuperuser) {
      return true
    }

    return { name: 'home' }
  } catch (error) {
    console.error('Unable to verify superuser access', error)
    return { name: 'login' }
  }
})

export default router
