<template>
  <div class="space-y-3">
    <div class="prose p-4 pb-0">
      <h2 class="mb-1">My Proposals</h2>
      <p class="text-sm mb-4">Overview of all the talks you have ever proposed</p>
    </div>
    <div v-if="proposals.loading" class="px-4">
      <LoadingText />
    </div>
    <div v-if="proposals.data" class="px-4">
      <p v-if="!proposals.data.length" class="text-sm text-gray-600">No submissions yet.</p>
      <SubmissionListItem
        v-for="(proposal, key) in proposals.data"
        :key="key"
        :proposal="proposal"
      />
    </div>
  </div>
</template>
<script setup>
import { createResource } from 'frappe-ui'
import LoadingText from 'frappe-ui/src/components/LoadingText.vue'
import { inject } from 'vue'
import SubmissionListItem from '@/components/profile/SubmissionListItem.vue'

const session = inject('$session')

const proposals = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    return {
      doctype: 'FOSS Event CFP Submission',
      fields: [
        'status',
        'event_name',
        'session_type',
        'talk_title',
        'route',
        'creation',
        'modified',
      ],
      order_by: 'creation',
      limit_page_length: 999,
      or_filters: { email: session.user, submitted_by: session.user },
    }
  },
  auto: true,
  loading: true,
})
</script>
