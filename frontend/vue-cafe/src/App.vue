<template>
  <div id="wrapper" class="is-preload">
    <div id="main">
      <div class="inner">
      <AppHeader />
      <RouterView />
      </div>
    </div>
    <div id="sidebar">
      <Sidebar />
    </div>
  </div>
</template>


<script setup>
  import AppHeader from './components/Header.vue'
  import Sidebar from './components/Sidebar.vue'
</script>