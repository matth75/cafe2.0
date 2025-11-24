<template>
<div class="inner">

<!-- Menu -->
<nav id="menu">
<header class="major">
<h2>CAFE</h2>
</header>
<ul>
<li>
  <RouterLink
    :to="isConnected ? { name: 'user-detail', params: { id: 'profil' } } : { name: 'login' }"
  >
    {{ isConnected ? 'Profil' : 'Connexion' }}
  </RouterLink>
</li>

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
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { AUTH_EVENT } from '@/utils/authEvents'

const isSuperuser = ref(false)
const isConnected = ref(false)


function syncConnectionStatus() {
  isConnected.value = typeof window !== 'undefined' && typeof localStorage.getItem('cafe_token') === 'string'
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

  if (event.key === 'cafe_token') {
    syncConnectionStatus()
  }
}

function handleVisibility() {
  if (document.visibilityState === 'visible') {
    syncSuperuserFlag()
    syncConnectionStatus()
  }
}

function handleAuthEvent() {
  syncSuperuserFlag()
  syncConnectionStatus()
}

onMounted(() => {
  syncSuperuserFlag()
  syncConnectionStatus()
  window.addEventListener('storage', handleStorage)
  document.addEventListener('visibilitychange', handleVisibility)
  window.addEventListener(AUTH_EVENT, handleAuthEvent as EventListener)
})

onBeforeUnmount(() => {
  window.removeEventListener('storage', handleStorage)
  document.removeEventListener('visibilitychange', handleVisibility)
  window.removeEventListener(AUTH_EVENT, handleAuthEvent as EventListener)
})
</script>
