<template>
  <section class="content kawa-page">
    <header class="major">
      <h1>Calendriers</h1>
      <p>Visualisation du calendrier PSEE</p>
    </header>
  
    <Calendar_compo />

  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import listPlugin from '@fullcalendar/list'
import interactionPlugin from '@fullcalendar/interaction'
import iCalendarPlugin from '@fullcalendar/icalendar'
import { getICS } from '@/api'
import { all } from 'axios'
import Calendar_compo from '@/components/Calendar_compo.vue'

type SelectedEvent = {
  title: string
  start: Date | null
  end: Date | null
  description?: string
  location?: string
}

const PROMO_SLUG = "get_all"

const isLoading = ref(false)
const error = ref<string | null>(null)
const selectedEvent = ref<SelectedEvent | null>(null)
const lastLoaded = ref<string | null>(null)
const icsUrl = ref<string | null>(null)
let blobUrl: string | null = null

const calendarOptions = computed(() => {
  if (!icsUrl.value) {
    return null
  }

  return {
    plugins: [
      dayGridPlugin,
      timeGridPlugin,
      listPlugin,
      interactionPlugin,
      iCalendarPlugin,
    ],
    initialView: 'dayGridMonth',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek',
    },
    locale: 'fr',
    height: 'auto',
    navLinks: true,
    selectable: true,
    eventClick: handleEventClick,
    eventSources: [
      {
        id: 'psee-ics',
        url: "https://cafe.zpq.ens-paris-saclay.fr/api/ics/get_all",
        format: 'ics',
      },
    ],
  }
})

function formatDate(date: Date | null) {
  if (!date) return '—'
  return date.toLocaleString('fr-FR', {
    weekday: 'long',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function handleEventClick(info: any) {
  selectedEvent.value = {
    title: info.event.title,
    start: info.event.start,
    end: info.event.end,
    description: info.event.extendedProps?.description,
    location: info.event.extendedProps?.location,
  }
}

async function loadCalendar() {
  isLoading.value = true
  error.value = null
  selectedEvent.value = null

  try {
    const data = await getICS(PROMO_SLUG)
    const icsContent =
      typeof data === 'string'
        ? data
        : data?.ics ?? data?.content ?? JSON.stringify(data)

    if (!icsContent || icsContent.length < 10) {
      throw new Error('Flux ICS vide pour la promo sélectionnée.')
    }

    if (blobUrl) {
      URL.revokeObjectURL(blobUrl)
    }

    const blob = new Blob([icsContent], { type: 'text/calendar' })
    console.log("ICS Blob created:", blob)
    blobUrl = URL.createObjectURL(blob)
    icsUrl.value = blobUrl
    console.log("ICS URL loaded:", icsUrl.value)
    lastLoaded.value = new Date().toLocaleTimeString('fr-FR')
  } catch (err) {
    console.error('Unable to load ICS feed', err)
    error.value =
      "Impossible de charger le calendrier PSEE pour le moment."
    icsUrl.value = null
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadCalendar()
})

onBeforeUnmount(() => {
  if (blobUrl) {
    URL.revokeObjectURL(blobUrl)
  }
})
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
