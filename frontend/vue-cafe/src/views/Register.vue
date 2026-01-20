<template>
  <section class="content">
    <header class="major">
      <h1>Inscription</h1>
      <p>Créez votre accès à l'espace CAFE en quelques clics.</p>
    </header>

    <form class="register-form" @submit.prevent="handleSubmit">
      <div class="row gtr-50 gtr-uniform">
        <div class="col-6 col-12-small">
          <label for="login">Identifiant</label>
          <input
            id="login"
            v-model.trim="form.login"
            type="text"
            required
            autocomplete="username"
            placeholder="ex : prenom.nom"
          />
        </div>
        <div class="col-6 col-12-small">
          <label for="email">Adresse e-mail</label>
          <input
            id="email"
            v-model.trim="form.email"
            type="email"
            required
            autocomplete="email"
            placeholder="adresse ens ou pas"
          />
        </div>
        <div class="col-6 col-12-small">
          <label for="prenom">Prénom</label>
          <input
            id="prenom"
            v-model.trim="form.prenom"
            type="text"
            required
            autocomplete="given-name"
          />
        </div>
        <div class="col-6 col-12-small">
          <label for="nom">Nom</label>
          <input
            id="nom"
            v-model.trim="form.nom"
            type="text"
            required
            autocomplete="family-name"
          />
        </div>
        <div class="col-6 col-12-small">
          <label for="birthday">Date de naissance</label>
          <input
            id="birthday"
            v-model="form.birthday"
            type="date"
            required
            autocomplete="bday"
          />
        </div>
        <div class="col-6 col-12-small">
          <label for="noteKfet">Note Kfet (optionnel)</label>
          <input
            id="noteKfet"
            v-model.trim="form.noteKfet"
            type="text"
            placeholder="Oscilloscope"
           />
        </div>
        <div class="col-6 col-12-small">
          <label for="hpwd">Mot de passe</label>
          <input
            id="hpwd"
            v-model="form.hpwd"
            type="password"
            required
            autocomplete="new-password"
            placeholder="Choisissez un mot de passe"
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
            {{ isSubmitting ? 'Création…' : 'Créer le compte' }}
          </button>
        </li>
        <li>
          <button
            type="button"
            class="button"
            @click="resetForm()"
            :disabled="isSubmitting"
          >
            Réinitialiser
          </button>
        </li>
      </ul>
    </form>

    <div
      v-if="feedback && feedback.type == 'success'"
      class="form-feedback"
      :class="feedback.type"
      role="status"
    >
      {{ feedback.message }}
      <RouterLink class="button Button_principal" to="/Login"> Connexion</RouterLink>
  </div>

    <div
      v-else-if="feedback && feedback.type == 'error'"
      class="form-feedback"
      :class="feedback.type"
      role="alert"
    >
      {{ feedback.message }}
    </div>
  </section>

</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { registerUser, type UserProfile } from '@/api'

const form = reactive<UserProfile>({
  login: '',
  email: '',
  nom: '',
  prenom: '',
  hpwd: '',
  superuser: false,
  teacher: false,
  noteKfet: '',
  birthday: '',
  promo_id: ""
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

  return "Impossible de créer le compte pour le moment."
}

function resetForm(clearFeedback = true) {
  form.login = ''
  form.email = ''
  form.nom = ''
  form.prenom = ''
  form.hpwd = ''
  form.superuser = false
  form.teacher = false
  form.noteKfet = ''
  form.birthday = ''
  form.promo_id = false

  if (clearFeedback) {
    feedback.value = null
  }
}

async function handleSubmit() {
  if (isSubmitting.value) return

  isSubmitting.value = true
  feedback.value = null

  try {
    await registerUser({ ...form })
    feedback.value = {
      type: 'success',
      message: 'Compte créé avec succès !',
    }
    resetForm(false)
  } catch (err) {
    feedback.value = {
      type: 'error',
      message: extractErrorMessage(err),
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>


<style scoped>
.register-form {
  margin-top: 2rem;
}

.checkbox-field {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
}

.checkbox-field input[type='checkbox'] {
  margin: 0;
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
  
