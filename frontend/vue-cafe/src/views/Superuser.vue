<template>
  <section class="content">
    <header class="major">
      <h1>Espace Superuser</h1>
      <p>Actions réservées aux administrateurs de la plateforme CAFE.</p>
    </header>

    <p v-if="error" class="status-message">{{ error }}</p>
    <div style="text-align: center;">
      <RouterLink class="button Button_principal" to="/su_people">Gérer les utilisateurs</RouterLink>
      &nbsp; &nbsp; &nbsp;
      <RouterLink class="button Button_principal" to="/su_cal">Gérer les calendriers</RouterLink>
      &nbsp; &nbsp; &nbsp;
      <RouterLink class="button Button_principal" to="/su_room">Gérer les salles</RouterLink>
    </div>

    </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getUsersList } from '@/api'

type RawUser = Record<string, any>
type UsersResponse = RawUser[] | Record<string, RawUser>

const users = ref<RawUser[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
type SectionKey = 'teachers' | 'students' | 'superusers'
const activeFilter = ref<SectionKey>('teachers')
const filterOptions: Array<{ key: SectionKey; label: string }> = [
  { key: 'teachers', label: 'Professeurs' },
  { key: 'students', label: 'Élèves' },
  { key: 'superusers', label: 'Superusers' },
]

const toBool = (value: unknown): boolean => {
  if (typeof value === 'boolean') {
    return value
  }
  if (typeof value === 'number') {
    return value !== 0
  }
  if (typeof value === 'string') {
    const normalized = value.trim().toLowerCase()
    return normalized === 'true' || normalized === '1' || normalized === 'oui'
  }
  return false
}

const resolveEmail = (user: RawUser): string => {
  const mail = user.mail ?? user.email ?? ''
  const value = String(mail).trim()
  return value || 'Email inconnu'
}

const resolveName = (user: RawUser): string => {
  const nom = user.nom ?? user.last_name ?? ''
  const prenom = user.prenom ?? user.first_name ?? ''
  const fallback = user.login ?? ''

  const fullName = `${prenom} ${nom}`.trim()
  if (fullName) {
    return fullName
  }
  if (fallback) {
    return String(fallback)
  }
  return 'Nom inconnu'
}

const isSuperuser = (user: RawUser): boolean => {
  const flag = user.superuser ?? user.is_superuser ?? user.isSuperuser
  return toBool(flag)
}

const isTeacher = (user: RawUser): boolean => {
  const droit = String(user.droit ?? user.role ?? user.right ?? '').toLowerCase()
  if (droit.includes('prof') || droit.includes('enseignant') || droit.includes('teacher')) {
    return true
  }
  const flag = user.teacher ?? user.is_teacher ?? user.isTeacher
  return toBool(flag)
}

const resolveDroit = (user: RawUser): string => {
  const droit = user.droit ?? user.role ?? user.right
  if (droit) {
    return String(droit)
  }
  if (isSuperuser(user)) {
    return 'superuser'
  }
  if (isTeacher(user)) {
    return 'prof'
  }
  return 'eleve'
}

const teacherUsers = computed(() => users.value.filter((user) => isTeacher(user)))
const superuserUsers = computed(() => users.value.filter((user) => isSuperuser(user)))
const studentUsers = computed(() =>
  users.value.filter((user) => !isTeacher(user) && !isSuperuser(user)),
)
const userSections = computed(() => [
  {
    key: 'teachers' as SectionKey,
    title: 'Professeurs',
    users: teacherUsers.value,
    emptyLabel: 'Aucun professeur trouvé.',
  },
  {
    key: 'students' as SectionKey,
    title: 'Élèves',
    users: studentUsers.value,
    emptyLabel: 'Aucun élève trouvé.',
  },
  {
    key: 'superusers' as SectionKey,
    title: 'Superusers',
    users: superuserUsers.value,
    emptyLabel: 'Aucun superuser trouvé.',
  },
])
const visibleSections = computed(() =>
  userSections.value.filter((section) => section.key === activeFilter.value),
)

onMounted(async () => {
  loading.value = true
  error.value = null

  const token = typeof window !== 'undefined' ? window.localStorage.getItem('cafe_token') : null
  if (!token) {
    error.value = 'Authentification requise pour accéder à la liste des utilisateurs.'
    loading.value = false
    return
  }

  try {
    const data = await getUsersList(token)
    users.value = normalizeUsers(data)
  } catch (err) {
    console.error('Failed to fetch users list', err)
    error.value = 'Impossible de récupérer la liste des utilisateurs.'
  } finally {
    loading.value = false
  }
})

function normalizeUsers(payload: UsersResponse | unknown): RawUser[] {
  if (!payload) {
    return []
  }

  if (Array.isArray(payload)) {
    return payload
  }

  if (typeof payload === 'object') {
    return Object.entries(payload as Record<string, RawUser>).map(([login, user]) => ({
      login,
      ...(user ?? {}),
    }))
  }

  return []
}
</script>

<style scoped>
.status-message {
  margin-top: 1.5rem;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  background: rgba(220, 38, 38, 0.08);
  border: 1px solid rgba(220, 38, 38, 0.24);
  color: #b91c1c;
}

.filter-switch {
  margin-top: 1.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.filter-button {
  padding: 0.5rem 1.1rem;
  border-radius: 999px;
  border: 1px solid rgba(99, 102, 241, 0.35);
  background: #fff;
  color: #4c51bf;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
}

.filter-button:hover {
  background: rgba(99, 102, 241, 0.1);
  box-shadow: 0 10px 18px rgba(76, 81, 191, 0.1);
}

.filter-button.active {
  color: #fff;
  background: #01778b;
  box-shadow: 0 12px 22px rgba(76, 81, 191, 0.24);
}

.cards-grid {
  margin-top: 1.5rem;
  display: grid;
  gap: 1.5rem;
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .cards-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.card {
  padding: 1.5rem;
  border-radius: 1rem;
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.2);
  box-shadow: 0 12px 22px rgba(76, 81, 191, 0.12);
}

.card h2 {
  margin-bottom: 0.75rem;
}

.user-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.user-item {
  padding: 0.75rem;
  border-radius: 0.75rem;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(99, 102, 241, 0.12);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.user-name {
  font-weight: 600;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  font-size: 0.95rem;
  color: #3f3f46;
}

.muted {
  color: #6b7280;
}

.error-text {
  color: #b91c1c;
}
</style>
