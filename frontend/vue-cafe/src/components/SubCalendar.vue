<template>
<section class="info-section">
          <h3 class="section-title">Cocher votre CALE favoris</h3>
          <p class="muted small">
          </p>
          <form class="access-form" @submit.prevent="handleSubmit">
            <label
              v-for="calendar in calendars"
              :key="calendar.value"
              class="checkbox-pill"
              :for="`calendar-${calendar.value}`"
            >
              <input
                :id="`calendar-${calendar.value}`"
                type="radio"
                name="favorite-calendar"
                :value="calendar.value"
                v-model="selectedCalendar"
              >
              <span>{{ calendar.label }}</span>
            </label>
            <button
              class="button primary submit-button"
              type="submit"
              :disabled="!selectedCalendar"
              
            >
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
import { onMounted, ref } from 'vue'
import { getUserCalendars, saveFavoriteCalendar } from '@/api'
import { emitProfileUpdated } from '@/utils/authEvents'

interface CalendarOption {
  value: string
  label: string
}

const calendars = ref<CalendarOption[]>([])
const selectedCalendar = ref<string | null>(null)
const status = ref<'idle' | 'success' | 'error'>('idle')
const statusMessage = ref('')

function normalizeCalendar(
  raw: unknown,
  index: number,
): CalendarOption | null {
  if (!raw) {
    return null
  }

  if (typeof raw === 'string') {
    const value = raw.trim()
    if (!value) return null
    return { value, label: value }
  }

  if (typeof raw === 'object') {
    const input = raw as Record<string, unknown>
    const valueSource =
      input.slug ?? input.id ?? input.value ?? input.code ?? index
    const labelSource =
      input.label ?? input.name ?? input.title ?? String(valueSource)

    const value = String(valueSource ?? index).trim()
    const label = String(labelSource ?? value).trim()

    if (!value || !label) {
      return null
    }

    return {
      value,
      label,
    }
  }

  return null
}

async function loadCalendars() {
  const token = localStorage.getItem('cafe_token')

  if (!token) {
    calendars.value = []
    selectedCalendar.value = null
    status.value = 'error'
    statusMessage.value = 'Session expirée, merci de vous reconnecter.'
    return
  }

  try {
    const payload = await getUserCalendars(token)
    const items = Array.isArray(payload) ? payload : []
    const options = items
      .map((item, index) => normalizeCalendar(item, index))
      .filter((item): item is CalendarOption => Boolean(item))

    calendars.value = options
    selectedCalendar.value = options[0]?.value ?? null

    if (options.length === 0) {
      status.value = 'error'
      statusMessage.value = 'Aucun calendrier disponible pour le moment.'
    } else {
      status.value = 'idle'
      statusMessage.value = ''
    }
  } catch (error) {
    console.error('Impossible de récupérer les calendriers disponibles.', error)
    calendars.value = []
    selectedCalendar.value = null
    status.value = 'error'
    statusMessage.value =
      'Impossible de récupérer la liste des calendriers disponibles.'
  }
}

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
    statusMessage.value = 'Promo sauvegardée.'
    emitProfileUpdated({ promoId: selectedCalendar.value })
  } catch (error) {
    console.error('Impossible de sauvegarder le calendrier favori.', error)
    status.value = 'error'
    statusMessage.value = 'Impossible de sauvegarder le calendrier favori.'
  }
}

onMounted(() => {
  loadCalendars()
})
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
