<template>
  <div class="px-4 py-8 md:p-8 w-full z-0 min-h-screen">
    <div v-if="chapter.doc" class="flex justify-between mt-4">
      <ChapterHeader :chapter="chapter" />
    </div>
    <div class="flex flex-col md:flex-row gap-2 justify-between mt-6 pb-2 border-b">
      <div class="prose">
        <h2>Create Event</h2>
      </div>
    </div>
    <div v-if="eventTypeOptions.data">
      <div class="flex flex-col gap-5 my-6">
        <div class="space-y-2">
          <div class="prose">
            <h3>Details</h3>
          </div>
          <div class="my-1 grid sm:grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-6">
            <FormControl
              v-model="temp_event.event_type"
              :type="'select'"
              :options="eventTypeOptions.data"
              size="md"
              label="Event Type&ast;"
            />
            <FormControl
              v-model="temp_event.event_name"
              :type="'text'"
              size="md"
              label="Event Name&ast;"
            />
            <FormControl
              v-model="temp_event.event_permalink"
              :type="'text'"
              size="md"
              label="Event Permalink&ast;"
            />
            <FormControl
              :value="getEventLink()"
              size="md"
              label="Event Link"
              :disabled="true"
              description="The event link will be as shown above."
            />
            <FormControl
              v-model="temp_event.status"
              :type="'select'"
              :options="[
                {
                  label: 'Draft',
                  value: 'Draft',
                },
                {
                  label: 'Live',
                  value: 'Live',
                },
              ]"
              size="md"
              label="Event Status&ast;"
              description="Current status of the event."
            />
            <TextEditor
              label="Event Description&ast;"
              class="col-span-2"
              placeholder="Write an event description"
              :model-value="temp_event.event_description"
              @update:model-value="($event) => (temp_event.event_description = $event)"
            />
          </div>
        </div>
        <div class="space-y-2">
          <div class="prose">
            <h3>Location</h3>
          </div>
          <div class="grid sm:grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-6">
            <FormControl
              v-model="temp_event.location"
              :type="'text'"
              size="md"
              label="Location&ast;"
            />
            <FormControl v-model="temp_event.map_link" :type="'url'" size="md" label="Map Link" />
          </div>
        </div>
        <div class="space-y-2">
          <div class="prose">
            <h3>Timeline</h3>
          </div>
          <div class="grid sm:grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-6">
            <FormControl
              v-model="temp_event.event_start_date"
              :type="'datetime-local'"
              size="md"
              label="Event Start Date&ast;"
            />
            <FormControl
              v-model="temp_event.event_end_date"
              :type="'datetime-local'"
              size="md"
              label="Event End Date&ast;"
            />
          </div>
        </div>
        <ErrorMessage :message="errorMessages" />
        <div class="grid my-4 justify-items-end grid-cols-1 md:grid-cols-2">
          <div></div>
          <Button
            label="Create"
            size="md"
            variant="solid"
            class="w-1/2"
            :loading="createEvent.loading"
            @click="handleCreateEvent()"
          />
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import {
  usePageMeta,
  createDocumentResource,
  FormControl,
  createListResource,
  createResource,
  ErrorMessage,
} from 'frappe-ui'
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import ChapterHeader from '@/components/ChapterHeader.vue'
import TextEditor from '@/components/ui/TextEditor.vue'
import { createAbsoluteUrlFromRoute } from '@/helpers/utils.js'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()

let temp_event = reactive({
  doctype: 'FOSS Chapter Event',
  chapter: route.params.id,
  event_name: '',
  event_permalink: '',
  status: '',
  event_type: '',
  event_description: '',
  location: 'TBD',
  map_link: '',
  event_start_date: '',
  event_end_date: '',
})

const chapter = createDocumentResource({
  doctype: 'FOSS Chapter',
  name: route.params.id,
})

const eventTypeOptions = createListResource({
  doctype: 'FOSS Event Type',
  fields: ['name'],
  auto: true,
  transform(data) {
    return data.map((d) => {
      return { label: d.name, value: d.name }
    })
  },
})

const createEvent = createResource({
  url: 'frappe.client.insert',
  makeParams() {
    return {
      doc: temp_event,
    }
  },
  onSuccess(data) {
    toast.success('Event Created Successfully!')
    setTimeout(() => {
      router.push(`/event/${data.name}`)
    })
  },
  onError(err) {
    errorMessages.value = err.messages
    toast.error('Error creating the event.' + err.messages)
  },
})

const handleCreateEvent = () => {
  const errors = getFormError()

  if (errors.length) {
    errorMessages.value = errors.join('\n')
    return
  }

  createEvent.fetch()
}

const errorMessages = ref('')

const getFormError = () => {
  const errors = []

  if (!temp_event.event_type) {
    errors.push('Event Type is required')
  }

  if (!temp_event.event_name) {
    errors.push('Event Name is required')
  }

  if (!temp_event.event_permalink) {
    errors.push('Permalink is required')
  }

  if (!temp_event.status) {
    errors.push('Status is required')
  }

  if (!temp_event.event_description) {
    errors.push('Event description is required')
  }

  if (!temp_event.location) {
    errors.push(
      'Location cannot be empty. If it is not finalized, please enter TBD or "To be announced" in the field',
    )
  }

  if (!temp_event.event_start_date) {
    errors.push('Start Date is required')
  }

  if (!temp_event.event_end_date) {
    errors.push('End date is required')
  }

  if (dayjs(temp_event.event_end_date).isBefore(dayjs(temp_event.event_start_date))) {
    errors.push('End date cannot be before start date')
  }

  return errors
}

const getEventLink = () => {
  let event_route = createAbsoluteUrlFromRoute(
    chapter.doc?.route + '/' + temp_event.event_permalink,
  )
  return event_route.replace(/(^\w+:|^)\/\//, '')
}

usePageMeta(() => {
  return {
    title: 'Create Event',
  }
})
</script>
