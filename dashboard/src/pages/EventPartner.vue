<template>
  <div v-if="event.doc" class="px-4 py-8 md:p-8 w-full z-0 min-h-screen">
    <EventHeader :event="event.doc" />
    <ManageSponsorView />
  </div>
</template>
<script setup>
import EventHeader from '@/components/EventHeader.vue'
import { inject } from 'vue'
import ManageSponsorView from '@/layout/event/ManageSponsorView.vue'

const event = inject('event')
</script>
