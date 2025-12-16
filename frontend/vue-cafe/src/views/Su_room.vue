<template>
  <section class="content">
    <header class="major">

     <h1> <RouterLink to="/Superuser">Espace Superuser</RouterLink> </h1>
      <p>Actions réservées aux administrateurs de la plateforme CAFE.</p>
    </header>

    <div class="panel">
      <ClassroomSelect> </ClassroomSelect>
      <button class="button">Ajouter une Salle </button>
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
import { ref } from 'vue'
import PromoSelect from '@/components/PromoSelect.vue'
import ClassroomSelect from '@/components/ClassroomSelect.vue';

const selectedRoom = ref('')
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

.csv {
  background: #01778b;
  color: white;

}
</style>
