<template>
<section class="info-section">
          <h3 class="section-title">Cocher votre CALE favoris</h3>
          <p class="muted small">
          </p>
          <form class="access-form" @submit.prevent="handleSubmit">
            <label
              v-for="calendar in calendars"
              :key="calendar"
              class="checkbox-pill"
              :for="`calendar-${calendar}`"
            >
              <input
                :id="`calendar-${calendar}`"
                type="radio"
                name="favorite-calendar"
                :value="calendar"
                v-model="selectedCalendar"
              >
              <span>{{ calendar }}</span>
            </label>
            <button class="button primary submit-button" type="submit">
              Valider
            </button>
          </form>
          <p
            v-if="status !== 'idle'"
            :class="['status-message', status]"
          >
            {{ statusMessage }}
          </p>
</section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { saveFavoriteCalendar } from '@/api'

const calendars = ['Saphire', 'M1 E3A', 'Intranet', 'PSEE'] as const
const selectedCalendar = ref<(typeof calendars)[number] | null>(calendars[0] ?? null)
const status = ref<'idle' | 'success' | 'error'>('idle')
const statusMessage = ref('')

async function handleSubmit() {
  status.value = 'idle'
  statusMessage.value = ''

  if (!selectedCalendar.value) {
    status.value = 'error'
    statusMessage.value = 'Aucun calendrier sélectionné.'
    return
  }

  const token = localStorage.getItem('cafe_token') ?? undefined
  if (!token) {
    status.value = 'error'
    statusMessage.value = 'Session expirée, merci de vous reconnecter.'
    return
  }

  try {
    await saveFavoriteCalendar(selectedCalendar.value, token)
    status.value = 'success'
    statusMessage.value = 'Calendrier favori sauvegardé.'
  } catch (error) {
    console.error('Impossible de sauvegarder le calendrier favori.', error)
    status.value = 'error'
    statusMessage.value = 'Impossible de sauvegarder le calendrier favori.'
  }
}
</script>

<style scoped>
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
  border-color: rgba(99, 102, 241, 0.45);
  box-shadow: 0 12px 22px rgba(76, 81, 191, 0.12);
}

.checkbox-pill input {
  accent-color: #6366f1;
}
.checkbox-pill input:checked + span{
  color: #6e12f0;
}
.status-message {
  margin-top: 1rem;
  font-size: 0.95rem;
}
.status-message.success {
  color: #1d8348;
}
.status-message.error {
  color: #c0392b;
}
</style>
