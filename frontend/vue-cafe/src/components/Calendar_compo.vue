<template>
    

    <p v-if="error" class="calendar-status error">{{ error }} </p>

    <button
        v-if="isSuperuser"
        type="button"
        class="button primary small"
        @click="openAddEventModal"
    >
        Ajouter un événement
    </button>

    <FullCalendar
        v-if="calendarOptions"
        ref="calendarRef"
        class="calendar-widget"
        :options="calendarOptions"
    />

    <p v-else-if="!isLoading" class="calendar-status empty">
        Impossible d’afficher le calendrier pour le moment.
    </p>

    <div
        v-if="isAddModalOpen && isSuperuser"
        class="modal-overlay"
        @click.self="closeAddEventModal"
    >
        <div class="modal-content">
            <EventAdd
                :default-promo="activePromoSlug"
                @close="closeAddEventModal"
                @create="handleEventCreate"
            />
        </div>
    </div>

    <EventModif
        v-if="isConnected && isSuperuser && selectedEvent"
        :event="selectedEvent"
        @close="clearSelectedEvent"
        @submit="handleEventSubmit"
    />

    <!-- <EventPopUp
        v-else-if="selectedEvent && !isSuperuser && isConnected"
        :event="selectedEvent"
        @close="clearSelectedEvent"
    /> -->

    <div class="calendar-actions">
        <button type="button" class="button primary small" :disabled="isLoading" @click="loadCalendar">
            {{ isLoading ? 'Chargement…' : 'Rafraîchir' }}
        </button>
        <span v-if="lastLoaded" class="calendar-hint">
            Mis à jour à {{ lastLoaded }}
        </span>
    </div>
</template>

<script setup lang="ts" >
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import listPlugin from '@fullcalendar/list'
import interactionPlugin from '@fullcalendar/interaction'
import iCalendarPlugin from '@fullcalendar/icalendar'
import { addEventToICS, getICS, type EventDetail } from '@/api'
import EventAdd from './event_add.vue'
import EventModif from './event_modif.vue'
//import EventPopUp from './event_pop_up.vue'
import { isConnected, isSuperuser, user, syncConnectionStatus } from '@/utils'


const emit = defineEmits<{
    (event: 'calendar-title', title: string): void
}>()

const props = defineProps<{
    selectedPromo?: string | false
}>()

const overridePromo = computed(() => {
    if (props.selectedPromo === undefined || props.selectedPromo === null) {
        return null
    }
    const value = String(props.selectedPromo).trim()
    return value.length ? value : null
})


type SelectedEvent = {
    uid: string
    title: string
    start: Date | null
    end: Date | null
    description?: string
    location?: string
}

const isLoading = ref(false)
const error = ref<string | null>(null)
const selectedEvent = ref<SelectedEvent | null>(null)
const selectedEventId = ref<string | null>(null)
const calendarRef = ref<any>(null)
const lastLoaded = ref<string | null>(null)
const icsUrl = ref<string | null>(null)
let blobUrl: string | null = null
const isAddModalOpen = ref(false)
const activePromoSlug = ref<string | null>(null)








const calendarOptions = computed(() => {
    if (!icsUrl.value || !isConnected.value) {
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
        initialView: 'timeGridWeek',
        weekends: false,
        slotMinTime: '08:00:00',
        slotMaxTime: '20:00:00',
        allDaySlot: false,
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
        eventContent: renderEventContent,
        eventClassNames,
        eventSources: [
            {
                id: 'calendar_ics',
                url: icsUrl.value,
                format: 'ics',
            },
        ],
    }
})


function handleEventClick(info: any) {
    const eventKey = getEventKey(info.event)
    selectedEvent.value = {
        uid: info.event.id,
        title: info.event.title,
        start: info.event.start,
        end: info.event.end,
        description: info.event.extendedProps?.description,
        location: info.event.extendedProps?.location,
    }
    selectedEventId.value = eventKey

    rerenderEvents()
}

function renderEventContent(arg: any) {
    const container = document.createElement('div')
    container.className = 'calendar-event-content'

    const timeEl = document.createElement('div')
    timeEl.className = 'calendar-event-time'
    timeEl.textContent = formatEventTime(arg.event)
    container.appendChild(timeEl)

    const titleEl = document.createElement('div')
    titleEl.className = 'calendar-event-title'
    titleEl.textContent = arg.event.title ?? ''
    container.appendChild(titleEl)

    const location = arg.event.extendedProps?.location
    if (location) {
        const locationEl = document.createElement('div')
        locationEl.className = 'calendar-event-location'
        locationEl.textContent = location
        container.appendChild(locationEl)
    }

    return { domNodes: [container] }
}

