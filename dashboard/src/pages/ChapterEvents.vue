<template>
  <div v-if="chapter.doc" class="px-4 py-8 md:p-8 w-full z-0 min-h-screen">
    <div class="flex justify-between mt-4">
      <ChapterHeader :chapter="chapter" />
    </div>
    <div class="flex flex-col mt-4 gap-3 w-fit">
      <div class="text-base text-gray-600">View and Create events for your chapter.</div>
      <Button
        class="w-fit"
        label="Create New Event"
        icon-left="plus"
        size="md"
        route="events/create"
      />
    </div>
    <div class="flex flex-col gap-8 my-6">
      <div v-if="upcoming_events.data" class="flex flex-col gap-3">
        <div class="text-2xl font-semibold">Scheduled Events</div>
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          <EventCard v-for="event in upcoming_events.data" :key="event.name" :event="event" />
        </div>
        <div v-if="upcoming_events.data.length == 0">
          <div class="text-base text-gray-600">No events scheduled yet.</div>
        </div>
      </div>
      <div v-if="past_events.data" class="flex flex-col gap-3">
        <div class="text-2xl font-semibold">Concluded Events</div>
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          <EventCard v-for="event in past_events.data" :key="event.name" :event="event" />
        </div>
        <div v-if="past_events.data.length === 0">
          <div class="text-base text-gray-600">No events history.</div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { useRoute } from 'vue-router'
import { createDocumentResource, createListResource } from 'frappe-ui'
import EventCard from '@/components/EventCard.vue'
import ChapterHeader from '@/components/ChapterHeader.vue'
const route = useRoute()

const chapter = createDocumentResource({
  doctype: 'FOSS Chapter',
  name: route.params.id,
  fields: ['*'],
  auto: true,
})

const upcoming_events = createListResource({
  doctype: 'FOSS Chapter Event',
  fields: ['*'],
  filters: [
    ['chapter', '=', route.params.id],
    ['event_end_date', '>', new Date()],
    ['status', 'in', ['Live', 'Draft', 'Cancelled']],
  ],
  auto: true,
})

const past_events = createListResource({
  doctype: 'FOSS Chapter Event',
  fields: ['*'],
  filters: [
    ['chapter', '=', route.params.id],
    ['event_start_date', '<', new Date()],
    ['status', 'in', ['Concluded', 'Cancelled']],
  ],
  auto: true,
})
</script>
