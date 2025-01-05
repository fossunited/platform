<template>
  <div class="flex flex-col w-full border rounded-sm p-4">
    <div class="text-sm uppercase font-semibold">{{ tier.title }}</div>
    <div class="flex gap-2 items-end justify-between mt-6">
      <div>
        <div class="prose">
          <h2 class="">{{ tier.total_sold }}</h2>
        </div>
        <span v-if="tier.tier_capacity" class="text-sm text-gray-600 mb-1"
          >out of {{ tier.tier_capacity }}</span
        >
      </div>
      <div
        class="flex items-center gap-1 text-sm mt-1 font-medium p-1 w-fit rounded-sm px-2"
        :class="
          tier.tickets_sold_today === 0
            ? 'bg-gray-100 text-gray-600'
            : 'bg-green-100 text-green-600'
        "
      >
        <IconArrowNarrowUp v-if="tier.tickets_sold_today" class="w-4 h-4 -mx-1" />
        <span>{{ tier.tickets_sold_today }}</span>
        <span>sold today</span>
      </div>
    </div>
  </div>
</template>
<script setup>
import { defineProps } from 'vue'
import { IconArrowNarrowUp } from '@tabler/icons-vue'

const props = defineProps({
  tier: {
    type: Object,
    required: true,
  },
})
</script>
