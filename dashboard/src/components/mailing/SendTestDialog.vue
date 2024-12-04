<template>
  <Dialog
    v-model="open"
    class="z-[70]"
    :options="{
      title: inSuccess ? ' ' : 'Send Test Mail',
      actions: getActions,
    }"
  >
    <template #body-content>
      <TransitionRoot
        :show="!inSuccess"
        enter="ease-in-out transition-all duration-500"
        enter-from="opacity-0 -translate-x-12"
        enter-to="opacity-100 translate-x-0"
        leave="ease-in-out transition-all duration-500"
        leave-from="opacity-100 translate-x-0"
        leave-to="opacity-0 -translate-x-12"
      >
        <FormControl
          v-if="!inSuccess"
          v-model="email"
          type="email"
          :required="true"
          placeholder="test@example.com"
          label="Email"
        />
        <ErrorMessage :message="errorMessages" class="mt-2" />
      </TransitionRoot>
      <TransitionRoot
        :show="inSuccess"
        enter="ease-in-out transition-all duration-500"
        enter-from="opacity-0 translate-x-12"
        enter-to="opacity-100 translate-x-0"
        leave="ease-in-out transition-all duration-500"
        leave-from="opacity-100 translate-x-0"
        leave-to="opacity-0 translate-x-12"
      >
        <div v-if="inSuccess" class="flex items-center flex-col gap-2">
          <SuccessIcon class="w-10 h-10" />
          <p class="text-base">
            Test email successfully sent to <span class="font-semibold">{{ email }}</span>
          </p>
        </div>
      </TransitionRoot>
    </template>
  </Dialog>
</template>
<script setup>
import { createResource, Dialog, FormControl, ErrorMessage } from 'frappe-ui'
import { ref, computed } from 'vue'
import { toast } from 'vue-sonner'
import { TransitionRoot } from '@headlessui/vue'
import SuccessIcon from '@/components/icons/SuccessIcon.vue'

const open = defineModel({ type: Boolean, required: true })

const errorMessages = ref('')
const inSuccess = ref(false)
const email = ref('')

const props = defineProps({
  campaignId: {
    type: String,
    required: true,
  },
})

const getActions = computed(() => {
  if (inSuccess.value) {
    return [
      {
        label: 'Send More',
        onclick: (event) => {
          event.stopImmediatePropagation()
          email.value = ''
          inSuccess.value = false
        },
      },
    ]
  }

  return [
    {
      label: 'Send',
      variant: 'solid',
      onclick: (event) => {
        event.stopImmediatePropagation()
        manageTest()
      },
    },
  ]
})

const sendTest = createResource({
  url: 'fossunited.api.emailing.send_test_email',
  makeParams() {
    return {
      campaign_id: props.campaignId,
      email: email.value,
    }
  },
  onSuccess() {
    errorMessages.value = ''
    inSuccess.value = true
  },
  onError(err) {
    toast.error(err.messages)
  },
})

const manageTest = () => {
  const errors = []

  if (!email.value) {
    errors.push('Email is required')
  }

  if (email.value && !email.value.match(/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/)) {
    errors.push('Please enter a valid email address')
  }

  if (errors.length) {
    errorMessages.value = errors.join('\n')
    return
  }

  sendTest.fetch()
}
</script>
