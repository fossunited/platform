<template>
  <Drawer v-model="open" title="Manage Email Campaign">
    <SendTestDialog v-model="showSendTest" :campaign-id="campaignId" />
    <div v-if="campaign.loading">
      <LoadingText />
    </div>
    <template #post-title>
      <Badge v-if="campaign.data" :theme="getBadgeTheme[campaign.data.status]" variant="subtle">
        {{ getStatus }}
      </Badge>
    </template>
    <div v-if="campaign.data" class="h-full">
      <EmailFormTemplate v-model="campaignData" :event="event" :chapter="chapter" />
      <div v-if="campaign.data.status == 'Sent'" class="w-full pt-4 space-y-2 sticky bottom-0">
        <ProgressSection :open="open" :campaign-id="campaign.data.name" />
      </div>
      <div
        v-if="campaign.data.status !== 'Sent'"
        class="w-full pt-4 space-y-2 border-t bg-white sticky bottom-0 z-50 -mb-2"
      >
        <ErrorMessage :message="errorMessages" />
        <ManageActions
          :in-update="inUpdate"
          :status="campaign.data.status"
          @update-campaign="manageUpdate"
          @schedule-mail="campaignData.schedule_sending = true"
          @send-now="manageSendNow"
          @send-test="showSendTest = true"
        />
      </div>
    </div>
  </Drawer>
</template>
<script setup>
import Drawer from '@/components/ui/Drawer.vue'
import ManageActions from './ManageActions.vue'
import { createResource, LoadingText, Badge, ErrorMessage, Progress } from 'frappe-ui'
import { computed, ref, watch } from 'vue'
import EmailFormTemplate from './EmailFormTemplate.vue'
import { isEqual, cloneDeep } from 'lodash'
import { validateCampaignFields } from '@/helpers/emailing'
import { toast } from 'vue-sonner'
import SendTestDialog from './SendTestDialog.vue'
import ProgressSection from './ProgressSection.vue'

const props = defineProps({
  campaignId: {
    type: String,
    required: true,
  },
  event: {
    type: String,
    default: '',
  },
  chapter: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update-campaigns'])

const errorMessages = ref('')
const open = defineModel({ type: Boolean })
const inUpdate = ref(false)
const campaignData = ref({})
const showSendTest = ref(false)

const campaign = createResource({
  url: 'fossunited.api.emailing.get_campaign_detail',
  makeParams() {
    return {
      id: props.campaignId,
    }
  },
  onSuccess(data) {
    data.status = getStatus
    campaignData.value = cloneDeep(data)
    return data
  },
})

watch(
  () => props.campaignId,
  (newId) => {
    if (newId) {
      campaign.fetch()
    }
  },
)

watch(
  () => campaignData.value,
  (newData) => {
    inUpdate.value = !isEqual(newData, campaign.data)
  },
  { deep: true },
)

const getStatus = computed(() => {
  if (inUpdate.value) {
    return 'Draft'
  }

  if (campaign.data.email_sent) {
    return 'Sent'
  }
  if (campaign.data.schedule_sending) {
    return 'Scheduled'
  }

  return 'Not Sent'
})

const getBadgeTheme = {
  'Not Sent': 'gray',
  Sent: 'green',
  Scheduled: 'blue',
  Draft: 'red',
}

const updateCampaign = createResource({
  url: 'fossunited.api.emailing.update_campaign',
  makeParams() {
    return {
      campaign_id: campaign.data.name,
      data: campaignData.value,
    }
  },
  onSuccess() {
    errorMessages.value = ''
    campaign.fetch()
    toast.success('Campaign Updated')
    emit('update-campaigns')
  },
  onError(err) {
    errorMessages.value = err.messages
    toast.error(`Error: ${err.messages}`)
  },
})

const manageUpdate = () => {
  const errors = validateCampaignFields(campaignData.value)
  if (errors.length) {
    errorMessages.value = errors.join('\n')
    return
  }

  updateCampaign.fetch()
}

const sendCampaign = createResource({
  url: 'fossunited.api.emailing.send_campaign',
  makeParams() {
    return {
      campaign_id: campaign.data.name,
    }
  },
  onSuccess(data) {
    toast.info('Email queued to be sent')
    campaign.fetch()
  },
  onError(err) {
    toast.error(`Error: ${err.messages}`)
  },
})

const manageSendNow = () => {
  const errors = validateCampaignFields(campaign.data)

  if (errors.length) {
    errorMessages.value = errors.join('\n')
    return
  }

  sendCampaign.fetch()
}
</script>
