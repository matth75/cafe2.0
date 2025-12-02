<template>
  <section class="content kawa-page">
    <header class="major">
      <h1>Calendrier {{ calendarName }}</h1>
      <p>Calendrier de ta promo</p>
      
    </header>
  
    <Calendar_compo @calendar-title="handleCalendarTitle" />

  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Calendar_compo from '@/components/Calendar_compo.vue'

const DEFAULT_TITLE = 'Calendriers'
const calendarName = ref<string>(DEFAULT_TITLE)

function handleCalendarTitle(name: string) {
  const trimmed = name?.trim()
  calendarName.value = trimmed || DEFAULT_TITLE
}
</script>

<style scoped>
.kawa-page .calendar-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.calendar-hint {
  font-size: 0.9rem;
  color: #7f8c8d;
}

.calendar-status {
  margin: 1rem 0;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
}

.calendar-status.error {
  background: rgba(192, 57, 43, 0.12);
  color: #c0392b;
}

.calendar-status.empty {
  background: rgba(127, 140, 141, 0.2);
  color: #2c3e50;
}

.event-details {
  margin-top: 2rem;
  padding: 1.5rem;
  border-radius: 1rem;
  background: #fff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.event-details header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.event-details dl {
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem 1.5rem;
}

.event-details dt {
  font-weight: 600;
  color: #7f8c8d;
}

.event-details dd {
  margin: 0.15rem 0 0;
}
</style>
