<script setup>
  import { ref } from 'vue';
  import AppHeader from './components/Header.vue'
  import Sidebar from './components/Sidebar.vue'
  import { RouterView } from 'vue-router'

  const sideBarOpen = ref(true);  
  const toggleSideBar = () => {
    sideBarOpen.value = !sideBarOpen.value;
  };
</script>

<style>
input { margin-right: 8px; padding: 6px; }
button { padding: 6px 10px; }
</style>


<template>
  <div id="wrapper" class="is-preload">

    <div id="main">
      <div class="inner">
      <AppHeader />
      <RouterView />
      </div>
    </div>
    <div id="sidebar" :class="{ inactive: !sideBarOpen }">
      <a
        href="#sidebar"
        class="toggle"
        role="button"
        @click.prevent="toggleSideBar"
        :aria-expanded="sideBarOpen.toString()"
      >
        Menu
      </a>
      <Sidebar />
    </div>
  </div>
</template>
