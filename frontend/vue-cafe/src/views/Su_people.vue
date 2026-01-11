<template>
<section class="content">
  <header class="major">
    <h1>Espace Superuser </h1>
  </header>

  <div class="role-buttons panel">
    <button
      v-for="role in roles"
      :key="role.value"
      class="button"
      :class="{ active: selectedRole === role.value }"
      type="button"
      @click="selectedRole = role.value"
    >
      {{ role.label }}
    </button>
  </div>

  <div class="list-wrapper">
    <p v-if="!selectedRole" class="hint">Choisissez un rôle pour voir la liste.</p>
    <UserRoleList v-else :role="selectedRole" />
  </div>
</section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import UserRoleList from '@/components/UserRoleList.vue'

type Role = 'prof' | 'eleve' | 'superuser'

const roles: { value: Role; label: string }[] = [
  { value: 'prof', label: 'Professeurs' },
  { value: 'eleve', label: 'Élèves' },
  { value: 'superuser', label: 'Superusers' },
]

const selectedRole = ref<Role | null>(null)
</script>

<style scoped>
.role-buttons {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.button.active {
  background: #01778b;
  color: #fff;
}

.list-wrapper {
  margin-top: 1rem;
}

.hint {
  color: #7f8c8d;
}
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
</style>
