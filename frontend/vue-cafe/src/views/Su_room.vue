<template>
  <section class="content">
    <header class="major">
      <h1><RouterLink to="/Superuser">Espace Administrateur</RouterLink></h1>
      <p>Actions reservees aux administrateurs de la plateforme CAFE.</p>
    </header>

    <div class="panel">
      <div class="panel-header">
        <h2>Salles</h2>
        <button class="button small" :disabled="isLoading" @click="loadRooms">
          {{ isLoading ? 'Chargement...' : 'Rafraichir' }}
        </button>
      </div>

      <p v-if="roomsError" class="status-message error">{{ roomsError }}</p>
      <p v-else-if="isLoading" class="status-message">Chargement...</p>
      <p v-else-if="!rooms.length" class="muted">Aucune salle disponible.</p>
      <div v-else class="room-picker">
        <div class="form-row" style="margin-bottom: 1.5rem;">
          <label for="room-picker"></label>
          <select
            id="room-picker"
            v-model="selectedRoomId"
            :disabled="isLoading || !rooms.length"
          >
            <option value="" disabled>Choisir une salle</option>
            <option v-for="room in rooms" :key="room.id" :value="room.id">
              {{ room.name }}
            </option>
          </select>
        </div>

        <div v-if="selectedRoom" class="room-card">
          <div class="room-main">
            <h3>{{ selectedRoom.name }}</h3>
            <dl class="room-meta">
              <div>
                <dt>Type</dt>
                <dd>{{ selectedRoom.roomType }}</dd>
              </div>
              <div>
                <dt>Capacite</dt>
                <dd>{{ selectedRoom.capacity ?? '-' }}</dd>
              </div>
              <div>
                <dt>Lieu</dt>
                <dd>{{ selectedRoom.location }}</dd>
              </div>
            </dl>
          </div>
          <button
            class="button small danger"
            :disabled="deletingRoomId === selectedRoom.id"
            @click="handleDeleteRoom(selectedRoom)"
          >
            {{ deletingRoomId === selectedRoom.id ? 'Suppression...' : 'Supprimer' }}
          </button>
        </div>
      </div>

      <p v-if="actionMessage" :class="['status-message', actionStatus]">
        {{ actionMessage }}
      </p>
    </div>

    <div class="panel">
      <h2>Ajouter une salle</h2>
      <div class="form-row">
        <label for="room-location">Salle *</label>
        <input
          id="room-location"
          v-model="newRoom.location"
          type="text"
          placeholder="Ex: 2Z42"
        />
      </div>
      <div class="form-row">
        <label for="room-type">Type</label>
        <input
          id="room-type"
          v-model="newRoom.room_type"
          type="text"
          placeholder="Ex: CM, Info ..."
        />
      </div>
      <div class="form-row">
        <label for="room-capacity">Capacite</label>
        <input
          id="room-capacity"
          v-model.number="newRoom.capacity"
          type="number"
          min="0"
          placeholder="Ex: 30"
        />
      </div>
      <button class="button" :disabled="isAddingRoom" @click="handleAddRoom">
        {{ isAddingRoom ? 'Ajout...' : 'Ajouter une Salle' }}
      </button>
      <p v-if="addRoomMessage" :class="['status-message', addRoomStatus]">
        {{ addRoomMessage }}
      </p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { addRoom, delRoom, getClassrooms, type struct_room } from '@/api'

interface RoomView {
  id: string
  name: string
  location: string
  roomType: string
  capacity: number | null
}

const rooms = ref<RoomView[]>([])
const isLoading = ref(false)
const roomsError = ref<string | null>(null)
const deletingRoomId = ref<string | null>(null)
const actionMessage = ref<string | null>(null)
const actionStatus = ref<'success' | 'error' | null>(null)
const selectedRoomId = ref('')

const selectedRoom = computed(() => {
  if (!selectedRoomId.value) {
    return null
  }
  return rooms.value.find((room) => room.id === selectedRoomId.value) ?? null
})

const isAddingRoom = ref(false)
const addRoomMessage = ref<string | null>(null)
const addRoomStatus = ref<'success' | 'error' | null>(null)

const newRoom = reactive<struct_room>({
  capacity: 1,
  room_type: 'Autre',
  location: '',
})

function normalizeRooms(payload: unknown): RoomView[] {
  if (!Array.isArray(payload)) {
    return []
  }

  return payload
    .map((item, index): RoomView | null => {
      if (typeof item === 'string') {
        const name = item.trim()
        const safeName = name || `Salle ${index + 1}`
        return {
          id: name || `room-${index}`,
          name: safeName,
          location: name || safeName,
          roomType: 'Autre',
          capacity: null,
        }
      }

      if (!item || typeof item !== 'object') {
        return null
      }

      const raw = item as Record<string, unknown>
      const name = String(raw.name ?? raw.label ?? raw.location ?? raw.id ?? '').trim()
      const location = String(raw.location ?? name).trim()
      const roomType = String(raw.room_type ?? raw.type ?? raw.roomType ?? '').trim() || 'Autre'
      const capacityRaw = raw.capacity ?? raw.capacite ?? raw.capacity_max ?? raw.max_capacity
      const capacity = Number.isFinite(Number(capacityRaw)) ? Number(capacityRaw) : null
      const safeName = name || location || `Salle ${index + 1}`
      const id = location || name || `room-${index}`

      return {
        id,
        name: safeName,
        location: location || safeName,
        roomType,
        capacity,
      }
    })
    .filter((room): room is RoomView => Boolean(room))
}