function formatEventTime(event: any) {
    const start = event.start
    const end = event.end
    if (!start) {
        return ''
    }

    const formatter = new Intl.DateTimeFormat('fr-FR', {
        hour: '2-digit',
        minute: '2-digit',
    })
    const startText = formatter.format(start)
    const endText = end ? formatter.format(end) : ''
    return endText ? `${startText} – ${endText}` : startText
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
        event?.id ?? null
    )
}

function rerenderEvents() {
    const api = calendarRef.value?.getApi?.()
    if (api) {
        api.refetchEvents()
    }
}

function openAddEventModal() {
    isAddModalOpen.value = true
}

function closeAddEventModal() {
    isAddModalOpen.value = false
}

async function handleEventCreate(payload: EventDetail) {
    try {
        await addEventToICS(payload)
        isAddModalOpen.value = false
        await loadCalendar()
    } catch (err) {
        console.error('Unable to create event', err)
        error.value = "Impossible de créer l'événement."
    }
}


async function loadCalendar() {
    isLoading.value = true
    error.value = null
    selectedEvent.value = null
    selectedEventId.value = null

    try {
        const connected = await syncConnectionStatus()
        if (!connected) {
            throw new Error('Utilisateur non connecté.')
        }
        const slugOverride = overridePromo.value
        const slug = slugOverride ?? await fetchPromoSlug()
        activePromoSlug.value = slug
        emit('calendar-title', slug)
        const data = await getICS(slug)
        //console.log("ICS data fetched for slug:", slug, data)
        const icsContent =
            typeof data === 'string'
                ? data
                : data?.ics ?? data?.content ?? JSON.stringify(data)

        if (!icsContent || icsContent.length < 10) {
            console.error('Empty ICS content received')
            throw new Error('Flux ICS vide pour la promo sélectionnée.')
        }
        if (blobUrl) {
            URL.revokeObjectURL(blobUrl)
        }
        const icsFixed = icsContent.replace(/^ID:/gm, "UID:");
        const blob = new Blob([icsFixed], { type: "text/calendar" });
        blobUrl = URL.createObjectURL(blob)
        icsUrl.value = blobUrl
        lastLoaded.value = new Date().toLocaleTimeString('fr-FR')
    } catch (err) {
        console.error('Unable to load ICS feed', err)
        error.value =
            err instanceof Error && err.message === 'Utilisateur non connecté.'
                ? "Veuillez vous connecter pour afficher le calendrier."
                : "Impossible de charger le calendrier pour le moment."
        icsUrl.value = null
        emit('calendar-title', 'Calendriers')
    } finally {
        isLoading.value = false
    }
}

async function fetchPromoSlug(): Promise<string> {
    if (!user.value?.promo_id) {
        const refreshed = await syncConnectionStatus()
        if (!refreshed || !user.value?.promo_id) {
            return 'get_all'
        }
    }
    return normalizePromoSlug(user.value?.promo_id)
}

function normalizePromoSlug(value: unknown): string {
    if (typeof value === 'number' && !Number.isNaN(value)) {
        return String(value)
    }

    if (typeof value === 'string') {
        const trimmed = value.trim()
        if (
            trimmed &&
            trimmed.toLowerCase() !== 'false' &&
            trimmed.toLowerCase() !== 'none'
        ) {
            return trimmed
        }
    }

    if (value && typeof value === 'object' && 'toString' in value) {
        const casted = String(value)
        if (casted) {
            return casted
        }
    }

    return 'get_all'
}


onMounted(async () => {
    await syncConnectionStatus()
    loadCalendar()
})

watch(overridePromo, (newValue, oldValue) => {
    if (newValue !== oldValue) {
        loadCalendar()
    }
})

onBeforeUnmount(() => {
    if (blobUrl) {
        URL.revokeObjectURL(blobUrl)
    }
})

</script>

<style scoped>
.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.35);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    overflow-y: auto;
}

.modal-content {
    width: min(500px, 90vw);
    background: #fff;
    border-radius: 1rem;
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.2);
}

:deep(.calendar-event-content) {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
}

:deep(.calendar-event-time) {
    font-size: 0.85rem;
    font-weight: 600;
}

:deep(.calendar-event-location) {
    font-size: 0.85rem;
    color: #555;
}

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
