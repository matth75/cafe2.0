<template>
  <li v-if="currentUser" class="user-icon">
    <RouterLink
      :to="profileLink"
      aria-label="Accéder à mon profil utilisateur"
      class="avatar-link"
    >
      <UserAvatar
        :first-name="currentUser.prenom"
        :last-name="currentUser.nom"
        :size="40"
      />
    </RouterLink>
  </li>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import UserAvatar from '@/components/UserAvatar.vue'
import { getUsersInfo, mapApiUser } from '@/api'
import type { UserProfile } from '@/api'
import { AUTH_EVENT } from '@/utils/authEvents'

const currentUser = ref<UserProfile | null>(null)
let lastToken: string | null = null
let isLoadingProfile = false

async function loadProfile(force = false) {
  if (typeof window === 'undefined') {
    return
  }

  const token = localStorage.getItem('cafe_token')

  if (!token) {
    currentUser.value = null
    lastToken = null
    return
  }

  if (!force && token === lastToken && currentUser.value) {
    return
  }

  if (isLoadingProfile) {
    return
  }

  isLoadingProfile = true

  try {
    const rawUser = await getUsersInfo(token)
    const source =
      Array.isArray(rawUser) && rawUser.length > 0 ? rawUser[0] : rawUser

    if (source) {
      currentUser.value = mapApiUser(source)
      lastToken = token
    } else {
      currentUser.value = null
      lastToken = null
    }
  } catch (error) {
    console.error('Unable to load user profile for avatar.', error)
    currentUser.value = null
    lastToken = null
  } finally {
    isLoadingProfile = false
  }
}

function handleStorage(event: StorageEvent) {
  if (event.key === 'cafe_token') {
    loadProfile(true)
  }
}

function handleVisibility() {
  if (document.visibilityState === 'visible') {
    loadProfile()
  }
}

function handleAuthEvent() {
  loadProfile(true)
}

onMounted(() => {
  loadProfile()
  window.addEventListener('storage', handleStorage)
  document.addEventListener('visibilitychange', handleVisibility)
  window.addEventListener(AUTH_EVENT, handleAuthEvent as EventListener)
})

onBeforeUnmount(() => {
  window.removeEventListener('storage', handleStorage)
  document.removeEventListener('visibilitychange', handleVisibility)
  window.removeEventListener(AUTH_EVENT, handleAuthEvent as EventListener)
})

const profileLink = computed(() => {
  if (!currentUser.value) {
    return { name: 'login' }
  }

  return {
    name: 'user-detail',
    params: { id: currentUser.value.login || 'profil' },
  }
})
</script>

<style scoped>
.user-icon {
  display: inline-flex;
  align-items: center;
}

.avatar-link {
  display: inline-flex;
  align-items: center;
}
</style>
