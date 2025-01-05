<template>
  <Header />
  <div v-if="submission.data" class="w-full flex flex-col items-center">
    <div class="max-w-screen-xl p-4 w-full">
      <Breadcrumb class="mb-5" :items="breadcrumb_items" />
      <div class="flex flex-col gap-2">
        <div class="prose">
          <h1 class="text-[2rem]">{{ submission.data.talk_title }}</h1>
        </div>
        <div class="flex flex-wrap gap-2 md:gap-4 items-center mt-0 mb-2">
          <Tooltip
            v-if="submission.data.is_first_talk === 'Yes'"
            text="This is the first talk submitted by the speaker"
          >
            <Badge label="First Talk" variant="outline" size="lg" class="p-1">
              <template #prefix>
                <IconSparkles class="h-4 w-4" />
              </template>
            </Badge>
          </Tooltip>
          <span class="text-sm uppercase font-medium">{{ submission.data.session_type }}</span>
        </div>
        <a
          v-if="submission.data.talk_reference"
          class="text-sm uppercase text-green-700 cursor-pointer font-medium hover:underline flex items-center gap-1"
          :href="submission.data.talk_reference"
          target="_blank"
        >
          <span>View Session Reference</span>
          <IconExternalLink class="h-4 w-4 stroke-green-700" />
        </a>
        <div v-else class="text-sm text-gray-500">
          <span>Session reference not provided.</span>
        </div>
      </div>
      <div class="my-6 flex flex-col gap-4">
        <div class="prose min-w-full">
          <h3 class="-mb-4">Description</h3>
          <div class="my-2" v-html="submission.data.talk_description"></div>
        </div>
        <div v-if="!cfp_settings.data?.anonymise_proposals" class="prose min-w-full">
          <h3>About Speaker</h3>
          <div class="flex flex-col gap-2 items-start">
            <div class="flex gap-4 -mb-2">
              <img :src="submission.data.picture_url" class="w-12 h-12 rounded m-0" />
              <div class="flex flex-col gap-2">
                <h5 class="text-lg font-medium">
                  {{ submission.data.full_name }}
                </h5>
                <div class="flex flex-wrap items-center gap-2 divide-x-2 divide-gray-600">
                  <span class="text-sm">{{ submission.data.designation }}</span>
                  <span class="text-sm pl-2">{{ submission.data.organization }}</span>
                </div>
              </div>
            </div>
            <div class="text-base text-gray-600" v-html="submission.data.bio"></div>
          </div>
        </div>
        <ReviewSection :submission="submission" />
      </div>
    </div>
  </div>
  <div v-else class="w-full h-screen flex items-center justify-center">
    <LoadingIndicator class="w-6 h-6" />
  </div>
</template>
<script setup>
import { useRoute } from 'vue-router'
import { createResource, LoadingIndicator, Badge, usePageMeta, Tooltip } from 'frappe-ui'
import { computed, ref } from 'vue'
import { toast } from 'vue-sonner'
import Header from '@/components/Header.vue'
import Breadcrumb from '@/components/Breadcrumb.vue'
import ReviewSection from '@/components/reviewers/ReviewSection.vue'
import { IconExternalLink, IconSparkles } from '@tabler/icons-vue'

const route = useRoute()

const fields_to_fetch = ref([
  'name',
  'linked_cfp',
  'route',
  'is_published',
  'status',
  'event',
  'event_name',
  'is_first_talk',
  'session_type',
  'talk_title',
  'talk_reference',
  'talk_description',
  'custom_answers',
  'positive_reviews',
  'negative_reviews',
  'unsure_reviews',
  'approvability',
])

const cfp_settings = createResource({
  url: 'frappe.client.get_value',
  makeParams() {
    return {
      doctype: 'FOSS Event CFP',
      filters: { event: route.params.id },
      fieldname: [
        'allow_cfp_edit',
        'anonymise_proposals',
        'cfp_reviewers',
        'only_talk_proposals',
        'only_workshops',
      ],
    }
  },
  onSuccess(data) {
    if (!data.anonymise_proposals) {
      fields_to_fetch.value.push(
        ...['full_name', 'bio', 'designation', 'organization', 'picture_url'],
      )
    }
    submission.fetch()
  },
  auto: true,
})

const submission = createResource({
  url: 'frappe.client.get_value',
  makeParams() {
    return {
      doctype: 'FOSS Event CFP Submission',
      filters: {
        name: route.params.talk_id,
      },
      fieldname: fields_to_fetch.value,
    }
  },
  onSuccess(data) {
    let is_anonymous = new Boolean(cfp_settings.data.anonymise_proposals)
    if (!is_anonymous) {
      submitter_profile.fetch()
    }
  },
  onError(error) {
    toast.error('Failed to fetch submission details')
  },
})

const submitter_profile = createResource({
  url: 'fossunited.api.reviewer.get_submitter_profile',
  makeParams() {
    return {
      submission_id: submission.data.name,
    }
  },
  onError(error) {
    toast.error('Failed to fetch submitter profile')
  },
})

usePageMeta(() => {
  return {
    title: `Review - ${submission.data?.talk_title}`,
  }
})

const breadcrumb_items = computed(() => {
  return [
    {
      label: 'CFP Review',
      route: '/review',
    },
    {
      label: submission.data.event_name,
      route: { name: 'ReviewPage', params: { id: submission.data.event } },
    },
    {
      label: submission.data.talk_title,
    },
  ]
})
</script>
