<template>
  <img
    v-if="hackathon.data.hackathon_banner && showBanner"
    :src="hackathon.data.hackathon_banner"
    alt=""
    class="w-full h-32 md:h-full md:max-h-72 object-cover rounded-sm"
  />
  <img :src="hackathon.data.hackathon_logo" alt="Logo" class="h-10 md:h-14 mt-6 mb-4" />
  <div
    class="flex gap-4 items-center rounded-sm w-fit py-2 mt-4 font-medium text-base text-gray-900 stroke-gray-900"
  >
    <div class="flex gap-1 justify-center items-center">
      <IconMapPinCode v-if="hackathon.data.hackathon_type == 'In-Person'" />
      <IconWorld v-else />
      <span>{{ hackathon.data.hackathon_type }}</span>
    </div>
    <div>|</div>
    <div class="flex gap-1 justify-center items-center">
      <div>
        {{ formatDate(hackathon.data.start_date) }}
      </div>
      <div v-if="hackathon.data.start_date != hackathon.data.end_date" class="flex gap-1">
        <span>-</span>
        <span>
          {{ formatDate(hackathon.data.end_date) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { IconMapPinCode, IconWorld } from '@tabler/icons-vue'
import { defineProps } from 'vue'

defineProps({
  hackathon: {
    type: Object,
    default: () => ({}),
  },
  showBanner: {
    type: Boolean,
    default: true,
  },
})

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}
</script>
