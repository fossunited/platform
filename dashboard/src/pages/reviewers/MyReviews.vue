<template>
  <div v-if="events.data" class="p-4">
    <div class="prose">
      <div class="prose pb-0">
        <h2 class="mb-1">Review Talks</h2>
        <p class="text-sm mb-4">List of all upcoming events with proposal forms.</p>
      </div>
    </div>
    <div v-if="events.data.length > 0" class="mt-5 flex flex-col">
      <ReviewListItem v-for="event in events.data" :key="event.name" :event="event" />
    </div>
    <div v-else class="flex flex-col gap-2 rounded-sm p-4 border bg-gray-50">
      <div class="text-sm font-medium uppercase text-gray-800">No Call For Proposals</div>
      <div class="text-xs text-gray-600">
        There are no CFPs open right now. There are no talks to review.
      </div>
    </div>
  </div>
</template>
<script setup>
import { createResource, Tooltip } from 'frappe-ui'
import ReviewListItem from '@/components/reviewers/ReviewListItem.vue'

const events = createResource({
  url: 'fossunited.api.reviewer.get_events_by_open_cfp',
  auto: true,
})
</script>
