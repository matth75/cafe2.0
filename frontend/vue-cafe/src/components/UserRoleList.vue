<template>
  <div class="user-role-list">
    <p v-if="error" class="status error">{{ error }}</p>
    <p v-else-if="isLoading" class="status">Chargement…</p>

    <ul v-else>
      <li v-for="person in filteredUsers" :key="person.login" class="user-row">
        <span class="identity">
          <strong>{{ person.nom }} {{ person.prenom }}</strong>
          <span class="meta">{{ person.email }}</span>
          <span class="meta">Utilisateur : {{ person.login }}</span>
        </span>
        <span class="actions">
          <button v-if="role === 'superuser'" type="button" class="action-btn secondary" @click="emitRights(person)">Enlever droits</button>
          <button
            v-if="role === 'eleve'"
            type="button"
            class="action-btn secondary"
            :disabled="isUpdating === person.login"
            @click="handleSetTeacher(person)"
          >
            {{ isUpdating === person.login ? 'Mise à jour…' : 'Mettre à prof' }}
          </button>
          <button v-if="role === 'eleve' || role === 'prof'" type="button" class="action-btn secondary" @click="emitRights(person)">Mettre à SuperUser</button>
          <button type="button" class="action-btn suppr" @click="emitDelete(person)">Supprimer</button>
        </span>
      </li>
      <li v-if="!filteredUsers.length" class="status">Aucun utilisateur trouvé.</li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getUsersList, mapApiUser, setTeacher, type UserProfile } from '@/api'

const props = defineProps<{
  role: 'prof' | 'eleve' | 'superuser' 
}>()

const emit = defineEmits<{
  (e: 'delete', user: UserProfile): void
  (e: 'change-rights', user: UserProfile): void
}>()

const isLoading = ref(false)
const error = ref<string | null>(null)
const users = ref<UserProfile[]>([])
const isUpdating = ref<string | null>(null)

const filteredUsers = computed(() => {
  if (!users.value.length) return []
  switch (props.role) {
    case 'prof':
      return users.value.filter((u) => !!u.teacher)
    case 'superuser':
      return users.value.filter((u) => !!u.superuser)
    case 'eleve':
    default:
      return users.value.filter((u) => !u.teacher && !u.superuser)
  }
})

onMounted(loadUsers)

async function loadUsers() {
  isLoading.value = true
  error.value = null
  try {
    const token = localStorage.getItem('cafe_token')
    if (!token) {
      error.value = "Token non trouvé."
      return
    }
    const data = await getUsersList(token)
    users.value = normalizeUsers(data)
  } catch (err) {
    console.error('Unable to load users list', err)
    error.value = "Impossible de charger les utilisateurs."
  } finally {
    isLoading.value = false
  }
}

function emitDelete(user: UserProfile) {
  emit('delete', user)
}

function emitRights(user: UserProfile) {
  emit('change-rights', user)
}

async function handleSetTeacher(user: UserProfile) {
  const token = localStorage.getItem('cafe_token')
  if (!token) {
    error.value = "Token non trouvé."
    return
  }
  if (!user.login) {
    error.value = "Login utilisateur manquant."
    return
  }
  isUpdating.value = user.login
  error.value = null
  try {
    await setTeacher(token, user.login)
    await loadUsers()
  } catch (err) {
    console.error('Unable to update teacher role', err)
    error.value = "Impossible de mettre à jour les droits."
  } finally {
    isUpdating.value = null
  }
}

function normalizeUsers(payload: unknown): UserProfile[] {
  if (!payload) return []

  // Cas simple: tableau direct
  if (Array.isArray(payload)) {
    return payload.map(mapApiUser)
  }

  // Cas { users: [...] }
  if (typeof payload === 'object' && payload !== null) {
    const withUsers = (payload as any).users
    if (Array.isArray(withUsers)) {
      return withUsers.map(mapApiUser)
    }

    // Cas dictionnaire { login: { ...user } }
    const entries = Object.entries(payload as Record<string, any>)
    if (entries.length) {
      return entries.map(([login, user]) => mapApiUser({ login, ...(user ?? {}) }))
    }
  }

  return []
}
</script>

<style scoped>
.user-role-list {
  text-align: left;
}

.status {
  color: #555;
}

.status.error {
  color: #c0392b;
}

ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.user-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
}

.identity {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.meta {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.action-btn {
  border: 1px solid #d1d5db;
  background: #f9fafb;
  color: #374151;
  padding: 0.35rem 0.6rem;
  border-radius: 0.4rem;
  cursor: pointer;
  font-size: 0.9rem;
}

.action-btn.secondary {
  background: #fff;
}

.action-btn:hover {
  background: #eef2ff;
}

.suppr {
  color: #fff;
  background-color: #e74c3c;
}
</style>
