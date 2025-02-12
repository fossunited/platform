<template>
  <Header priority="high" />
  <div
    v-if="event.loading"
    class="max-w-screen-lg mx-auto mt-8 flex items-center justify-center min-h-[320px]"
  >
    <LoadingText class="text-lg" text="Loading event data" />
  </div>
  <div v-else class="container mx-auto px-4">
    <Breadcrumb class="mt-2" :items="breadcrumb_items" />
    <EventHeader 
      :event="event.data" 
      class="my-4 border-b border-gray-900 pb-4"
      :image-priority="true"
    />

    <AllProposalsBanner 
      :event="event.data" 
      class="py-2"
      :image-priority="true" 
    />
    <!-- Search and filters -->
    <div class="flex flex-col gap-y-3 justify-between my-7 md:flex-row md:items-center">
      <div class="w-full md:w-1/2">
        <TextInput
          v-model="searchQuery"
          type="text"
          class="h-10"
          placeholder="Search by proposal title"
          variant="subtle outline"
        >
          <template #suffix>
            <FeatherIcon class="w-4" name="search" />
          </template>
        </TextInput>
      </div>
      <div class="flex gap-x-2 items-center">
        <ThemedSelectBlack v-model="selectedSessionType" :options="sessionTypes" />
        <ThemedSelectBlack v-model="selectedStatus" :options="statuses" />
      </div>
    </div>

    <div v-if="proposals.loading">
      <LoadingText class="text-lg" text="Loading Proposals..." />
    </div>
    <div v-else-if="proposals.data">
      <!-- Talk proposals list -->
      <div class="mb-12">
        <div v-if="filteredProposals.length != 0">
          <div v-for="(proposal, index) in filteredProposals" :key="index" class="border-b-2 py-4">
            <ProposalBlock 
              :proposal="proposal" 
              :image-priority="index < 3"  // Prioritize first 3 proposals' images
            />
          </div>
        </div>
        <div v-else>
          <h3>No proposals</h3>
        </div>
      </div>
    </div>
    <div v-else class="pt-3">
      <h4 class="text-lg font-medium">No proposals</h4>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { createResource, usePageMeta, LoadingText, TextInput, FeatherIcon } from 'frappe-ui'
import { createAbsoluteUrlFromRoute } from '@/helpers/utils'
import Header from '@/components/Header.vue'
import Breadcrumb from '@/components/Breadcrumb.vue'
import AllProposalsBanner from '@/components/proposals/AllProposalsBanner.vue'
import ProposalBlock from '@/components/proposals/ProposalBlock.vue'
import EventHeader from '@/components/schedule/EventHeader.vue'
import ThemedSelectBlack from '@/components/common/ThemedSelectBlack.vue'

const route = useRoute()

const event = createResource({
  url: 'fossunited.api.dashboard.get_event_from_route',
  makeParams() {
    return {
      route: route.params.route,
      fields: [
        'name',
        'chapter',
        'chapter_name',
        'event_name',
        'event_start_date',
        'event_end_date',
        'event_location',
        'event_bio',
        'is_external_event',
        'external_event_url',
        'event_logo',
        'proposal_page_description',
        'route',
      ],
    }
  },
  auto: true,
  onSuccess(data) {
    proposals.fetch()
  },
})

const proposals = createResource({
  url: 'fossunited.api.proposal.get_event_proposals',
  makeParams() {
    return {
      event: event.data.name,
    }
  },
  auto: false,
})

usePageMeta(() => {
  return {
    title: 'Proposals | ' + event.data?.event_name,
  }
})

const breadcrumb_items = computed(() => {
  if (!event.data) return []
  return [
    {
      label: event.data.event_name,
      link: event.data.is_external_event
        ? event.data.external_event_url
        : createAbsoluteUrlFromRoute(event.data.route),
    },
    {
      label: 'All Proposals',
    },
  ]
})

const searchQuery = ref('')

const selectedSessionType = ref('')
const selectedStatus = ref('')

const sessionTypes = ref([
  { label: 'All Session Types', value: '' },
  { label: 'Talk', value: 'Talk' },
  { label: 'Lightning Talk', value: 'Lightning Talk' },
  { label: 'Workshop', value: 'Workshop' },
  { label: 'Panel', value: 'Panel' },
])

const statuses = ref([
  { label: 'All Status', value: '' },
  { label: 'Approved', value: 'Approved' },
  { label: 'Rejected', value: 'Rejected' },
  { label: 'Screening', value: 'Screening' },
])

// Computed function for monitoring search-filter
const filteredProposals = computed(() => {
  if (!proposals.data) return []

  return proposals.data.filter((proposal) => {
    const matchesSearch = proposal.talk_title
      .toLowerCase()
      .includes(searchQuery.value.toLowerCase())
    const matchesSessionType =
      selectedSessionType.value === '' || proposal.session_type === selectedSessionType.value
    const matchesStatus = selectedStatus.value === '' || proposal.status === selectedStatus.value

    return matchesSearch && matchesSessionType && matchesStatus
  })
})
</script>
