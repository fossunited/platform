<template>
  <Header />
  <div v-if="event.doc" class="w-full flex flex-col items-center">
    <div class="max-w-screen-xl p-4 w-full">
      <Button label="Go Back" icon-left="arrow-left" variant="ghost" @click="router.back()" />
      <div class="prose my-5">
        <h1 class="m-0">CFP Review</h1>
        <p class="mt-1">Review the session proposals for this event.</p>
      </div>
      <hr class="mb-6" />
      <div class="my-6">
        <EventHeader :event="event.doc" />
        <a
          class="text-sm flex gap-1 my-4 hover:underline"
          target="_blank"
          :href="redirectToRoute(event.doc.route)"
        >
          <span> Go to Event Page </span>
          <IconArrowUpRight class="w-4 h-4" />
        </a>
      </div>
      <div class="my-2">
        <ProposalList :event="event.doc.name" />
      </div>
    </div>
  </div>
</template>
<script setup>
import { createDocumentResource, usePageMeta } from 'frappe-ui'
import { useRoute, useRouter } from 'vue-router'
import EventHeader from '@/components/EventHeader.vue'
import Header from '@/components/Header.vue'
import ProposalList from '@/components/reviewers/ProposalsList.vue'
import { IconArrowUpRight } from '@tabler/icons-vue'

const route = useRoute()
const router = useRouter()

usePageMeta(() => {
  return {
    title: 'CFP Review',
  }
})

const event = createDocumentResource({
  doctype: 'FOSS Chapter Event',
  name: route.params.id,
  fields: ['*'],
  auto: true,
})

const redirectToRoute = (route) => {
  return `${window.location.origin}/${route}`
}
</script>
