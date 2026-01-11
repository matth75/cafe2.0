<template>
<section class="content">
  <header class="major">
    <h1>Espace Superuser </h1>
  </header>

  <div class="role-grid">
    <div class="role-panel">
      <h2 class="role-title">Professeurs</h2>
      <UserRoleList role="prof" :refresh-key="refreshKey" @refresh="refreshAll" />
    </div>

    <div class="role-panel">
      <h2 class="role-title">Élèves</h2>
      <UserRoleList role="eleve" :refresh-key="refreshKey" @refresh="refreshAll" />
    </div>

    <div class="role-panel role-panel-wide">
      <h2 class="role-title">Superusers</h2>
      <UserRoleList role="superuser" :refresh-key="refreshKey" @refresh="refreshAll" />
    </div>
  </div>
</section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import UserRoleList from '@/components/UserRoleList.vue'

const refreshKey = ref(0)

function refreshAll() {
  refreshKey.value += 1
}
</script>

<style scoped>
.role-grid {
  margin-top: 2rem;
  display: grid;
  gap: 1.5rem;
  grid-template-columns: 1fr;
}

.role-panel {
  padding: 1.5rem;
  border-radius: 1rem;
  background: #01768b1c;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.role-title {
  margin: 0;
}

@media (min-width: 900px) {
  .role-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .role-panel-wide {
    grid-column: 1 / -1;
  }
}
</style>
