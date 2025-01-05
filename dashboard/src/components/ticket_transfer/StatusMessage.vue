<template>
  <div class="py-10 px-5 w-full flex justify-center">
    <div
      v-if="status == 'Approved' || status == 'Already Approved'"
      class="flex flex-col items-center gap-2"
    >
      <IconCircleCheckFilled class="w-10 h-10 fill-green-600" />
      <div class="prose text-center">
        <div v-if="status == 'Approved'">
          <h2 class="my-3">Ticket Transferred Successfully!</h2>
          <p>
            Your ticket has been successfully transferred to the new owner.<br />
            An email has been sent to the new ticket holder.
          </p>
        </div>
        <div v-else-if="status == 'Already Approved'">
          <h2 class="my-3">Ticket Already Transferred!</h2>
          <p>
            Your ticket has already been transferred to the new owner.<br />
            An email has been sent to the new ticket holder.
          </p>
        </div>
      </div>
    </div>
    <div
      v-else-if="status == 'Rejected' || status == 'Already Rejected'"
      class="flex flex-col text-center items-center"
    >
      <IconCircleXFilled class="w-10 h-10 fill-red-600" />
      <div class="prose">
        <div v-if="status == 'Rejected'">
          <h2 class="my-3">Transfer Rejected!</h2>
          <p>
            Your ticket transfer request has been rejected.<br />
            For further assistance, please send a mail at
            <a href="mailto:indiafoss@fossunited.org" class="underline">indiafoss@fossunited.org</a
            >.
          </p>
        </div>
        <div v-else-if="status == 'Already Rejected'">
          <h2 class="my-3">Transfer Already Rejected!</h2>
          <p>
            Your ticket transfer request has already been rejected.<br />
            For further assistance, please send a mail at
            <a href="mailto:indiafoss@fossunited.org">indiafoss@fossunited.org</a>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { defineProps } from 'vue'
import { IconCircleCheckFilled, IconCircleXFilled } from '@tabler/icons-vue'

const props = defineProps({
  status: {
    type: String,
    required: true,
  },
})
</script>
