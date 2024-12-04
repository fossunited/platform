<template>
  <Drawer v-model="open" title="Create Email Campaign">
    <div class="space-y-4 h-full">
      <p class="text-sm text-gray-600 -mt-4">Create email campaigns to be sent to users.</p>
      <EmailFormTemplate v-model="data" :event="event" :chapter="chapter" />
      <div class="w-full pt-4 space-y-2 border-t bg-white sticky bottom-0 z-50 -mb-2">
        <ErrorMessage :message="errorMessages" />
        <Button label="Create" class="w-full" variant="solid" @click="handleCampaignCreate" />
      </div>
    </div>
  </Drawer>
</template>
<script setup>
import Drawer from '@/components/ui/Drawer.vue'
import EmailFormTemplate from './EmailFormTemplate.vue'
import { validateCampaignFields } from '@/helpers/emailing'
import { ErrorMessage, createResource } from 'frappe-ui'
import { reactive, ref } from 'vue'
import { toast } from 'vue-sonner'

const errorMessages = ref('')
const open = defineModel({ type: Boolean })
const emit = defineEmits(['create-campaign'])

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

const data = reactive({
  email_group: [],
  subject: '',
  content_type: 'Rich Text',
  attachments: [],
  message: '',
  message_html: '',
  message_md: '',
})

const newsletter = createResource({
  url: 'fossunited.api.emailing.create_newsletter_campaign',
  makeParams() {
    return {
      data: data,
      event: props.event,
      chapter: props.chapter,
    }
  },
  onSuccess() {
    toast.success('Campaign created successfully!')
    emit('create-campaign')
    open.value = false
  },
  onError(err) {
    toast.error('Error while creating campaign! ' + err.messages)
  },
})

const handleCampaignCreate = () => {
  const errors = validateCampaignFields(data)

  if (errors.length) {
    errorMessages.value = errors.join('\n')
    return
  }

  newsletter.fetch()
}
</script>
