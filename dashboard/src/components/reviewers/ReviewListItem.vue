<template>
  <div
    class="p-4 border-t border-b border-gray-500 w-full flex flex-col gap-2 hover:cursor-pointer hover:bg-gray-50"
    @click="router.push({ name: 'ReviewPage', params: { id: event.event } })"
  >
    <div class="flex flex-col gap-1 mb-2">
      <div class="flex gap-2 text-sm uppercase">
        <span>{{ event.chapter_name }}</span>
        <span> - {{ dayjs(event.start_date).format('D MMM YYYY') }}</span>
      </div>
      <h4 class="text-lg font-semibold">{{ event.event_name }}</h4>
    </div>
    <div class="flex flex-col md:flex-row gap-2 justify-between">
      <div class="flex flex-col md:flex-row gap-2 font-medium md:divide-x-2 divide-gray-300">
        <span class="text-sm text-gray-800">Submissions: {{ event.submission_count }}</span>
        <span class="text-sm md:pl-2 text-green-800">Reviewed: {{ event.reviewed_count }}</span>
        <span class="text-sm md:pl-2 text-orange-800"
          >Pending Review: {{ event.reviewed_count }}</span
        >
      </div>
    </div>
  </div>
</template>
<script setup>
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
const router = useRouter()

defineProps({
  event: {
    type: Object,
    required: true,
  },
})
</script>
