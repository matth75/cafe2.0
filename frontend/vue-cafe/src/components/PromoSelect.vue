<template>
  <div class="promo-selector">
    <label v-if="labelText" :for="selectId">{{ labelText }}</label>

    <div
      v-if="isMultiple"
      class="promo-scroll"
      role="group"
      :aria-labelledby="labelText ? selectId : undefined"
    >
      <p class="hint" v-if="status === 'loading'">Chargement…</p>
      <template v-else-if="promoOptions.length">
        <label
          v-for="option in promoOptions"
          :key="option.value"
          class="promo-option"
          :class="{ selected: selectedArray.includes(option.value) }"
        >
          <input
            type="checkbox"
            :value="option.value"
            v-model="selectedArray"
          />
          <span>{{ option.label }}</span>
        </label>
      </template>
      <p class="hint" v-else>Aucune promo disponible.</p>
    </div>

    <template v-else>
      <select
        :id="selectId"
        v-model="selectedSingle"
        :disabled="status === 'loading' || promoOptions.length === 0"
      >
        <option value="" disabled>
          {{ status === 'loading' ? 'Chargement…' : placeholder }}
        </option>
        <option
          v-for="option in promoOptions"
          :key="option.value"
          :value="option.value"
        >
          {{ option.label }}
        </option>
      </select>
    </template>

    <p v-if="statusMessage" :class="['status-banner', status]">
      {{ statusMessage }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { getUserCalendars } from '@/api'

interface PromoOption {
  value: string
  label: string
}

type Status = 'idle' | 'loading' | 'error'

const props = defineProps<{
  modelValue?: string | string[] | null
  defaultValue?: string | string[] | null
  placeholder?: string
  label?: string
  selectId?: string
  autoSelectFirst?: boolean
  multiple?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | string[]): void
  (e: 'status-change', payload: { status: Status; message: string }): void
  (e: 'loaded', options: PromoOption[]): void
}>()

const placeholder = computed(() => props.placeholder ?? 'Sélectionnez une promo')
const labelText = computed(() => props.label ?? '')
const selectId = computed(() => props.selectId ?? 'promo-select')
const autoSelectFirst = computed(() => props.autoSelectFirst ?? true)
const isMultiple = computed(() => props.multiple ?? false)

const promoOptions = ref<PromoOption[]>([])
const status = ref<Status>('idle')
const statusMessage = ref('')
const internalValue = ref<string | string[]>(isMultiple.value ? [] : '')

function toArray(value: string | string[] | null | undefined): string[] {
  if (Array.isArray(value)) {
    return value.map((v) => String(v)).filter(Boolean)
  }
  if (value === null || value === undefined) return []
  const casted = String(value).trim()
  return casted ? [casted] : []
}

function setStatus(nextStatus: Status, message = '') {
  statusMessage.value = message
  status.value = nextStatus
}

function syncFromModel(value: string | string[] | null | undefined) {
  if (isMultiple.value) {
    internalValue.value = toArray(value)
  } else {
    const casted = Array.isArray(value) ? value[0] : value
    internalValue.value = casted ? String(casted) : ''
  }
}

watch(
  () => props.modelValue,
  (value) => {
    syncFromModel(value)
  },
)

const selectedArray = computed<string[]>({
  get() {
    return Array.isArray(internalValue.value) ? internalValue.value : []
  },
  set(value: string[]) {
    internalValue.value = value
  },
})

const selectedSingle = computed<string>({
  get() {
    return typeof internalValue.value === 'string'
      ? internalValue.value
      : internalValue.value[0] ?? ''
  },
  set(value: string) {
    internalValue.value = value
  },
})

watch(internalValue, (value) => {
  if (isMultiple.value) {
    emit('update:modelValue', Array.isArray(value) ? value : toArray(value))
  } else {
    emit('update:modelValue', typeof value === 'string' ? value : value[0] ?? '')
  }
})

watch(status, () => {
  emit('status-change', { status: status.value, message: statusMessage.value })
})

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

function ensureDefaultOptionPresent() {
  const defaults = toArray(props.defaultValue)
  defaults.forEach((value) => {
    if (!value) return
    const exists = promoOptions.value.some((option) => option.value === value)
    if (!exists) {
      promoOptions.value.unshift({ value, label: value })
    }
  })
}

function applyDefaults() {
  const availableValues = new Set(promoOptions.value.map((option) => option.value))
  if (isMultiple.value) {
    const base = toArray(props.modelValue ?? internalValue.value)
    const defaults = toArray(props.defaultValue)
    const candidates = [...defaults, ...base].filter(Boolean)
    const filtered = candidates.filter((value) => availableValues.has(value) || defaults.includes(value))
    let next = filtered

    if (!next.length && autoSelectFirst.value && promoOptions.value[0]) {
      next = [promoOptions.value[0].value]
    }

    internalValue.value = next
  } else {
    const raw = props.modelValue ?? internalValue.value ?? props.defaultValue ?? ''
    const candidate = Array.isArray(raw) ? raw[0] : raw
    let next = candidate ? String(candidate) : ''

    if (!availableValues.has(next)) {
      next = ''
    }

    if (!next && autoSelectFirst.value && promoOptions.value[0]) {
      next = promoOptions.value[0].value
    }

    internalValue.value = next
  }
}

async function loadPromos() {
  setStatus('loading', '')

  const token = localStorage.getItem('cafe_token') ?? undefined
  if (!token) {
    promoOptions.value = []
    internalValue.value = isMultiple.value ? [] : ''
    setStatus('error', 'Session expirée, merci de vous reconnecter.')
    return
  }

  try {
    const payload = await getUserCalendars(token)
    const items = Array.isArray(payload) ? payload : []
    const normalized = items
      .map((item, index) => normalizeOption(item, index))
      .filter((option): option is PromoOption => Boolean(option))

    promoOptions.value = normalized
    ensureDefaultOptionPresent()
    applyDefaults()
    emit('loaded', promoOptions.value)

    if (!promoOptions.value.length) {
      internalValue.value = isMultiple.value ? [] : ''
      setStatus('error', 'Aucune promo disponible pour le moment.')
      return
    }

    setStatus('idle', '')
  } catch (error) {
    console.error('Impossible de récupérer les promos disponibles', error)
    promoOptions.value = []
    internalValue.value = isMultiple.value ? [] : ''
    setStatus('error', 'Impossible de récupérer la liste des promos disponibles.')
  }
}

onMounted(() => {
  syncFromModel(props.modelValue)
  loadPromos()
})

defineExpose({ reload: loadPromos })
</script>

<style scoped>
.promo-selector {
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

.promo-scroll {
  max-height: 12rem;
  overflow-y: auto;
  padding: 0.5rem;
  border-radius: 0.75rem;
  border: 1px solid rgba(99, 102, 241, 0.25);
  background: #fff;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.promo-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0.5rem;
  border-radius: 0.5rem;
  transition: background 0.2s ease;
}

.promo-option:hover {
  background: rgba(99, 102, 241, 0.08);
}

.promo-option.selected {
  background: rgba(99, 102, 241, 0.14);
  border: 1px solid rgba(99, 102, 241, 0.6);
  font-weight: 600;
}

.promo-option input {
  accent-color: #6366f1;
}

.hint {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0.35rem 0 0;
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
</style>
