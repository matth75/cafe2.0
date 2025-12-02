<template>
  <section class="content">
    <header class="major">
      <h1>Espace Superuser</h1>
      <p>Actions réservées aux administrateurs de la plateforme CAFE.</p>
    </header>

    <div class="panel" style="text-align: center">
      <select id="promo-select" v-model="selectedPromo" :disabled="status === 'loading' || promoOptions.length === 0">
        <option value="" disabled>
          {{ status === 'loading' ? 'Chargement…' : 'Sélectionnez une promo' }}
        </option>
        <option v-for="option in promoOptions" :key="option.value" :value="option.value">
          {{ option.label }}
        </option>
      </select>
      <p v-if="statusMessage" :class="['status-banner', status]">
        {{ statusMessage }}
      </p>
    </div>
    <br>

    <div class="panel" v-if="selectedPromo" style="text-align: center;">
      <div style="display: flex; flex-direction: row; justify-content: center;">
        <button class="csv button">Télécharger .csv {{ selectedPromo }}</button>
        &nbsp; &nbsp; &nbsp;
        <button class="button csv">Upload le .csv {{ selectedPromo }}</button>
      </div>
      <br>
      <h2 style="text-align: left;">Calendrier {{ selectedPromo }}</h2>
      <Calendar_compo :selectedPromo="selectedPromo" />
   
    </div>

  </section>


</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getUserCalendars } from '@/api'
import Calendar_compo from '@/components/Calendar_compo.vue'

interface PromoOption {
  value: string
  label: string
}

const promoOptions = ref<PromoOption[]>([])
const selectedPromo = ref('')
const status = ref<'idle' | 'loading' | 'error'>('idle')
const statusMessage = ref('')

function normalizeOption(raw: unknown, index: number): PromoOption | null {
  if (!raw) return null

  if (typeof raw === 'string') {
    const value = raw.trim()
    if (!value) return null
    return { value, label: value }
  }

  if (typeof raw === 'object') {
    const source = raw as Record<string, unknown>
    const baseValue = source.slug ?? source.id ?? source.value ?? index
    const baseLabel = source.label ?? source.name ?? source.title ?? baseValue
    const value = String(baseValue ?? index).trim()
    const label = String(baseLabel ?? value).trim()
    return value ? { value, label: label || value } : null
  }

  return null
}

async function loadPromos() {
  status.value = 'loading'
  statusMessage.value = ''

  const token = localStorage.getItem('cafe_token') ?? undefined
  if (!token) {
    promoOptions.value = []
    selectedPromo.value = ''
    status.value = 'error'
    statusMessage.value = 'Session expirée, merci de vous reconnecter.'
    return
  }

  try {
    const payload = await getUserCalendars(token)
    const items = Array.isArray(payload) ? payload : []
    const normalized = items
      .map((item, index) => normalizeOption(item, index))
      .filter((option): option is PromoOption => Boolean(option))

    promoOptions.value = normalized
    selectedPromo.value = normalized[0]?.value ?? ''
    status.value = 'idle'
    statusMessage.value = normalized.length
      ? ''
      : 'Aucune promo disponible pour le moment.'
  } catch (error) {
    console.error('Impossible de récupérer les promos disponibles', error)
    promoOptions.value = []
    selectedPromo.value = ''
    status.value = 'error'
    statusMessage.value =
      'Impossible de récupérer la liste des promos disponibles.'
  }
}

onMounted(() => {
  loadPromos()
})
</script>

<style scoped>
.panel {
  margin-top: 2rem;
  padding: 1.5rem;
  border-radius: 1rem;
  background: #01768b1c;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  justify-content: center;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

select {
  padding: 0.65rem 0.85rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(99, 102, 241, 0.25);
  font-size: 1rem;
}

.selection-preview {
  margin: 0;
  font-size: 1rem;
}

.status-banner {
  margin: 0;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-weight: 600;
}

.status-banner.error {
  background: rgba(192, 57, 43, 0.12);
  color: #c0392b;
}

.csv {
  background: #01778b;
  color: white;

}
</style>
