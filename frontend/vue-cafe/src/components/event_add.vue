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
        <PromoSelect
          v-model="form.promos"
          :default-value="defaultPromo"
          :multiple="true"
          :auto-select-first="false"
          label="Promos"
          select-id="add-event-promo"
        />
        <p v-if="promoSelectionError" class="hint error">
          {{ promoSelectionError }}
        </p>
      </div>
      <div class="form-row">
        <ClassroomSelect
          v-model="form.location"
          label="Salle"
          select-id="add-event-location"
          :auto-select-first="true"
        />
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
import { computed, reactive, ref, watch } from 'vue'
import type { EventDetail } from '@/api'
import PromoSelect from './PromoSelect.vue'
import ClassroomSelect from './ClassroomSelect.vue'

const props = defineProps<{
  defaultPromo?: string | string[] | null
}>()

const defaultPromo = computed(() => props.defaultPromo ?? null)

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'create', payload: EventDetail): void
}>()

const promoSelectionError = ref<string | null>(null)

const form = reactive({
  matiere: '',
  start: '',
  end: '',
  typeCours: 'CM',
  promos: [] as string[],
  enseignant: '',
  description: '',
  location: '',
})

function handleSubmit() {
  if (!form.promos.length) {
    promoSelectionError.value = 'Sélectionnez au moins une promo.'
    return
  }

  form.promos.forEach((promoSlug) => {
    const payload: EventDetail = {
      matiere: form.matiere,
      start: form.start,
      end: form.end,
      type_cours: form.typeCours,
      infos_sup: [form.description, form.enseignant].filter(Boolean).join(' - ') || undefined,
      classroom_str: form.location || undefined,
      user_id: 0,
      promo_str: promoSlug,
    }
    emit('create', payload)
  })
}

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

watch(
  () => form.promos.slice(),
  () => {
    if (form.promos.length) {
      promoSelectionError.value = null
    }
  },
)
</script>

<style scoped>
.event-details {
  margin-top: 1.25rem;
  padding: 1.1rem 1.25rem;
  border-radius: 0.9rem;
  background: #fff;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.08);
}

.event-details header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.event-form {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.form-row input,
.form-row textarea {
  width: 100%;
  padding: 0.65rem 0.85rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(99, 102, 241, 0.25);
  font-size: 1rem;
}

.hint {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0;
}

.hint.error {
  color: #b91c1c;
}

.form-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  padding-top: 0.25rem;
}
</style>
