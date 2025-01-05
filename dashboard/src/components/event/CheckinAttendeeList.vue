<template>
  <CheckinConfirmationDialog
    v-model="showConfirmDialog"
    :selected-attendee="selectedAttendee"
    :attendees="attendees"
  />
  <CheckinManageDialog
    v-model="showManageDialog"
    :selected-attendee="selectedAttendee"
    :attendees="attendees"
  />

  <!-- Attendee List -->
  <div v-if="attendees.data">
    <ListView
      :columns="[
        { label: 'Name', key: 'full_name' },
        { label: 'Ticket ID', key: 'name' },
        { label: 'Bought Tshirt?', key: 'wants_tshirt', width: '150px' },
        { label: 'Tshirt Delivered?', key: 'tshirt_delivered', width: '150px' },
        { label: 'Check-in Status', key: 'checkin_status', width: 1.5 },
        { label: 'Actions', key: 'action' },
      ]"
      :rows="attendees.data"
      :options="{
        selectable: false,
        showTooltip: false,
        resizeColumn: true,
        emptyState: {
          title: 'No attendees found',
        },
      }"
      row-key="name"
    >
      <template #cell="{ item, row, column }">
        <template v-if="column.key === 'action'">
          <Button
            v-if="!isCheckedInToday(row)"
            class="w-fit"
            label="Check-in"
            variant="solid"
            @click="
              () => {
                selectedAttendee = row
                showConfirmDialog = true
              }
            "
          />
          <Button
            v-else
            class="w-fit"
            label="Manage"
            @click="
              () => {
                selectedAttendee = row
                showManageDialog = true
              }
            "
          />
        </template>
        <template v-else-if="column.key === 'wants_tshirt' || column.key === 'tshirt_delivered'">
          <Checkbox :model-value="Boolean(item)" :disabled="true" class="w-4 h-4" />
        </template>
        <template v-else-if="column.key === 'name'">
          <span class="font-mono text-sm font-semibold text-gray-800">{{ item }}</span>
        </template>
        <template v-else-if="column.key === 'checkin_status'">
          <div class="flex items-center overflow-hidden overflow-x-visible flex-wrap">
            <span
              v-for="(data, index) in row.checkin_data"
              :key="index"
              class="flex items-center p-1 rounded-sm"
            >
              <Tooltip arrow-class="fill-black" :placement="'top'" :hover-delay="0.5">
                <template #body>
                  <span class="text-xs bg-gray-900 text-white px-2 py-1 rounded-full">
                    {{ getFormattedDateTime(data.check_in_time) }}
                  </span>
                </template>
                <Badge
                  :theme="getRelativeTime(data.check_in_time) == 'Today' ? 'green' : 'gray'"
                  class="flex gap-1 items-center"
                >
                  <IconChecks class="w-4 h-4" />
                  <span>{{ getRelativeTime(data.check_in_time) }}</span>
                </Badge>
              </Tooltip>
            </span>
          </div>
        </template>
        <template v-else>
          <span class="text-base">
            {{ item }}
          </span>
        </template>
      </template>
    </ListView>
  </div>
  <div v-else>
    <LoadingText />
  </div>
</template>
<script setup>
import { ref, defineProps, provide } from 'vue'
import { LoadingText, ListView, Badge, Tooltip, Checkbox } from 'frappe-ui'
import CheckinManageDialog from '@/components/event/CheckinManageDialog.vue'
import CheckinConfirmationDialog from '@/components/event/CheckinConfirmationDialog.vue'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import isToday from 'dayjs/plugin/isToday'
import isYesterday from 'dayjs/plugin/isYesterday'
import { IconChecks } from '@tabler/icons-vue'

dayjs.extend(relativeTime)
dayjs.extend(isToday)
dayjs.extend(isYesterday)

const props = defineProps({
  event: {
    type: Object,
    required: true,
  },
  attendees: {
    type: Object,
    required: true,
  },
})

const selectedAttendee = ref(null)
const showConfirmDialog = ref(false)
const showManageDialog = ref(false)

const isCheckedInToday = (attendee) => {
  return attendee.checkin_data.some((data) => dayjs(data.check_in_time).isToday())
}

provide('isCheckedInToday', isCheckedInToday)

const getFormattedDateTime = (datetime) => {
  return dayjs(datetime).format('DD MMM, hh:mm A')
}

const getRelativeTime = (datetime) => {
  const date = dayjs(datetime)
  if (date.isToday()) {
    return 'Today'
  } else if (date.isYesterday()) {
    return 'Yesterday'
  } else {
    return date.fromNow()
  }
}
</script>
