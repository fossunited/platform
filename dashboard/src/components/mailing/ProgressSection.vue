<template>
  <TransitionRoot
    v-if="stats.data"
    :show="stats.data.sent !== stats.data.total"
    as="div"
    enter="ease-in-out transition-all duration-300"
    enter-from="opacity-0 -translate-y-12"
    enter-to="opacity-100 translate-y-0"
    leave="ease-in-out transition-all duration-1000"
    leave-from="opacity-100 translate-y-0"
    leave-to="opacity-0 -translate-y-12"
  >
    <Progress
      :value="interpolatedProgress"
      class="border rounded p-4"
      label="Sending Progress"
      :hint="true"
    />
  </TransitionRoot>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { createResource, Progress } from 'frappe-ui'
import { TransitionRoot } from '@headlessui/vue'

const props = defineProps({
  campaignId: {
    type: String,
    required: true,
  },
  open: {
    type: Boolean,
    default: false,
  },
})

const currentProgress = ref(0)

const stats = createResource({
  url: 'fossunited.api.emailing.get_sending_status',
  makeParams() {
    return {
      campaign_id: props.campaignId,
    }
  },
  onSuccess(data) {
    if (data.sent == data.total) {
      currentProgress.value = 100
      return
    }

    // Smoothly interpolate to the new progress value
    animateProgress(data.sent, data.total)

    // Continue fetching if not complete
    if (data.sent < data.total && props.open) {
      stats.fetch()
    }
  },
  debounce: 1000,
  auto: true,
})

const interpolatedProgress = computed(() => Math.round(currentProgress.value))

function animateProgress(sent, total) {
  const targetProgress = (sent * 100) / total
  const steps = 20 // Number of steps for smooth animation
  const currentValue = currentProgress.value

  const stepSize = (targetProgress - currentValue) / steps

  function updateProgress(step = 0) {
    if (step < steps) {
      currentProgress.value = Math.min(100, currentValue + stepSize * (step + 1))

      // Use requestAnimationFrame for smooth animation
      requestAnimationFrame(() => updateProgress(step + 1))
    } else {
      currentProgress.value = targetProgress
    }
  }

  updateProgress()
}
</script>
