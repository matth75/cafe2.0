<template>
  <section class="content">
    <header class="major">
      <h1>Bienvenue {{ userInfo[0] }}</h1>
      <p>Voici les informations liées à votre compte CAFE.</p>
    </header>

    <div v-if="isLoading" class="status info">
      Chargement de vos informations…
    </div>

    <div v-else-if="error" class="status error">
      {{ error }}
    </div>

    <div v-else-if="userInfo" class="profile-card">
      <div class="profile-header">
        <div class="avatar" aria-hidden="true">
          coucou
        </div>
        <div>
          <h2>{{ userInfo[1] }} {{ userInfo[0] }}</h2>
          <p class="muted">{{ userInfo[2]    }}</p>
        </div>
      </div>

      <dl class="profile-details">
        <div class="detail">
          <dt>Identifiant</dt>
          <dd>{{ userInfo[3] }}</dd>
        </div>
        <div class="detail">
          <dt>Rôle</dt>
          <dd>
            <span class="tag">{{ userInfo[4] ? 'Administrateur' : 'élève' }}</span>
            <span class="tag" v-if="userInfo[5]">Administrateur</span>
          </dd>
        </div>
        <div class="detail">
          <dt>Note Kfet</dt>
          <dd>{{ userInfo[6] || '—' }}</dd>
        </div>
      </dl>

      <footer class="profile-actions">
        <RouterLink class="button" to="/calendar">
          Accéder à l'agenda
        </RouterLink>
        <button class="button" type="button" @click="refresh">
          Rafraîchir
        </button>
      </footer>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getUsersInfo } from '@/api'

interface UserProfile {
  login: string
  email: string
  nom: string
  prenom: string
  superuser: boolean
  owner: boolean
  noteKfet: string | null
}

const route = useRoute()
const router = useRouter()

const userInfo = ref<string[]>([])
const token = ref<string | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

token.value = localStorage.getItem('cafe_token')


function requireToken() {
  if (!token.value) {
    error.value = 'Token d’authentification manquant. Veuillez vous reconnecter.'
  }
}

async function fetchProfile() {
  if (!token.value) {
    return
  }
  isLoading.value = true
  error.value = null

  try {
    userInfo.value = await getUsersInfo(token.value)


  } catch (err: unknown) {
    if (
      err &&
      typeof err === 'object' &&
      'response' in err &&
      (err as any).response?.status === 401
    ) {
      error.value = 'Session expirée. Merci de vous reconnecter.'
      localStorage.removeItem('cafe_token')
      router.push({ name: 'login' })
    } else {
      error.value = "Impossible de récupérer vos informations pour le moment."
    }
  } finally {
    isLoading.value = false
  }
}

function refresh() {
  fetchProfile()
}


onMounted(() => {
  requireToken()
  fetchProfile()
})
</script>

<style scoped>
.status {
  padding: 1rem;
  border-radius: 0.75rem;
  margin-bottom: 1.5rem;
}

.status.info {
  background: rgba(52, 152, 219, 0.12);
  color: #2980b9;
}

.status.error {
  background: rgba(192, 57, 43, 0.12);
  color: #c0392b;
}

.profile-card {
  padding: 2rem;
  border-radius: 1rem;
  background: #fff;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6c5ce7, #0984e3);
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 1.5rem;
  font-weight: 700;
}

.muted {
  color: #7f8c8d;
  margin: 0.25rem 0 0;
}

.profile-details {
  display: grid;
  gap: 1.25rem;
  margin: 0;
}

.detail dt {
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: #2c3e50;
}

.detail dd {
  margin: 0;
}

.tag {
  display: inline-flex;
  align-items: center;
  padding: 0.3rem 0.65rem;
  border-radius: 999px;
  background: rgba(46, 204, 113, 0.15);
  color: #27ae60;
  font-size: 0.85rem;
  font-weight: 600;
}

.tag + .tag {
  margin-left: 0.5rem;
}

.profile-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

@media (max-width: 600px) {
  .profile-card {
    padding: 1.25rem;
  }

  .profile-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .profile-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
