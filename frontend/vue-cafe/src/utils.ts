import { ref } from 'vue'
import { getUsersInfo } from '@/api'
import type { UserProfile } from '@/api'

type RawUser = Record<string, unknown>

const isConnected = ref(false)
const isSuperuser = ref(false)
const isTeacher = ref(false)
const user = ref<UserProfile | null>(null)

async function syncConnectionStatus(): Promise<boolean> {
  const token = localStorage.getItem('cafe_token')

  if (!token) {
    // Aucun token → pas connecté
    isConnected.value = false
    isSuperuser.value = false
    isTeacher.value = false
    user.value = null
    return false
  }

  try {
    // Appel API
    const userInfo = await getUsersInfo(token)

    // Si OK → connecté
    user.value = userInfo
    isConnected.value = true
    isSuperuser.value = !!userInfo.superuser
    isTeacher.value = !!userInfo.teacher

    return true
  } catch (err) {
    // Token invalide / API down / etc
    console.error("Erreur syncStatus:", err)

    isConnected.value = false
    isSuperuser.value = false
    isTeacher.value = false
    user.value = null

    return false
  }
}

function toBool(value: unknown): boolean {
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

export function isSuperuserUser(user: RawUser): boolean {
  const flag = user.superuser ?? user.is_superuser ?? user.isSuperuser
  return toBool(flag)
}

export function isTeacherUser(user: RawUser): boolean {
  const droit = String(user.droit ?? user.role ?? user.right ?? '').toLowerCase()
  if (droit.includes('prof') || droit.includes('enseignant') || droit.includes('teacher')) {
    return true
  }
  const flag = user.teacher ?? user.is_teacher ?? user.isTeacher
  return toBool(flag)
}

export { isConnected, isSuperuser, isTeacher, syncConnectionStatus, user }
