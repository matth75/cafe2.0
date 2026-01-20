<template>
  <section class="content">
    <header class="major">
      <h1>Bienvenue {{user?.prenom}}</h1>
      <p>Voici les informations liées à votre compte CAFE.</p>
    </header>

    <div v-if="isLoading" class="status info">
      Chargement de vos informations…
    </div>

    <div v-else-if="error" class="status error">
      {{ error }}
    </div>

    <div v-else-if="user" class="profile-card">
      <header class="profile-header">
        <UserAvatar :first-name="user.prenom" :last-name="user.nom" />
        <div class="profile-heading">
          <div class="profile-identity">
            <h2>{{ user.prenom }} {{ user.nom }}</h2>
            <p class="muted">{{ user.email }}</p>
          </div>
          <div class="profile-status">
            <span class="tag">{{ user.teacher ? 'Prof' : 'Élève' }}</span>
          </div>
        </div>
      </header>

      <div class="profile-body">
        <section class="info-section">
          <h3 class="section-title">Informations de compte</h3>
          <dl class="profile-details">
            <div class="detail">
              <dt>Identifiant</dt>
              <dd>{{ user.login }}</dd>
            </div>
            <div class="detail">
              <dt>Date de naissance</dt>
              <dd>{{ user.birthday }}</dd>
              
            </div>
            <div v-if="user.noteKfet" class="detail">
              <dt>Note Kfet</dt>
              <dd>{{ user.noteKfet || '—' }}</dd>
            </div>
            <div class="detail">
              <dt>Droits d'accès</dt>
              <dd v-if="user.superuser">Superuser</dd>
              <dd v-else>Standard</dd>
            </div>
            <div class="detail">
              <dt>Promo</dt>
              <dd>
                <button class="link-button" type="button" @click="openCalendarModal">
                  {{ user.promo_id ? user.promo_id : 'Sélectionner un calendrier' }}
                </button>
              </dd>
            </div>
          </dl>
        </section>
      </div>

      <footer class="profile-actions">
        <RouterLink class="button" to="/calendar">
          Accéder à l'agenda
        </RouterLink>
        <button class="button" type="button" @click="refresh">
          Rafraîchir
        </button>
        <button class="button primary" type="button" @click="logout">
          Se déconnecter
        </button>
      </footer>
    </div>


    <Teleport to="body">
      <div
        v-if="isCalendarModalOpen"
        class="modal-backdrop"
        role="dialog"
        aria-modal="true"
        aria-label="Sélection de la Promo "
        @click.self="closeCalendarModal"
      >
        <div class="modal-panel">
          <button
            class="modal-close"
            type="button"
            @click="closeCalendarModal"
            aria-label="Fermer la fenêtre"
          >
            ×
          </button>
          <SubCalendar />
        </div>
      </div>
    </Teleport>
  </section>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getUsersInfo, mapApiUser } from '@/api'
import type { UserProfile } from '@/api'
import SubCalendar from '@/components/SubCalendar.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import {
  emitAuthEvent,
  PROFILE_UPDATED_EVENT,
  type ProfileUpdatedDetail,
} from '@/utils/authEvents'



const route = useRoute()
const router = useRouter()


const user = ref<UserProfile | null>(null)
const token = ref<string | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)
const isCalendarModalOpen = ref(false)

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
    const rawUser = await getUsersInfo(token.value)
    user.value = mapApiUser(rawUser)
    localStorage.setItem(
      'cafe_superuser',
      user.value?.superuser ? 'true' : 'false',
    )
    emitAuthEvent({
      token: token.value,
      superuser: !!user.value?.superuser,
    })


  } catch (err: unknown) {
    if (
      err &&
      typeof err === 'object' &&
      'response' in err &&
      (err as any).response?.status === 401
    ) {
      error.value = 'Session expirée. Merci de vous reconnecter.'
      localStorage.removeItem('cafe_token')
      localStorage.removeItem('cafe_superuser')
      emitAuthEvent({ token: null, superuser: false })
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

function logout() {
  localStorage.removeItem('cafe_token')
  localStorage.removeItem('cafe_superuser')
  emitAuthEvent({ token: null, superuser: false })
  router.push({ name: 'login' })
}

function openCalendarModal() {
  isCalendarModalOpen.value = true
}

function closeCalendarModal() {
  isCalendarModalOpen.value = false
}

function handleSubmit() {
  // placeholder for future handling of platform access update
  isCalendarModalOpen.value = false
}

function handleProfileUpdated(event: Event) {
  if (!user.value) {
    return
  }

  const detail = (event as CustomEvent<ProfileUpdatedDetail>).detail
  if (!detail || typeof detail.promoId === 'undefined') {
    return
  }

  user.value.promo_id = detail.promoId ?? false
}

onMounted(() => {
  requireToken()
  fetchProfile()
  if (typeof window !== 'undefined') {
    window.addEventListener(
      PROFILE_UPDATED_EVENT,
      handleProfileUpdated as EventListener,
    )
  }
})

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener(
      PROFILE_UPDATED_EVENT,
      handleProfileUpdated as EventListener,
    )
  }
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


.profile-heading {
  display: grid;
  gap: 0.75rem;
  width: 100%;
}

.profile-identity h2 {
  margin: 0;
}

.profile-status {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.muted {
  color: #7f8c8d;
  margin: 0.25rem 0 0;
}

.muted.small {
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.profile-body {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.info-section {
  padding: 1.5rem;
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 0.85rem;
  background: #f8fafc;
}

.section-title {
  font-size: 1.05rem;
  margin: 0 0 0.75rem;
  color: #1f2937;
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

.access-form {
  display: grid;
  gap: 0.75rem;
}

.checkbox-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.85rem;
  border-radius: 999px;
  border: 1px solid rgba(99, 102, 241, 0.2);
  background: #fff;
  box-shadow: 0 8px 16px rgba(76, 81, 191, 0.08);
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.checkbox-pill:hover {
  border-color: rgba(212, 33, 33, 0.45);
  box-shadow: 0 12px 22px rgba(76, 81, 191, 0.12);
}

.checkbox-pill input {
  accent-color: #6366f1;
}

.submit-button {
  justify-self: start;
  margin-top: 0.5rem;
}

.link-button {
  background: none;
  border: none;
  color: #1f7aec;
  font-weight: 600;
  cursor:grab; 
  text-decoration: underline;
}

.link-button:hover {
  color: #1453a3;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  display: grid;
  place-items: center;
  padding: 1.5rem;
  z-index: 1000;
}

.modal-panel {
  background: #fff;
  border-radius: 1rem;
  max-width: min(640px, 100%);
  width: 100%;
  padding: 2rem;
  position: relative;
  box-shadow: 0 24px 48px rgba(15, 23, 42, 0.2);
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  border: none;
  background: transparent;
  font-size: 1.75rem;
  line-height: 1;
  cursor: pointer;
  color: #94a3b8;
}

.modal-close:hover {
  color: #1f2937;
}

.profile-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: flex-end;
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

  .profile-actions .button {
    width: 100%;
  }

  .modal-panel {
    padding: 1.5rem;
  }
}
</style>
