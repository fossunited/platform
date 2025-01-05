<template>
  <div class="py-10 px-5 w-full flex justify-center">
    <div v-if="status == 'Accepted'" class="flex flex-col gap-2 items-center justify-center">
      <IconCircleCheckFilled class="w-10 h-10 fill-green-600" />
      <div class="text-center prose">
        <h2>Attendance Confirmed</h2>
        <p>Your Attendance for the Localhost has been confirmed.</p>
      </div>
    </div>
    <div v-else class="flex flex-col gap-2 items-center justify-center">
      <IconCircleXFilled class="w-10 h-10 fill-red-600" />
      <div class="prose text-center">
        <h2>Rejected</h2>
        <p>
          You rejected the attendance confirmation. You will now attend the hackathon remotely.
        </p>
      </div>
    </div>
  </div>
</template>
<script setup>
import { IconCircleCheckFilled, IconCircleXFilled } from '@tabler/icons-vue'
import { defineProps } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true,
  },
})
</script>
