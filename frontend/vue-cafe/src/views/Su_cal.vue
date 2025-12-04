<template>
  <section class="content">
    <header class="major">
      <h1>Espace Superuser</h1>
      <p>Actions réservées aux administrateurs de la plateforme CAFE.</p>
    </header>

    <div class="panel" style="text-align: center">
      <PromoSelect v-model="selectedPromo" />
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
import { ref } from 'vue'
import PromoSelect from '@/components/PromoSelect.vue'
import Calendar_compo from '@/components/Calendar_compo.vue'

const selectedPromo = ref('')
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