async function loadRooms() {
  isLoading.value = true
  roomsError.value = null

  try {
    const data = await getClassrooms()
    rooms.value = normalizeRooms(data)
    if (rooms.value.length) {
      const hasSelection = rooms.value.some((room) => room.id === selectedRoomId.value)
      if (!hasSelection) {
        const firstRoom = rooms.value[0]
        if (firstRoom) {
          selectedRoomId.value = firstRoom.id
        }
      }
    } else {
      selectedRoomId.value = ''
    }
  } catch (err) {
    console.error('Unable to load rooms', err)
    roomsError.value = 'Impossible de charger la liste des salles.'
    rooms.value = []
    selectedRoomId.value = ''
  } finally {
    isLoading.value = false
  }
}

async function handleDeleteRoom(room: RoomView) {
  if (deletingRoomId.value) {
    return
  }

  const token = localStorage.getItem('cafe_token') || ''
  if (!token) {
    actionStatus.value = 'error'
    actionMessage.value = 'Authentification requise pour supprimer une salle.'
    return
  }

  if (!room.location) {
    actionStatus.value = 'error'
    actionMessage.value = 'Salle invalide.'
    return
  }

  const confirmed = window.confirm(`Supprimer la salle "${room.name}" ?`)
  if (!confirmed) {
    return
  }

  deletingRoomId.value = room.id
  actionMessage.value = null
  actionStatus.value = null

  try {
    await delRoom(token, room.location)
    actionStatus.value = 'success'
    actionMessage.value = 'Salle supprimee.'
    await loadRooms()
  } catch (err) {
    console.error('Unable to delete room', err)
    actionStatus.value = 'error'
    actionMessage.value = 'Impossible de supprimer la salle.'
  } finally {
    deletingRoomId.value = null
  }
}

async function handleAddRoom() {
  if (isAddingRoom.value) {
    return
  }

  const token = localStorage.getItem('cafe_token') || ''
  if (!token) {
    addRoomStatus.value = 'error'
    addRoomMessage.value = 'Authentification requise pour ajouter une salle.'
    return
  }

  const location = newRoom.location.trim()
  const roomType = newRoom.room_type.trim() || 'Autre'
  let capacity = Number(newRoom.capacity)
  if (Number.isNaN(capacity) || capacity < 0) {
    capacity = 0
  }

  if (!location) {
    addRoomStatus.value = 'error'
    addRoomMessage.value = 'Renseignez une salle.'
    return
  }

  isAddingRoom.value = true
  addRoomMessage.value = null
  addRoomStatus.value = null

  try {
    await addRoom(token, { location, room_type: roomType, capacity })
    addRoomStatus.value = 'success'
    addRoomMessage.value = 'Salle ajoutee.'
    newRoom.location = ''
    newRoom.room_type = 'Autre'
    newRoom.capacity = 0
    await loadRooms()
  } catch (err) {
    console.error('Unable to add room', err)
    addRoomStatus.value = 'error'
    addRoomMessage.value = "Impossible d'ajouter la salle."
  } finally {
    isAddingRoom.value = false
  }
}

onMounted(() => {
  loadRooms()
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
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.room-card {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 1rem;
  border-radius: 0.9rem;
  background: #fff;
  border: 1px solid rgba(1, 119, 139, 0.2);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.04);
}

.room-main h3 {
  margin: 0 0 0.5rem;
}

.room-meta {
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.5rem 1.5rem;
}

.room-meta dt {
  font-weight: 600;
  color: #1f2937;
}

.room-meta dd {
  margin: 0.15rem 0 0;
  color: #4b5563;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.form-row input {
  padding: 0.6rem 0.8rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(99, 102, 241, 0.25);
  font-size: 1rem;
}

.form-row select {
  padding: 0.6rem 0.8rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(99, 102, 241, 0.25);
  font-size: 1rem;
  background: #fff;
}

.status-message {
  margin: 0;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  font-weight: 600;
}

.status-message.success {
  background: rgba(46, 204, 113, 0.12);
  color: #1e824c;
}

.status-message.error {
  background: rgba(220, 38, 38, 0.08);
  color: #b91c1c;
}

.muted {
  color: #6b7280;
}

.button.danger {
  background: #c0392b;
  color: #fff;
}
</style>
