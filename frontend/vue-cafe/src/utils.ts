import { ref } from 'vue'
import { getUsersInfo } from '@/api'
import type { UserProfile } from '@/api'

const isConnected = ref(false)
const isSuperuser = ref(false)
const user = ref<UserProfile | null>(null)

async function syncConnectionStatus(): Promise<boolean> {
  const token = localStorage.getItem('cafe_token')

  if (!token) {
    // Aucun token → pas connecté
    isConnected.value = false
    isSuperuser.value = false
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

    return true
  } catch (err) {
    // Token invalide / API down / etc
    console.error("Erreur syncStatus:", err)

    isConnected.value = false
    isSuperuser.value = false
    user.value = null

    return false
  }
}

export { isConnected, isSuperuser, syncConnectionStatus, user }