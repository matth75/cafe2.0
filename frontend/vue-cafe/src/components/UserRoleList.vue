<template>
  <div class="user-role-list">
    <p v-if="error" class="status error">{{ error }}</p>
    <p v-else-if="isLoading" class="status">Chargement…</p>

    <ul v-else>
      <template v-if="role === 'eleve'">
        <li v-for="group in studentGroups" :key="group.key" class="promo-group">
          <div class="promo-header">{{ group.label }}</div>
          <ul class="promo-list">
            <li v-for="person in group.users" :key="person.login" class="user-row">
              <span class="identity">
                <strong>{{ person.nom }} {{ person.prenom }}</strong>
                <span class="meta">{{ person.email }}</span>
                <span class="meta">Utilisateur : {{ person.login }}</span>
              </span>
              <span class="actions">
                <button
                  type="button"
                  class="action-btn secondary"
                  :disabled="isUpdating === person.login"
                  @click="handleSetTeacher(person)"
                >
                  {{ isUpdating === person.login ? 'Mise à jour…' : 'Mettre à prof' }}
                </button>
                <button
                  type="button"
                  class="action-btn suppr"
                  :disabled="isUpdating === person.login"
                  @click="handleRemoveUser(person)"
                >
                  {{ isUpdating === person.login ? 'Suppression…' : 'Supprimer' }}
                </button>
              </span>
            </li>
          </ul>
        </li>
        <li v-if="!studentGroups.length" class="status">Aucun utilisateur trouvé.</li>
      </template>
      <template v-else>
        <li v-for="person in filteredUsers" :key="person.login" class="user-row">
          <span class="identity">
            <strong>{{ person.nom }} {{ person.prenom }}</strong>
            <span class="meta">{{ person.email }}</span>
            <span class="meta">Utilisateur : {{ person.login }}</span>
          </span>
          <span class="actions">
            <button
              v-if="role === 'prof'"
              type="button"
              class="action-btn secondary"
              :disabled="isUpdating === person.login"
              @click="handleUnsetTeacher(person)"
            >
              {{ isUpdating === person.login ? 'Mise à jour…' : 'Retirer prof' }}
            </button>
            <button
              type="button"
              class="action-btn suppr"
              :disabled="isUpdating === person.login"
              @click="handleRemoveUser(person)"
            >
              {{ isUpdating === person.login ? 'Suppression…' : 'Supprimer' }}
            </button>
          </span>
        </li>
        <li v-if="!filteredUsers.length" class="status">Aucun utilisateur trouvé.</li>
      </template>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { getUsersList, mapApiUser, removeUser, setTeacher, unsetTeacher, type UserProfile } from '@/api'

const props = defineProps<{
  role: 'prof' | 'eleve' | 'superuser'
  refreshKey?: number
}>()

const emit = defineEmits<{
  (e: 'refresh'): void
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

const studentGroups = computed(() => {
  const students = users.value.filter((u) => !u.teacher && !u.superuser)
  if (!students.length) return []

  const grouped = new Map<string, { label: string; sortKey: string; users: UserProfile[] }>()
  for (const student of students) {
    const promoKey = getPromoKey(student.promo_id)
    const mapKey = promoKey || '__none__'
    const existing = grouped.get(mapKey)
    if (existing) {
      existing.users.push(student)
    } else {
      grouped.set(mapKey, {
        label: formatPromo(student.promo_id),
        sortKey: promoKey,
        users: [student],
      })
    }
  }

  const groups = Array.from(grouped.entries()).map(([key, value]) => ({
    key,
    ...value,
  }))

  groups.sort((a, b) => comparePromoKeys(a.sortKey, b.sortKey))
  for (const group of groups) {
    group.users.sort(compareUsersByName)
  }

  return groups
})

onMounted(loadUsers)
watch(
  () => props.refreshKey,
  (nextValue, prevValue) => {
    if (nextValue !== undefined && nextValue !== prevValue) {
      loadUsers()
    }
  },
)

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
    await triggerRefresh()
  } catch (err) {
    console.error('Unable to update teacher role', err)
    error.value = "Impossible de mettre à jour les droits."
  } finally {
    isUpdating.value = null
  }
}

async function handleUnsetTeacher(user: UserProfile) {
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
    await unsetTeacher(token, user.login)
    await triggerRefresh()
  } catch (err) {
    console.error('Unable to update teacher role', err)
    error.value = "Impossible de mettre à jour les droits."
  } finally {
    isUpdating.value = null
  }
}

async function handleRemoveUser(user: UserProfile) {
  const token = localStorage.getItem('cafe_token')
  if (!token) {
    error.value = "Token non trouvé."
    return
  }
  if (!user.login) {
    error.value = "Login utilisateur manquant."
    return
  }
  const confirmed = window.confirm(`Supprimer définitivement ${user.nom} ${user.prenom} (${user.login}) ?`)
  if (!confirmed) {
    return
  }
  isUpdating.value = user.login
  error.value = null
  try {
    await removeUser(token, user.login)
    await triggerRefresh()
  } catch (err) {
    console.error('Unable to remove user', err)
    error.value = "Impossible de supprimer l'utilisateur."
  } finally {
    isUpdating.value = null
  }
}

async function triggerRefresh() {
  if (props.refreshKey === undefined) {
    await loadUsers()
  }
  emit('refresh')
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

function getPromoKey(promoId: UserProfile['promo_id']) {
  if (!promoId || promoId === 'false') {
    return ''
  }
  return String(promoId).trim()
}

function formatPromo(promoId: UserProfile['promo_id']) {
  const key = getPromoKey(promoId)
  return key || '—'
}

function comparePromoKeys(a: string, b: string) {
  if (!a && !b) return 0
  if (!a) return 1
  if (!b) return -1
  return a.localeCompare(b, 'fr', { numeric: true })
}

function compareUsersByName(a: UserProfile, b: UserProfile) {
  const nameA = `${a.nom} ${a.prenom}`.trim()
  const nameB = `${b.nom} ${b.prenom}`.trim()
  return nameA.localeCompare(nameB, 'fr')
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

.promo-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.promo-header {
  font-weight: 600;
  color: #374151;
}

.promo-list {
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
