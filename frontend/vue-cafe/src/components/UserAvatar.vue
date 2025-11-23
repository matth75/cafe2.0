<template>
  <div
    class="user-avatar"
    :style="avatarStyle"
    aria-hidden="true"
  >
    {{ initials }}
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface UserAvatarProps {
  firstName?: string | null
  lastName?: string | null
  size?: number
}

const props = withDefaults(defineProps<UserAvatarProps>(), {
  firstName: '',
  lastName: '',
  size: 64,
})

const initials = computed(() => {
  const first = props.firstName?.trim().charAt(0) ?? ''
  const last = props.lastName?.trim().charAt(0) ?? ''
  const result = `${first}${last}`.toUpperCase()
  return result || '??'
})

const avatarStyle = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
}))
</script>

<style scoped>
.user-avatar {
  border-radius: 50%;
  background: linear-gradient(135deg, #6c5ce7, #0984e3);
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 1.5rem;
  font-weight: 700;
  text-transform: uppercase;
}
</style>
