<template>
  <div class="flex bg-gray-50 flex-col gap-4 w-full h-screen items-center py-12">
    <IconCircleDashedCheck class="w-20 h-20 stroke-green-600" />
    <div class="prose">
      <h2 class="text-gray-700">Transfer Initiated</h2>
    </div>

    <div class="shadow-lg w-2/5 rounded bg-white text-center px-4 py-6">
      <p>
        Ticket Transfer has been initiated. <br /><br />
        An email has been sent to the ticket holder.
        <br />
        On approval, the ticket will be transferred to the new owner.
        <br />
        <br />
        For further assistance, send an email to
        <a class="underline" href="mailto:team@fossunited.org">team@fossunited.org</a>
      </p>
    </div>
  </div>
</template>
<script setup>
import { IconCircleDashedCheck } from '@tabler/icons-vue'
</script>
