<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div id="wrapper">
    <header id="header">
      <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/calendar">Calendar</RouterLink>
        <RouterLink to="/kawa">Kawa</RouterLink>
        <RouterLink to="/contact">Contact</RouterLink>
        <RouterLink to="/stage">Stage</RouterLink>
      </nav>
    </header>

    <RouterView />
  </div>
</template>
