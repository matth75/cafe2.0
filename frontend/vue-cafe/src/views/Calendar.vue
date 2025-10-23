<template>
  <section class="content calendar-page">
    <header class="calendar-header">
      <h1>Agenda</h1>
      <div
        v-if="showCalendarControls || canRefreshCalendar"
        class="calendar-controls"
      >
        <template v-if="showCalendarControls">
          <label for="calendar-select">Calendrier</label>
          <select id="calendar-select" v-model="selectedCalendarId">
            <option
              v-for="source in calendars"
              :key="source.id"
              :value="source.id"
            >
              {{ source.label }}
            </option>
          </select>
        </template>
        <button
          v-if="canRefreshCalendar"
          type="button"
          class="button small"
          @click="refreshCurrent"
          :disabled="isLoading"
        >
          Rafraîchir
        </button>
      </div>
    </header>

    <p v-if="error" class="calendar-status error">{{ error }}</p>
    <p v-else-if="isLoading" class="calendar-status loading">Chargement…</p>

    <FullCalendar
      v-if="currentCalendar"
      class="calendar-widget"
      :options="calendarOptions"
    />

    <p v-else class="calendar-status empty">
      Aucun calendrier disponible pour le moment.
    </p>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import listPlugin from '@fullcalendar/list'
import interactionPlugin from '@fullcalendar/interaction'
import iCalendarPlugin from '@fullcalendar/icalendar'

const API_BASE =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api'

const isLoading = ref(false)
const error = ref(null)

const calendars = ref([
  {
    id: 'sample',
    label: 'Exemple de calendrier CAFE',
    type: 'local',
    events: [
      {
        id: 'sample-1',
        title: 'Réunion d’accueil',
        start: new Date().toISOString().slice(0, 10),
        allDay: true,
      },
      {
        id: 'sample-2',
        title: 'Cours - Architecture des réseaux',
        start: new Date(new Date().setHours(10, 0, 0)).toISOString(),
        end: new Date(new Date().setHours(12, 0, 0)).toISOString(),
      },
    ],
  },
])

const selectedCalendarId = ref(calendars.value[0]?.id ?? null)

const currentCalendar = computed(() =>
  calendars.value.find((calendar) => calendar.id === selectedCalendarId.value),
)

const showCalendarControls = computed(() => calendars.value.length > 1)
const canRefreshCalendar = computed(
  () => currentCalendar.value?.type === 'json',
)

const calendarOptions = computed(() => {
  const base = {
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
    events: [],
    eventSources: [],
  }

  if (!currentCalendar.value) {
    return base
  }

  if (
    ['local', 'json'].includes(currentCalendar.value.type) &&
    currentCalendar.value.events
  ) {
    base.events = currentCalendar.value.events
  }

  if (currentCalendar.value.type === 'ics' && currentCalendar.value.url) {
    base.eventSources = [
      {
        id: currentCalendar.value.id,
        url: currentCalendar.value.url,
        format: 'ics',
      },
    ]
  }

  return base
})

function normalizeCalendarSource(rawSource, index) {
  const type = rawSource?.type ?? rawSource?.format ?? 'json'

  if (type === 'ics' && rawSource?.url) {
    return {
      id: rawSource.id ?? `ics-${index}`,
      label: rawSource.label ?? rawSource.name ?? 'Calendrier ICS',
      type: 'ics',
      url: rawSource.url,
    }
  }

  return {
    id: rawSource.id ?? `json-${index}`,
    label: rawSource.label ?? rawSource.name ?? 'Calendrier',
    type: 'json',
    url: rawSource.url ?? rawSource.endpoint ?? null,
    events: Array.isArray(rawSource.events) ? rawSource.events : null,
  }
}

function normalizeEvent(rawEvent, index) {
  if (!rawEvent) {
    return null
  }

  const title = rawEvent.title ?? rawEvent.summary ?? `Événement ${index + 1}`

  return {
    id: rawEvent.id ?? rawEvent.uid ?? `event-${index}`,
    title,
    start: rawEvent.start ?? rawEvent.startDate ?? rawEvent.begin,
    end: rawEvent.end ?? rawEvent.endDate ?? rawEvent.finish ?? null,
    allDay: Boolean(rawEvent.allDay ?? rawEvent.allday ?? false),
    extendedProps: rawEvent.extendedProps ?? rawEvent.meta ?? {},
  }
}

async function fetchCalendars() {
  isLoading.value = true
  error.value = null

  try {
    const response = await fetch(`${API_BASE}/calendars`, {
      credentials: 'include',
    })

    if (!response.ok) {
      throw new Error('Réponse invalide du serveur')
    }

    const payload = await response.json()

    if (Array.isArray(payload) && payload.length > 0) {
      calendars.value = payload
        .map(normalizeCalendarSource)
        .filter((item) => item)

      selectedCalendarId.value = calendars.value[0]?.id ?? null
    }
  } catch (err) {
    console.error('Unable to fetch calendars', err)
    error.value =
      "Impossible de récupérer les calendriers, affichage d'un exemple."
  } finally {
    isLoading.value = false
  }
}

async function fetchEventsForCalendar(calendar) {
  if (!calendar?.url) {
    return
  }

  isLoading.value = true
  error.value = null

  try {
    const response = await fetch(calendar.url, { credentials: 'include' })

    if (!response.ok) {
      throw new Error('Réponse invalide du serveur')
    }

    const payload = await response.json()
    const list = Array.isArray(payload?.events) ? payload.events : payload

    if (Array.isArray(list)) {
      calendar.events = list
        .map(normalizeEvent)
        .filter((item) => item?.start)
    } else {
      throw new Error('Aucun événement exploitable reçu')
    }
  } catch (err) {
    console.error('Unable to fetch events', err)
    error.value =
      'Impossible de récupérer les événements pour ce calendrier.'
  } finally {
    isLoading.value = false
  }
}

async function refreshCurrent() {
  if (currentCalendar.value?.type === 'json') {
    await fetchEventsForCalendar(currentCalendar.value)
  }
}

onMounted(async () => {
  await fetchCalendars()

  if (currentCalendar.value?.type === 'json' && !currentCalendar.value.events) {
    await fetchEventsForCalendar(currentCalendar.value)
  }
})

watch(
  selectedCalendarId,
  async (next, prev) => {
    if (next === prev) {
      return
    }

    const source = calendars.value.find((item) => item.id === next)

    if (source?.type === 'json' && !source.events) {
      await fetchEventsForCalendar(source)
    }
  },
  { flush: 'post' },
)
</script>

<style scoped>
.calendar-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding-bottom: 2rem;
}

.calendar-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.calendar-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.calendar-controls select {
  padding: 0.35rem 0.5rem;
}

.calendar-status {
  font-size: 0.95rem;
  margin: 0;
}

.calendar-status.loading {
  color: #888;
}

.calendar-status.error {
  color: #c0392b;
}

.calendar-widget {
  background: #fff;
  border-radius: 0.75rem;
  padding: 1rem;
  box-shadow: 0 8px 24px rgba(15, 179, 15, 0.08);
}
</style>
