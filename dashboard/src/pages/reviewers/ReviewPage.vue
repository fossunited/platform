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
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="icon icon-tabler w-4 h-4 icons-tabler-outline icon-tabler-arrow-up-right"
          >
            <path stroke="none" d="M0 0h24v24H0z" fill="none" />
            <path d="M17 7l-10 10" />
            <path d="M8 7l9 0l0 9" />
          </svg>
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
