<template>
<section id="banner">
<div class="content">
<header>
<h1>Bienvenue sur CAFE</h1>
</header>


<div class="cta-row">
<RouterLink
  v-if="!isConnected"
  class="button Button_principal"
  to="/login"
>
  Connexion
</RouterLink>
<RouterLink
  v-else
  class="button Button_principal"
  :to="{ name: 'user-detail', params: { id: 'profil' } }"
>
  Mon profil
</RouterLink>

  <RouterLink class="button Button_principal" to="/register">Inscription</RouterLink>
</div>

<br />

<div class="inner">
<header class="major">
<h2>À propos de CAFE</h2>
</header>
<p> CAFE est une plateforme dédiée aux étudiants et professeurs du DER SIEN ((Nikola Tesla) ((GE)) (((E3A)))...) pour accéder à leur emploi du temps et à d'autres informations.
    <br />
    Les étudiants, après inscription, peuvent consulter leur emploi du temps, mis à jour régulièrement par les administrateurs, les ressrouces pédagogiques et des informatiosn diverses.
    Les délégués de promo et les professeurs disposent de fonctionnalités supplémentaires pour gérer les calendriers des promos et des salles et communiquer avec les étudiants.
    <br />
    Sur votre profil, vous pouvez choisir votre promo de référence pour accéder rapidement à votre emploi du temps.
    Un tuto sur la page de votre calendrier vous guidera pour ajouter votre emploi du temps à votre agenda personnel (Google Calendar, Apple Calendar, etc.).
</p>


<header class="major">
<h2>Contactez-nous</h2>
</header>
<p>Ce site se veut évolutif et collaboratif, n'hésite pas à envoyer tes suggestions et commentaires.</p>
<RouterLink class="button big" to="/contact">Envoie nous un message</RouterLink>

</div>


</div>
</section>
</template>


<script setup lang="ts">
import { isConnected, isSuperuser } from '@/utils'


</script>

<style scoped>
.cta-row {
  display: flex;
  justify-content: center;
  gap: 1rem;
}
</style>
