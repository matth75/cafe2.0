<template>
  <div class="classroom-selector">
    <label v-if="labelText" :for="selectId">{{ labelText }}</label>

    <select
      :id="selectId"
      v-model="internalValue"
      :disabled="status === 'loading' || options.length === 0"
    >
      <option value="" disabled>
        {{ status === 'loading' ? 'Chargement…' : placeholder }}
      </option>
      <option v-for="room in options" :key="room" :value="room">
        {{ room }}
      </option>
    </select>

    <p v-if="statusMessage" :class="['status-banner', status]">
      {{ statusMessage }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { getClassrooms } from '@/api'

type Status = 'idle' | 'loading' | 'error'

const props = defineProps<{
  modelValue?: string | null
  placeholder?: string
  label?: string
  selectId?: string
  autoSelectFirst?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'status-change', payload: { status: Status; message: string }): void
  (e: 'loaded', options: string[]): void
}>()

const placeholder = computed(() => props.placeholder ?? 'Choisir une salle')
const labelText = computed(() => props.label ?? '')
const selectId = computed(() => props.selectId ?? 'classroom-select')
const autoSelectFirst = computed(() => props.autoSelectFirst ?? false)

const options = ref<string[]>([])
const status = ref<Status>('idle')
const statusMessage = ref('')
const internalValue = ref(props.modelValue ?? '')

function setStatus(nextStatus: Status, message = '') {
  statusMessage.value = message
  status.value = nextStatus
}

watch(
  () => props.modelValue,
  (value) => {
    internalValue.value = value ?? ''
  },
)

watch(internalValue, (value) => {
  emit('update:modelValue', value)
})

watch(status, () => {
  emit('status-change', { status: status.value, message: statusMessage.value })
})

async function loadClassrooms() {
  setStatus('loading', '')
  try {
    const data = await getClassrooms()
    const rooms = Array.isArray(data) ? data : []
    const mapped = rooms
      .map((room: any) => room?.name ?? room?.label ?? room)
      .filter((room: unknown): room is string => typeof room === 'string' && room.trim().length > 0)

    options.value = mapped
    emit('loaded', mapped)

    if (!mapped.length) {
      internalValue.value = ''
      setStatus('error', 'Aucune salle disponible.')
      return
    }

    const hasCurrent = mapped.includes(internalValue.value)
    if (!hasCurrent && autoSelectFirst.value && mapped[0]) {
      internalValue.value = mapped[0]
    }

    setStatus('idle', '')
  } catch (err) {
    console.error('Unable to load classrooms', err)
    options.value = []
    internalValue.value = ''
    setStatus('error', 'Impossible de charger la liste des salles.')
  }
}

onMounted(() => {
  loadClassrooms()
})

defineExpose({ reload: loadClassrooms })
</script>

<style scoped>
.classroom-selector {
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
