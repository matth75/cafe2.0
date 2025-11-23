<template>
<div class="inner">

<!-- Menu -->
<nav id="menu">
<header class="major">
<h2>CAFE</h2>
</header>
<ul>
<li v-if="!isConnected"><RouterLink to="/login">Connexion</RouterLink></li>
<li v-if="isConnected"><RouterLink to="/user-detail">Profil</RouterLink></li>
<li v-if="isConnected"><RouterLink to="/calendar">Agenda</RouterLink></li>
<li><RouterLink to="/kawa">Machine à Café</RouterLink></li>
<li><RouterLink to="/contact">Contact</RouterLink></li>
<li><RouterLink to="/stage">Stage</RouterLink></li>
<li v-if="isSuperuser"><RouterLink to="/superuser">Espace Superuser</RouterLink></li>
</ul>
</nav>


<!-- Section Contact -->
<section>
<header class="major">
<h2>Contact</h2>
</header>
<p>
Tu veux demander à Thomas Rodet de nous mettre 20/20 en Génie Logiciel ?<br />
=> envoie nous un mail
</p>
<ul class="contact">
<li class="icon solid fa-envelope">
<a href="mailto:contact@sien-ens.fr">contact@domaine-cafe.fr à setup</a>
</li>
<li class="icon solid fa-home">
ENS Paris-Saclay – DER SIEN - M2FESup Intranet
</li>
</ul>
</section>


<!-- Footer -->
<footer id="footer">
<p class="copyright">
&copy; CAFE / SIEN. Design base: HTML5 UP.<br />
Version 0.1<br />
Tazz - Matthew - Pilou
</p>
</footer>
</div>
</template>


<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

const isSuperuser = ref(false)
const isConnected = ref(false)

function syncConnectionStatus() {
  if (typeof window === 'undefined') {
    isConnected.value = false
    return
  }
  isConnected.value = localStorage.getItem('cafe_connected') === 'true'
}

function syncSuperuserFlag() {
  if (typeof window === 'undefined') {
    isSuperuser.value = false
    return
  }
  isSuperuser.value = localStorage.getItem('cafe_superuser') === 'true'
}

function handleStorage(event: StorageEvent) {
  if (event.key === 'cafe_superuser') {
    isSuperuser.value = event.newValue === 'true'
  }
}

function handleVisibility() {
  if (document.visibilityState === 'visible') {
    syncSuperuserFlag()
  }
}

onMounted(() => {
  syncSuperuserFlag()
  window.addEventListener('storage', handleStorage)
  document.addEventListener('visibilitychange', handleVisibility)
})

onBeforeUnmount(() => {
  window.removeEventListener('storage', handleStorage)
  document.removeEventListener('visibilitychange', handleVisibility)
})
</script>
