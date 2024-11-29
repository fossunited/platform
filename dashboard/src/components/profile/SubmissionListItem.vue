<template>
  <div
    class="p-4 border-b first:border-t border-gray-500 w-full flex flex-col gap-3 hover:cursor-pointer hover:bg-gray-50"
    @click="redirectRoute(proposal.route)"
  >
    <h4 class="text-base font-medium">{{ proposal.talk_title }}</h4>
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-2">
      <div class="flex flex-wrap gap-2 items-center divide-x-2 text-gray-800">
        <Badge class="!rounded-sm" :theme="getTheme[proposal.status]">{{ proposal.status }}</Badge>
        <span class="text-sm uppercase pl-2">{{ proposal.event_name }}</span>
        <span class="text-sm uppercase pl-2">{{ proposal.chapter }}</span>
      </div>
      <span class="text-xs text-gray-600">{{ getFormattedModified(proposal.modified) }}</span>
    </div>
  </div>
</template>
<script setup>
import { Badge } from 'frappe-ui'
import { redirectRoute } from '@/helpers/utils'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
dayjs.extend(relativeTime)

const props = defineProps({
  proposal: {
    type: Object,
    required: true,
  },
})

const getTheme = {
  'Review Pending': 'orange',
  Approved: 'green',
  Rejected: 'red',
  Screening: 'blue',
}

const getFormattedModified = (date) => {
  let fromNow = dayjs(date).fromNow()

  // Extract the number and first letter of the time unit
  const match = fromNow.match(/(\d+)\s*(\w)/)

  if (match) {
    const [, number, unit] = match
    return `${number}${unit.charAt(0)}`
  }

  return 'now'
}
</script>
