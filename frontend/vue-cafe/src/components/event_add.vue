<template>
  <div class="event-details">
    <header>
      <h2>Nouvel événement</h2>
      <button class="link-button" type="button" @click="$emit('close')">
        Fermer
      </button>
    </header>

    <form class="event-form" @submit.prevent="handleSubmit">
      <div class="form-row">
        <label for="add-event-matiere">Matière</label>
        <input
          id="add-event-matiere"
          v-model="form.matiere"
          type="text"
          placeholder="Nom du cours / événement"
          required
        />
      </div>
      <div class="form-row">
        <label for="add-event-enseignant">Enseignant</label>
        <input
          id="add-event-enseignant"
          v-model="form.enseignant"
          type="text"
          placeholder="Nom de l’enseignant"
        />
      </div>
      <div class="form-row">
        <label for="add-event-start">Début</label>
        <input
          id="add-event-start"
          v-model="form.start"
          type="datetime-local"
          required
        />
      </div>
      <div class="form-row">
        <label for="add-event-end">Fin</label>
        <input
          id="add-event-end"
          v-model="form.end"
          type="datetime-local"
          required
        />
      </div>
      <div class="form-row">
        <label for="add-event-type">Type de cours</label>
        <select id="add-event-type" v-model="form.typeCours">
          <option value="CM">CM</option>
          <option value="TD">TD</option>
          <option value="TP">TP</option>
          <option value="AUTRE">Autre</option>
        </select>
      </div>
      <div class="form-row">
        <label for="add-event-promo">Promo</label>
        <input
          id="add-event-promo"
          v-model="form.promo"
          type="text"
          placeholder="Promo concernée"
          required
        />
      </div>
      <div class="form-row">
        <label for="add-event-location">Salle</label>
        <select id="add-event-location" v-model="form.location">
          <option value="">Choisir une salle</option>
          <option v-for="room in classrooms" :key="room" :value="room">
            {{ room }}
          </option>
        </select>
      </div>
      <div class="form-row">
        <label for="add-event-description">Description</label>
        <textarea
          id="add-event-description"
          v-model="form.description"
          rows="3"
          placeholder="Détails de l’événement"
        />
      </div>

      <div class="form-actions">
        <button class="button primary small" type="submit">
          Créer
        </button>
        <button class="button small" type="button" @click="$emit('close')">
          Annuler
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import type { EventDetail } from '@/api'
import { getClassrooms } from '@/api'

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'create', payload: EventDetail): void
}>()

const classrooms = ref<string[]>([])

const form = reactive({
  matiere: '',
  start: '',
  end: '',
  typeCours: 'CM',
  promo: '',
  enseignant: '',
  description: '',
  location: '',
})

function handleSubmit() {
  emit('create', {
    matiere: form.matiere,
    start: form.start,
    end: form.end,
    type_cours: form.typeCours === 'CM',
    promo: form.promo,
    enseignant: form.enseignant,
    description: form.description,
    location: form.location,
  })
}

async function loadClassrooms() {
  try {
    const data = await getClassrooms()
    const rooms = Array.isArray(data) ? data : []
    classrooms.value = rooms
      .map((room: any) => room?.name ?? room?.label ?? room)
      .filter(Boolean)
  } catch (err) {
    console.error('Unable to load classrooms', err)
    classrooms.value = []
  }
}

onMounted(() => {
  loadClassrooms()
})

watch(() => form.start, (value) => {
  if (!value) {
    return
  }
  const startDate = new Date(value)
  if (Number.isNaN(startDate.getTime())) {
    return
  }
  const endDate = new Date(startDate.getTime() + (5.25) *3600 * 1000)
  form.end = endDate.toISOString().slice(0, 16)
})
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

.event-form {
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
  padding: 0.65rem 0.85rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(99, 102, 241, 0.25);
  font-size: 1rem;
}

.form-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}
</style>
