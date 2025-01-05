<template>
  <div class="prose mt-4">
    <h2>{{ localhost.localhost_name }}</h2>
  </div>
  <div class="flex gap-2 my-2 text-base font-medium items-center">
    <div class="flex gap-1 items-center">
      <IconMapPin class="w-5 h-5" />
      <span>
        {{ localhost.location }}
      </span>
    </div>
  </div>
</template>
<script setup>
import { IconMapPin } from '@tabler/icons-vue'
import { defineProps } from 'vue'

const props = defineProps({
  localhost: {
    type: Object,
    required: true,
  },
})
</script>
