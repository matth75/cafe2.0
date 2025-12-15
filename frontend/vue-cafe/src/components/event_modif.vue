<template>
  <div v-if="event" class="event-details">
    <header>
      <h2>{{ event.title }}</h2>
      <button class="link-button" type="button" @click="emit('close')">
        Fermer
      </button>
    </header>

    <dl>
      <div>
        <dt>Début</dt>
        <dd>{{ formatDate(event.start) }}</dd>
      </div>
      <div>
        <dt>Fin</dt>
        <dd>{{ formatDate(event.end) }}</dd>
      </div>
      <div v-if="event.location">
        <dt>Lieu</dt>
        <dd>{{ event.location }}</dd>
      </div>
      <div v-if="event.description">
        <dt>Description</dt>
        <dd>{{ event.description }}</dd>
      </div>
    </dl>

    <form class="event-form" @submit.prevent="handleSubmit">
      <div class="form-row">
        <label for="event-title">Titre</label>
        <input
          id="event-title"
          v-model="form.title"
          type="text"
          placeholder="Nom de l’événement"
        />
      </div>
      <div class="form-row">
        <label for="event-start">Début</label>
        <input
          id="event-start"
          v-model="form.start"
          type="datetime-local"
        />
      </div>
      <div class="form-row">
        <label for="event-end">Fin</label>
        <input
          id="event-end"
          v-model="form.end"
          type="datetime-local"
        />
      </div>
      <div class="form-row">
        <label for="event-location">Lieu</label>
        <input
          id="event-location"
          v-model="form.location"
          type="text"
          placeholder="Salle / Emplacement"
        />
      </div>
      <div class="form-row">
        <label for="event-description">Description</label>
        <textarea
          id="event-description"
          v-model="form.description"
          rows="3"
          placeholder="Détails de l’événement"
        />
      </div>
      <div class="form-actions">
        <button class="button primary small" type="submit">
          Enregistrer
        </button>
        <button class="button small" type="button" @click="resetForm">
          Réinitialiser
        </button>
        <button type="button" class="button small" @click="handleDelete">
          Supprimer
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import { deleteEvent } from '@/api'


interface EventDetail {
  uid: string
  title: string
  start: Date | null
  end: Date | null
  description?: string
  location?: string
}

const props = defineProps<{
  event: EventDetail | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'deleted'): void
  (e: 'submit', payload: {
    title: string
    start: string
    end: string
    description: string
    location: string
  }): void
}>()

const form = reactive({
  title: '',
  start: '',
  end: '',
  description: '',
  location: '',
})

watch(
  () => props.event,
  (next) => {
    hydrateForm(next ?? null)
  },
  { immediate: true },
)

function hydrateForm(event: EventDetail | null) {
  form.title = event?.title ?? ''
  form.start = event?.start ? toInputDate(event.start) : ''
  form.end = event?.end ? toInputDate(event.end) : ''
  form.description = event?.description ?? ''
  form.location = event?.location ?? ''
}

function toInputDate(date: Date) {
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 16)
}

function formatDate(date: Date | null) {
  if (!date) return '—'
  return date.toLocaleString('fr-FR', {
    weekday: 'long',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function handleSubmit() {
  emit('submit', {
    title: form.title,
    start: form.start,
    end: form.end,
    description: form.description,
    location: form.location,
  })
}

function resetForm() {
  hydrateForm(props.event ?? null)
}

async function handleDelete() {
  const current = props.event
  if (!current?.uid) {
    console.warn('No UID available for deletion')
    return
  }

  const confirmed = window.confirm(`Supprimer l’événement "${current.title}" ?`)
  if (!confirmed) {
    return
  }

  try {
    await deleteEvent(current.uid)
    emit('deleted')
    emit('close')
  } catch (err) {
    console.error('Unable to delete event', err)
  }
}
</script>

<style scoped>
.event-details {
  margin-top: 2rem;
  padding: 1.5rem;
  border-radius: 1rem;
  background: #fff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.event-details header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.event-details dl {
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem 1.5rem;
}

.event-details dt {
  font-weight: 600;
  color: #7f8c8d;
}

.event-details dd {
  margin: 0.15rem 0 0;
}

.event-form {
  margin-top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-row input,
.form-row textarea {
  width: 100%;
  padding: 0.6rem 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(127, 140, 141, 0.5);
  font-size: 1rem;
}

.form-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}
</style>
