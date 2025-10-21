<script setup>
  import { ref } from 'vue';
  import AppHeader from './components/Header.vue'
  import Sidebar from './components/Sidebar.vue'
  import { RouterView } from 'vue-router'

  const sideBarOpen = ref(true);  
  const toggleSideBar = () => {
    sideBarOpen.value = !sideBarOpen.value;
  };

  const items = ref([])
  const name = ref('')
  const qty = ref(1)
  const error = ref(null)
  const mdp = ref('')
  const mail = ref('')

  const API_BASE = 'http://localhost:8000/api' // backend

  async function loadItems() {
    error.value = null
    try {
      const r = await fetch(`${API_BASE}/users/info`)
      items.value = await r.json()
    } catch (e) {
      error.value = 'Impossible de récupérer les items'
      console.error(e)
    }
  }

async function onSubmit() {
  error.value = null
  try {
    const payload = { name: name.value, qty: qty.value, mdp: mdp.value, mail: mail.value }
    const r = await fetch(`${API_BASE}/users/create`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const data = await r.json()
    // reset inputs
    name.value = ''
    qty.value = 1
    mdp.value = ''
    mail.value = ''
    // rafraîchir la liste
    await loadItems()
  } catch (e) {
    error.value = 'Erreur lors de l\'envoi'
    console.error(e)
  }
}

// load at start
loadItems()
</script>

<style>
input { margin-right: 8px; padding: 6px; }
button { padding: 6px 10px; }
</style>


<template>
  <div id="wrapper" class="is-preload">
    <div id="main">
      <div class="inner">
      <button class="btn-toggle" @click="toggleSideBar">
      {{ sideBarOpen ? 'Nuit' : 'Jour' }}
      </button>
      <AppHeader />
      <RouterView />
      </div>
    </div>
    <div id="sidebar" v-show="sideBarOpen">
      <Sidebar />
    </div>
  </div>
</template>
