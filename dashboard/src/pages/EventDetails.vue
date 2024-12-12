<template>
  <div v-if="event.doc" class="px-4 py-8 md:p-8 w-full z-0 min-h-screen">
    <div class="flex flex-col md:flex-row gap-2 justify-between">
      <EventHeader
        :event="event.doc"
        :form-exists="true"
        :form="{
          data: {
            is_published: event.doc.is_published,
            doctype: 'Event',
          },
        }"
      />
      <Button
        class="w-fit"
        size="md"
        label="Update Details"
        icon-left="edit"
        @click="updateDetails()"
      ></Button>
    </div>
    <div class="flex flex-col gap-3 my-6">
      <div class="font-semibold text-gray-800 border-b-2 pb-2">Banner Image</div>
      <div>
        <img
          :src="getBannerImage()"
          alt="Banner Image"
          class="object-cover w-full border rounded-lg aspect-[4.96/1]"
        />
        <div class="flex gap-2 my-2">
          <FileUploader
            :file-types="'image/*'"
            :validate-file="validateFile"
            @success="(file) => setBannerImage(file)"
          >
            <template #default="{ progress, uploading, openFileSelector }">
              <Button
                :variant="'subtle'"
                :size="'md'"
                :label="
                  uploading
                    ? `Uploading ${progress}`
                    : event.doc.banner_image
                      ? 'Change Image'
                      : 'Upload Image'
                "
                @click="openFileSelector"
              />
            </template>
          </FileUploader>
          <Button
            v-if="event.doc.banner_image"
            :variant="'subtle'"
            theme="red"
            :size="'md'"
            :label="'Remove Image'"
            @click="() => setBannerImage({ file_url: '' })"
          />
        </div>
        <div class="text-sm text-gray-600">
          The ideal dimensions for a banner image are: 1240 x 300 (WxH)
        </div>
      </div>
    </div>
    <div class="flex flex-col my-6">
      <div class="font-semibold text-gray-800 border-b-2 pb-2">Event Details</div>
      <div class="p-2 my-1 grid sm:grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-6">
        <FormControl
          v-model="event.doc.event_permalink"
          :type="'text'"
          size="md"
          label="Event Permalink"
        />
        <div class="flex flex-col gap-2">
          <FormControl
            :disabled="true"
            :value="getEventLink()"
            type="url"
            size="md"
            label="Event Link"
          >
            <template #suffix>
              <CopyToClipboardButton :value="getEventLink()" />
            </template>
          </FormControl>
          <Button
            label="See on Website"
            class="w-fit"
            icon-right="external-link"
            :link="createAbsoluteUrlFromRoute(event.doc.route)"
            :disabled="['Draft', 'Cancelled'].includes(event.doc.status)"
          />
        </div>
        <FormControl v-model="event.doc.event_name" :type="'text'" size="md" label="Event Name" />
        <FormControl
          v-model="event.doc.status"
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
            {
              label: 'Concluded',
              value: 'Concluded',
            },
            {
              label: 'Cancelled',
              value: 'Cancelled',
            },
          ]"
          size="md"
          label="Event Status"
          description="Current status of the event."
        />
        <FormControl
          v-model="event.doc.event_type"
          :type="'select'"
          :options="eventTypeOptions.data"
          size="md"
          label="Event Type"
        />
        <FormControl
          v-model="event.doc.event_bio"
          :type="'text'"
          size="md"
          label="Short Event Bio"
          description="This bio may be used in OG images and in event cards. Typically it is a one-liner."
        />
        <TextEditor
          label="Event Description"
          class="col-span-2"
          :model-value="event.doc.event_description"
          @update:model-value="($event) => (event.doc.event_description = $event)"
        />
      </div>
    </div>
    <div class="flex flex-col my-6">
      <div class="font-semibold text-gray-800 border-b-2 pb-2">Event Timeline</div>
      <div class="p-2 my-1 grid sm:grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-6">
        <FormControl
          v-model="event.doc.event_start_date"
          :type="'datetime-local'"
          label="Event Start Date & Time"
          size="md"
        />
        <FormControl
          v-model="event.doc.event_end_date"
          :type="'datetime-local'"
          label="Event End Date & Time"
          size="md"
        />
      </div>
    </div>
    <div class="flex flex-col my-6">
      <div class="font-semibold text-gray-800 border-b-2 pb-2">Location Details</div>
      <div class="p-2 my-1 grid sm:grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-6">
        <FormControl
          v-model="event.doc.event_location"
          :type="'text'"
          label="Location"
          size="md"
        />
        <FormControl v-model="event.doc.map_link" :type="'url'" label="Map Link" side="md" />
      </div>
    </div>
  </div>
</template>
<script setup>
import EventHeader from '@/components/EventHeader.vue'
import TextEditor from '@/components/TextEditor.vue'
import CopyToClipboardButton from '@/components/CopyToClipboardButton.vue'
import { createDocumentResource, createListResource, FileUploader, FormControl } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { toast } from 'vue-sonner'
import { createAbsoluteUrlFromRoute } from '@/helpers/utils'
import { inject } from 'vue'

const route = useRoute()
const event = createDocumentResource({
  doctype: 'FOSS Chapter Event',
  name: route.params.id,
  fields: ['*'],
  auto: true,
})
const chapter = inject('chapter')

const validateFile = (file) => {
  let extn = file.name.split('.').pop().toLowerCase()
  if (!['png', 'jpg'].includes(extn)) {
    return 'Only PNG and JPG images are allowed'
  }
}

const getBannerImage = () => {
  if (event.doc.banner_image) {
    return event.doc.banner_image
  }
  return '/assets/fossunited/images/defaults/event_banner.png'
}

const setBannerImage = (file) => {
  event.setValue.submit({
    banner_image: file.file_url,
  })
  if (file.file_url) {
    toast.success('Banner image uploaded successfully')
  } else {
    toast.info('Banner image removed successfully')
  }
}

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

const updateDetails = () => {
  event.save
    .submit()
    .then(() => {
      toast.success('Event details updated successfully')
    })
    .catch((error) => {
      toast.error('Failed to update event details', {
        description: error.message,
      })
    })
}

const getEventLink = () => {
  let event_route = createAbsoluteUrlFromRoute(
    chapter.data?.route + '/' + event.doc.event_permalink,
  )
  return event_route.replace(/(^\w+:|^)\/\//, '')
}
</script>
