<template>
  <section class="content">
    <header class="major">
      <h1>Connexion</h1>
      <p>Identifiez-vous pour accéder à votre espace CAFE.</p>
    </header>

    <form class="login-form" @submit.prevent="handleSubmit">
      <div class="row gtr-50 gtr-uniform">
        <div class="col-12">
          <label for="login">Identifiant</label>
          <input
            id="login"
            v-model.trim="form.login"
            type="text"
            required
            autocomplete="username"
            placeholder="ex : prenom.nom"
          />
        </div>

        <div class="col-12">
          <label for="password">Mot de passe</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            required
            autocomplete="current-password"
            placeholder="Votre mot de passe"
          />
        </div>
      </div>
      <p> </p>
      <ul class="actions">
        <li>
          <button
            type="submit"
            class="button primary"
            :disabled="isSubmitting"
          >
            {{ isSubmitting ? 'Connexion…' : 'Se connecter' }}
          </button>
        </li>
      </ul>
    </form>

    <p
      v-if="feedback"
      class="form-feedback"
      :class="feedback.type"
      role="status"
    >
      {{ feedback.message }}
    </p>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { loginUser, getUsersInfo, mapApiUser } from '@/api'
import { emitAuthEvent } from '@/utils/authEvents'

interface LoginFormState {
  login: string
  password: string
}

const router = useRouter()
const form = reactive<LoginFormState>({
  login: '',
  password: '',
})
const isSubmitting = ref(false)
const feedback = ref<{ type: 'success' | 'error'; message: string } | null>(
  null,
)

function extractErrorMessage(err: unknown): string {
  if (
    err &&
    typeof err === 'object' &&
    'response' in err &&
    (err as any).response?.data?.detail
  ) {
    return (err as any).response.data.detail
  }

  if (err instanceof Error) {
    return err.message
  }

  return 'Connexion impossible pour le moment.'
}

async function handleSubmit() {
  if (isSubmitting.value) return

  isSubmitting.value = true
  feedback.value = null

  try {
    const { data } = await loginUser({ username: form.login, password: form.password })
    feedback.value = {
      type: 'success',
      message: 'Connexion réussie, redirection…',
    }
    form.password = ''
    const token = data.access_token
    const userInfo = await getUsersInfo(token)
    localStorage.setItem('cafe_token', token)
    const profile =
      Array.isArray(userInfo) && userInfo.length > 0 ? userInfo[0] : userInfo
    const normalizedProfile = profile ? mapApiUser(profile) : null
    localStorage.setItem(
      'cafe_superuser',
      normalizedProfile?.superuser ? 'true' : 'false',
    )
    emitAuthEvent({
      token,
      superuser: normalizedProfile?.superuser ?? false,
    })
    const identifier = profile?.login ?? 'profil'
    await router.push({ name: 'user-detail', params: { id: identifier } })


  } catch (err) {
    feedback.value = {
      type: 'error',
      message: extractErrorMessage(err),
    }
    localStorage.removeItem('cafe_superuser')
    emitAuthEvent({ token: null, superuser: false })
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.login-form {
  margin-top: 2rem;
}

.form-feedback {
  margin-top: 1.5rem;
  font-weight: 600;
}

.form-feedback.success {
  color: #2ecc71;
}

.form-feedback.error {
  color: #c0392b;
}
</style>
