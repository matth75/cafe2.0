<template>
  <section class="content">
    <header class="major">

     <h1> <RouterLink to="/Superuser">Espace Superuser</RouterLink> </h1>
      <p>Actions réservées aux administrateurs de la plateforme CAFE.</p>
    </header>

    <div class="panel">
      <h2>Ajouter une salle</h2>
      <div class="form-row">
        <label for="room-location">Salle</label>
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
        <label for="room-capacity">Capacité</label>
        <input
          id="room-capacity"
          v-model.number="newRoom.capacity"
          type="number"
          min="0"
          placeholder="Ex: 30"
        />
      </div>
      <button class="button" :disabled="isAddingRoom" @click="handleAddRoom">
        {{ isAddingRoom ? 'Ajout…' : 'Ajouter une Salle' }}
      </button>
      <p v-if="addRoomMessage" :class="['status-message', addRoomStatus]">
        {{ addRoomMessage }}
      </p>
    </div>

    <div class="panel">
      <ClassroomSelect
        ref="classroomSelectRef"
        v-model="selectedRoom"
        label="Salle"
        select-id="room-select"
      />
    </div>
    <br>
        <div class="panel" v-if="selectedRoom" style="text-align: center;">

      <div style="display: flex; flex-direction: row; justify-content: center;">
        <button class="csv button">Télécharger .csv {{ selectedRoom }}</button>
        &nbsp; &nbsp; &nbsp;
        <button class="button csv">Upload le .csv {{ selectedRoom }}</button>
      </div>
      <br>
      <h2 style="text-align: left;">Calendrier {{ selectedRoom }}</h2>
      <Calendar_compo_SU :selectedPromo="selectedRoom" />
   
    </div>

  </section>


</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { addRoom, type room_type } from '@/api'
import ClassroomSelect from '@/components/ClassroomSelect.vue'

const selectedRoom = ref('')
const classroomSelectRef = ref<{ reload: () => void } | null>(null)
const isAddingRoom = ref(false)
const addRoomMessage = ref<string | null>(null)
const addRoomStatus = ref<'success' | 'error' | null>(null)

const newRoom = reactive<room_type>({
  capacity: 0,
  room_type: '',
  location: '',
})

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
  const roomType = newRoom.room_type.trim()
  const capacity = Number(newRoom.capacity)

  if (!location || !roomType || Number.isNaN(capacity) || capacity <= 0) {
    addRoomStatus.value = 'error'
    addRoomMessage.value = 'Renseignez une salle, un type et une capacité valides.'
    return
  }

  isAddingRoom.value = true
  addRoomMessage.value = null
  addRoomStatus.value = null

  try {
    await addRoom(token, { location, room_type: roomType, capacity })
    addRoomStatus.value = 'success'
    addRoomMessage.value = 'Salle ajoutée.'
    newRoom.location = ''
    newRoom.room_type = ''
    newRoom.capacity = 0
    classroomSelectRef.value?.reload?.()
  } catch (err) {
    console.error('Unable to add room', err)
    addRoomStatus.value = 'error'
    addRoomMessage.value = "Impossible d'ajouter la salle."
  } finally {
    isAddingRoom.value = false
  }
}
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

.csv {
  background: #01778b;
  color: white;

}
</style>
