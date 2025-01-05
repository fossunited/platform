<template>
  <div class="pt-12 pb-6 px-6 md:p-6 bg-white border border-gray-500 flex flex-col gap-3 w-full">
    <div class="flex justify-between">
      <div class="flex gap-3 md:gap-4">
        <div
          class="px-2 py-1 bg-green-100 text-green-600 text-xs font-medium rounded-[2px] flex items-center"
        >
          {{ session.category != 'Other' ? session.category : session.other_category }}
        </div>
        <div
          class="px-2 py-1 bg-gray-100 text-gray-900 text-xs font-medium rounded-[2px] flex items-center"
        >
          {{ getDuration() }}
        </div>
      </div>

      <button
        class="px-2 py-1 bg-gray-900 text-white text-xs font-medium rounded-[2px] flex items-center gap-2"
        @click="downloadSessionIcs()"
      >
        <IconCalendarPlus class="w-4 h-4" />
        <span class="hidden md:block uppercase">Add to Calendar</span>
      </button>
    </div>
    <h3 class="text-lg font-semibold tracking-[-0.18px]">
      {{ session.title }}
    </h3>
    <div v-if="getSpeakers()" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="(speaker, index) in getSpeakers().speakers" :key="index">
        <div class="flex gap-2 items-start">
          <img
            :src="speaker.image"
            :alt="speaker.name"
            class="w-13 h-13 rounded-[2px] object-cover object-top"
          />
          <div class="flex flex-col gap-1">
            <h4 class="text-base font-medium">{{ speaker.name }}</h4>
            <p class="text-xs text-gray-600">
              {{ speaker.designation }} | {{ speaker.organization }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { createEvent } from 'ics'
import { toast } from 'vue-sonner'
import { defineProps, inject } from 'vue'
import dayjs from 'dayjs'
import duration from 'dayjs/plugin/duration'
import { IconCalendarPlus } from '@tabler/icons-vue'

dayjs.extend(duration)

const event = inject('event')

const props = defineProps({
  session: {
    type: Object,
    required: true,
  },
})

function formatTimeForIcs(time) {
  let date_arr = props.session.scheduled_date.split('-').map(Number)
  let time_arr = time.split(':').map(Number)
  time_arr.pop()

  const formattedTime = date_arr.concat(time_arr)
  return formattedTime
}

function downloadSessionIcs() {
  let icsEvent = {
    title: `${props.session.title} - ${event.data.event_name}`,
    start: formatTimeForIcs(props.session.start_time),
    end: formatTimeForIcs(props.session.end_time),
    location: `${props.session.hall}, ${event.data.event_location}`,
    categories: [
      props.session.category !== 'Other' ? props.session.category : props.session.other_category,
    ],
  }

  let alarms = []

  alarms.push({
    action: 'display',
    description: `Session Reminder: ${props.session.title} | ${event.data.event_name}`,
    trigger: { minutes: 10, before: true },
  })
  alarms.push({
    action: 'audio',
    description: `Session Reminder: ${props.session.title} | ${event.data.event_name}`,
    trigger: { minutes: 10, before: true },
  })

  icsEvent['alarms'] = alarms

  createEvent(icsEvent, (error, value) => {
    if (error) {
      toast.error('Error downloading the .ics file' + error.message)
      return
    }

    const blob = new Blob([value], { type: 'text/calendar' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${props.session.title}.ics`
    a.click()
    window.URL.revokeObjectURL(url)
  })

  toast.info('.ics file downloaded.')
}

function getDuration() {
  const startTime = dayjs(`1970-01-01 ${props.session.start_time}`)
  const endTime = dayjs(`1970-01-01 ${props.session.end_time}`)

  const durationInMinutes = endTime.diff(startTime, 'minute')

  return `${durationInMinutes} minutes`
}

function getSpeakers() {
  return JSON.parse(props.session.speakers)
}
</script>
