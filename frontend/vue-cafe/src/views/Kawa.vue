<template>
  <div>
    <v-sheet class="d-flex" tile>
      <v-btn class="ma-2" variant="text" icon @click="goPrev">
        <v-icon>mdi-chevron-left</v-icon>
      </v-btn>
      <v-select
        v-model="type"
        :items="types"
        class="ma-2"
        density="comfortable"
        label="Vue"
        variant="outlined"
        hide-details
      />
      <v-select
        v-model="mode"
        :items="modes"
        class="ma-2"
        density="comfortable"
        label="Chevauchement"
        variant="outlined"
        hide-details
      />
      <v-select
        v-model="weekday"
        :items="weekdays"
        class="ma-2"
        density="comfortable"
        label="Jours"
        variant="outlined"
        hide-details
      />
      <v-spacer />
      <v-btn class="ma-2" variant="text" icon @click="goNext">
        <v-icon>mdi-chevron-right</v-icon>
      </v-btn>
    </v-sheet>
    <v-sheet height="600">
      <v-calendar
        ref="calendar"
        v-model="value"
        :event-color="getEventColor"
        :event-overlap-mode="mode"
        :event-overlap-threshold="30"
        :events="events"
        :type="type"
        :weekdays="weekday"
        @change="getEvents"
      />
    </v-sheet>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

type CalendarRange = { start: { date: string }; end: { date: string } }

const calendar = ref<any>(null)
const type = ref('month')
const types = ['month', 'week', 'day', '4day']
const mode = ref('stack')
const modes = ['stack', 'column']
const weekday = ref([0, 1, 2, 3, 4, 5, 6])
const weekdays = [
  { title: 'Sun - Sat', value: [0, 1, 2, 3, 4, 5, 6] },
  { title: 'Mon - Sun', value: [1, 2, 3, 4, 5, 6, 0] },
  { title: 'Mon - Fri', value: [1, 2, 3, 4, 5] },
  { title: 'Mon, Wed, Fri', value: [1, 3, 5] },
]
const value = ref(new Date().toISOString().slice(0, 10))
const events = ref<
  Array<{
    name: string
    start: Date
    end: Date
    color: string
    timed: boolean
  }>
>([])
const colors = ['blue', 'indigo', 'deep-purple', 'cyan', 'green', 'orange', 'grey-darken-1']
const names = ['Meeting', 'Holiday', 'PTO', 'Travel', 'Event', 'Birthday', 'Conference', 'Party']

const goPrev = () => {
  calendar.value?.prev()
}

const goNext = () => {
  calendar.value?.next()
}

function rnd(a: number, b: number) {
  return Math.floor((b - a + 1) * Math.random()) + a
}

function getEvents({ start, end }: CalendarRange) {
  const evts: typeof events.value = []

  const min = new Date(`${start.date}T00:00:00`)
  const max = new Date(`${end.date}T23:59:59`)
  const days = (max.getTime() - min.getTime()) / 86400000
  const eventCount = rnd(days, days + 20)

  for (let i = 0; i < eventCount; i++) {
    const allDay = rnd(0, 3) === 0
    const firstTimestamp = rnd(min.getTime(), max.getTime())
    const first = new Date(firstTimestamp - (firstTimestamp % 900000))
    const secondTimestamp = rnd(2, allDay ? 288 : 8) * 900000
    const second = new Date(first.getTime() + secondTimestamp)

    evts.push({
      name: names[rnd(0, names.length - 1)],
      start: first,
      end: second,
      color: colors[rnd(0, colors.length - 1)],
      timed: !allDay,
    })
  }

  events.value = evts
}

function getEventColor(event: { color: string }) {
  return event.color
}

function seedInitialEvents() {
  const seedDate = new Date(value.value)
  const start = new Date(seedDate.getFullYear(), seedDate.getMonth(), 1)
  const end = new Date(seedDate.getFullYear(), seedDate.getMonth() + 1, 0)
  getEvents({
    start: { date: start.toISOString().slice(0, 10) },
    end: { date: end.toISOString().slice(0, 10) },
  })
}

onMounted(() => {
  seedInitialEvents()
})
</script>
