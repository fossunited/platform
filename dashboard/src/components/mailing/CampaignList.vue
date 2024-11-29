<!-- eslint-disable vue/no-unused-vars -->
<template>
  <ListView
    class="mt-2"
    :columns="[
      {
        label: 'Subject',
        key: 'subject',
      },
      {
        label: 'Status',
        key: 'status',
      },
      {
        label: 'Last Modified',
        key: 'modified',
      },
    ]"
    :rows="campaigns"
    :options="{
      onRowClick: (row) => emit('row-click', row.name),
      selectable: false,
      emptyState: {
        title: 'No campaigns found',
        description: 'Create a new campaign to get started',
      },
    }"
    row-key="name"
  >
    <template #cell="{ item, row, column }">
      <template v-if="column.key == 'status'">
        <Badge :theme="getBadgeTheme(item)">{{ item }}</Badge>
      </template>
      <template v-else-if="column.key == 'modified'">
        <span class="text-base">
          {{ dayjs(item).fromNow() }}
        </span>
      </template>
      <template v-else>
        <span class="text-base font-medium">{{ item }}</span>
      </template>
    </template>
  </ListView>
</template>
<script setup>
import { ListView, Badge } from 'frappe-ui'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

const emit = defineEmits(['row-click'])

const props = defineProps({
  campaigns: {
    type: Array,
    required: true,
  },
})

function getBadgeTheme(label) {
  if (label == 'Scheduled') {
    return 'blue'
  }
  if (label == 'Sent') {
    return 'green'
  }

  return 'gray'
}
</script>
