<template>
    

    <p v-if="error" class="calendar-status error">{{ error }}</p>

    <FullCalendar
        v-if="calendarOptions"
        ref="calendarRef"
        class="calendar-widget"
        :options="calendarOptions"
    />

    <p v-else-if="!isLoading" class="calendar-status empty">
        Impossible d’afficher le calendrier pour le moment.
    </p>

    <EventPopUp
        v-if="selectedEvent"
        :event="selectedEvent"
        @close="clearSelectedEvent"
        @submit="handleEventSubmit"
    />

    <div class="calendar-actions">
        <button type="button" class="button primary small" :disabled="isLoading" @click="loadCalendar">
            {{ isLoading ? 'Chargement…' : 'Rafraîchir' }}
        </button>
        <span v-if="lastLoaded" class="calendar-hint">
            Mis à jour à {{ lastLoaded }}
        </span>
    </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import listPlugin from '@fullcalendar/list'
import interactionPlugin from '@fullcalendar/interaction'
import iCalendarPlugin from '@fullcalendar/icalendar'
import { getICS } from '@/api'
import EventPopUp from './event_pop_up.vue'



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
const selectedEventId = ref<string | null>(null)
const calendarRef = ref<any>(null)
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
        eventClassNames,
        eventSources: [
            {
                id: 'psee-ics',
                url: "https://cafe.zpq.ens-paris-saclay.fr/api/ics/get_all",
                format: 'ics',
            },
        ],
    }
})

function handleEventClick(info: any) {
    const eventKey = getEventKey(info.event)
    selectedEvent.value = {
        title: info.event.title,
        start: info.event.start,
        end: info.event.end,
        description: info.event.extendedProps?.description,
        location: info.event.extendedProps?.location,
    }
    selectedEventId.value = eventKey
    rerenderEvents()
}

function handleEventSubmit(payload: {
    title: string
    start: string
    end: string
    description: string
    location: string
}) {
    
}

function clearSelectedEvent() {
    selectedEvent.value = null
    selectedEventId.value = null
    rerenderEvents()
}

function eventClassNames(arg: any) {
    const eventKey = getEventKey(arg.event)
    return eventKey && eventKey === selectedEventId.value
        ? ['calendar-event--selected']
        : []
}

function getEventKey(event: any) {
    return (
        event?.id ||
        event?.extendedProps?.uid ||
        event?._def?.publicId ||
        event?._instance?.instanceId ||
        null
    )
}

function rerenderEvents() {
    const api = calendarRef.value?.getApi?.()
    if (api) {
        api.rerenderEvents()
    }
}

async function loadCalendar() {
    isLoading.value = true
    error.value = null
    selectedEvent.value = null
    selectedEventId.value = null

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

:deep(.calendar-event--selected .fc-event-main) {
    box-shadow: 0 0 0 2px #01778b inset !important;
    background-color: rgba(240, 9, 124, 0.856) !important;
    color: #014752 !important;
}

</style>
