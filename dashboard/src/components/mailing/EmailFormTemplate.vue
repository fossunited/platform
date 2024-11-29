<template>
  <div class="flex flex-col h-full justify-between relative gap-4 pb-4">
    <div class="flex flex-col gap-4">
      <div
        v-if="data.schedule_sending"
        class="space-y-3 bg-blue-50 border border-blue-500 border-dashed p-4 rounded"
      >
        <h5 class="text-base font-semibold mb-1">Scheduled Sending</h5>
        <FormControl
          v-model="data.schedule_sending"
          type="checkbox"
          label="Schedule sending at a later time"
          :disabled="data.status == 'Sent'"
        />
        <FormControl
          v-model="data.schedule_send"
          variant="outline"
          type="datetime-local"
          :disabled="data.status == 'Sent'"
          label="Sent Email At&ast;"
        />
      </div>
      <div class="space-y-3">
        <h5 class="text-base font-semibold mb-1">Email Group</h5>
        <label class="text-sm text-gray-600">Audience&ast;</label>
        <Autocomplete
          v-model="data.email_group"
          :disabled="data.status == 'Sent'"
          class="-mt-2"
          label="Recipients &ast;"
          :options="emailGroups.data"
          :multiple="true"
          placeholder="Select Recipients"
        />
      </div>
      <div class="space-y-3">
        <h5 class="text-base font-semibold mb-1">Subject</h5>
        <FormControl
          v-model="data.subject"
          :disabled="data.status == 'Sent'"
          label="Subject&ast;"
          type="data"
        />
      </div>
      <div class="space-y-3">
        <h5 class="text-base font-semibold mb-1">Content</h5>
        <FormControl
          v-model="data.content_type"
          :disabled="data.status == 'Sent'"
          label="Content Type"
          type="select"
          :options="['Rich Text', 'Markdown', 'HTML']"
        />
        <TextEditor
          v-if="data.content_type == 'Rich Text'"
          :disabled="data.status == 'Sent'"
          class="col-span-2 mt-2"
          label="Message"
          :model-value="data.message"
          @update:model-value="($event) => (data.message = $event)"
        />
        <div v-else>
          <label class="text-sm text-gray-600">Message</label>
          <CodeEditor
            v-if="data.content_type == 'Markdown'"
            v-model="data.message_md"
            :disabled="data.status == 'Sent'"
            lang="md"
          />
          <CodeEditor
            v-if="data.content_type == 'HTML'"
            v-model="data.message_html"
            :disabled="data.status == 'Sent'"
          />
        </div>
      </div>
      <div class="space-y-3">
        <h5 class="text-base font-semibold mb-1">Attachments</h5>
        <FileUploader
          v-if="data.status !== 'Sent'"
          :file-types="['image/*', '.pdf', '.doc', '.docx']"
          :validate-file="validateFile"
          @success="handleAttachment"
        >
          <template #default="{ uploading, progress, message, error, openFileSelector }">
            <Button
              :loading="uploading"
              icon-left="plus"
              label="Add Attachments"
              @click="openFileSelector"
            />
            <div v-if="uploading" class="text-sm">Uploading {{ progress }}%</div>
            <div v-if="message" class="text-sm">{{ message }}</div>
            <div v-if="error" class="text-red-600 text-sm">{{ error }}</div>
          </template>
        </FileUploader>
        <div v-if="data.attachments" class="flex flex-col gap-2 py-1">
          <div v-for="item in data.attachments" :key="item">
            <a
              class="flex gap-2 items-center text-base cursor-pointer hover:underline"
              :href="createAbsoluteUrlFromRoute(item.file_url.substring(1))"
              target="_blank"
            >
              <FeatherIcon name="file" class="w-4 h-4" />
              {{ item.file_name }}
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import TextEditor from '@/components/TextEditor.vue'
import CodeEditor from '@/components/ui/CodeEditor.vue'
import { FormControl, FileUploader, FeatherIcon, createResource, Autocomplete } from 'frappe-ui'
import { reactive, ref, watch } from 'vue'
import { createAbsoluteUrlFromRoute } from '@/helpers/utils'

const props = defineProps({
  event: {
    type: String,
    default: '',
  },
  chapter: {
    type: String,
    default: '',
  },
})

const emailGroups = createResource({
  url: 'fossunited.api.emailing.get_email_groups',
  makeParams() {
    return {
      event: props.event,
      chapter: props.chapter,
    }
  },
  auto: true,
  transform(data) {
    let d = []
    data.forEach((item) => {
      d.push({
        label: item.group_type,
        value: item.name,
        description: `${item.total_subscribers} subscribers`,
      })
    })
    return d
  },
})

const data = defineModel({
  type: Object,
  required: true,
})

const handleAttachment = (file) => {
  data.value.attachments.push(file)
}

watch(
  () => data.value,
  (newData) => {
    if (!newData.schedule_sending && data.value.schedule_send) {
      data.value.schedule_send = ''
    }
  },
  { deep: true },
)

const validateFile = (fileObject) => {
  const validTypes = [
    'image/jpeg',
    'image/svg+xml',
    'image/png',
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  ]

  const maxSize = 10 * 1024 * 1024 // 5 MB

  if (!validTypes.includes(fileObject.type)) {
    return 'Invalid file type.'
  }
  if (fileObject.size > maxSize) {
    return 'File size exceeds the maximum limit of 10 MB.'
  }
}
</script>
