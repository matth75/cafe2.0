<template>
  <div
    @click="generateColorAvatar"
    class="user-avatar"
    :style="avatarStyle"
    aria-hidden="true"
  >
    {{ initials }}
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'

const color1 = ref('')
const color2 = ref('')

function generateColorAvatar() {
  const letters = '0123456789ABCDEF'
  let colorA = '#'
  let colorB = '#'
  for (let i = 0; i < 6; i++) {
    colorA += letters[Math.floor(Math.random() * 16)]
    colorB += letters[Math.floor(Math.random() * 16)]
  }
  color1.value = colorA
  color2.value = colorB
}
const avatarStyle = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
  '--color1': color1.value || '#3498db',
  '--color2': color2.value || '#9b59b6',
}));

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



onMounted(() => generateColorAvatar())

</script>

<style scoped>
.user-avatar {
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color1), var(--color2));
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 1.5rem;
  font-weight: 700;
  text-transform: uppercase;
}
</style>
