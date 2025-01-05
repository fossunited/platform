<template>
  <Dialog
    v-model="showDialog"
    class="z-50"
    :options="{
      title: 'Sold T-shirt Details',
    }"
  >
    <template #body-content>
      <div class="text-sm">
        <p class="mb-2">T-shirts sold for this event.</p>
      </div>
      <table class="w-3/4 table-fixed text-center">
        <thead class="text-xs text-gray-700 uppercase bg-gray-50">
          <tr>
            <th class="p-2 border">Size</th>
            <th class="p-2 border">Quantity</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(quantity, size) in insight.tshirt_size_count" :key="size">
            <td class="p-2 text-base border">{{ size }}</td>
            <td class="p-2 text-base border">{{ quantity }}</td>
          </tr>
          <tr>
            <td class="p-2 text-base font-semibold">Total</td>
            <td class="p-2 text-base font-semibold">{{ insight.tshirts_sold }}</td>
          </tr>
        </tbody>
      </table>
    </template>
  </Dialog>
  <div class="flex flex-col w-full border rounded-sm p-4">
    <div class="text-sm flex gap-2 items-center uppercase font-semibold">
      <IconShirtFilled class="w-5 h-5" />
      <span> T-shirts Sold </span>
    </div>
    <div class="flex gap-2 items-end justify-between mt-6">
      <div class="prose">
        <h2 class="">{{ insight.tshirts_sold }}</h2>
      </div>
      <Button class="w-fit" label="View Details" @click="showDialog = true" />
    </div>
  </div>
</template>
<script setup>
import { Dialog } from 'frappe-ui'
import { defineProps, ref } from 'vue'
import { IconShirtFilled } from '@tabler/icons-vue'

const showDialog = ref(false)

const props = defineProps({
  insight: {
    type: Object,
    required: true,
  },
})
</script>
