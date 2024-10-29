<template>
  <div v-if="cfpSubmissions.data">
    <div class="flex flex-col gap-2">
      <div class="text-base font-medium">Filters</div>
      <div class="flex justify-between">
        <div class="flex gap-4 mb-5">
          <div class="flex gap-2 items-center">
            <label class="text-sm">Status:</label>
            <select
              v-model="selectedStatusFilter"
              class="border-none text-sm px-4 rounded w-44 h-fit items-center flex flex-col bg-gray-100 border-2"
            >
              <option
                v-for="(filter, index) in statusFilters"
                :key="index"
                @click="filterByStatus(filter)"
              >
                {{ filter.label }}
              </option>
            </select>
          </div>
          <div v-if="selectedStatusFilter == 'Reviewed'" class="flex gap-2 items-center">
            <label class="text-sm">Review Filter:</label>
            <select
              v-model="selectedToApproveFilter"
              class="border-none text-sm px-4 rounded w-44 h-fit items-center flex flex-col bg-gray-100 border-2"
            >
              <option
                v-for="(filter, index) in toApproveFilter"
                :key="index"
                @click="filterByToApprove(filter)"
              >
                {{ filter.label }}
              </option>
            </select>
          </div>
        </div>
        <RefreshButton :in-spin="cfpSubmissions.loading" @click="cfpSubmissions.fetch" />
      </div>
    </div>
    <ListView
      class="h-[480px]"
      :columns="[
        {
          label: 'Talk Title',
          key: 'talk_title',
        },
        {
          label: 'Status',
          key: 'review_status',
          width: 1 / 2,
        },
        {
          label: 'Review',
          key: 'reviewer_status',
        },
        {
          label: 'Remarks',
          key: 'reviewer_remarks',
        },
      ]"
      :rows="cfpSubmissions.data"
      row-key="name"
      :options="{
        selectable: false,
        showTooltip: true,
        resizeColumn: true,
        onRowClick: (row) => openSubmission(row),
        emptyState: {
          title: 'No Submissions',
          description: 'No submissions found.',
        },
      }"
    >
      <template #cell="{ item, column }">
        <div v-if="column.label == 'Status'">
          <Badge :theme="item == 'Reviewed' ? 'blue' : 'gray'" :label="item" />
        </div>
        <div v-else-if="column.label == 'Review'">
          <Badge
            v-if="item"
            :theme="
              item == 'Yes' ? 'green' : item == 'Maybe' ? 'orange' : item == 'No' ? 'red' : 'gray'
            "
          >
            {{ { Yes: 'Approved', No: 'Reject', Maybe: 'Not Sure' }[item] }}
          </Badge>
          <div v-else class="text-sm text-gray-500">-</div>
        </div>
        <div v-else-if="column.label == 'Remarks'">
          <div v-if="item" class="text-sm truncate">{{ item }}</div>
          <div v-else class="text-sm text-gray-500">-</div>
        </div>
        <div v-else class="text-base truncate">
          {{ item }}
        </div>
      </template>
    </ListView>
  </div>
</template>
<script setup>
import { defineProps, ref } from 'vue'
import { createResource, ListView, Badge } from 'frappe-ui'
import { useRouter } from 'vue-router'
import RefreshButton from '@/components/RefreshButton.vue'

const router = useRouter()

const props = defineProps({
  event: {
    type: String,
    required: true,
  },
})

const statusFilters = [
  {
    label: 'All',
    value: ['Reviewed', 'Not Reviewed'],
  },
  {
    label: 'Reviewed',
    value: ['Reviewed'],
  },
  {
    label: 'Not Reviewed',
    value: ['Not Reviewed'],
  },
]

const toApproveFilter = [
  {
    label: 'All',
    value: ['Yes', 'No', 'Maybe'],
  },
  {
    label: 'Approved',
    value: ['Yes'],
  },
  {
    label: 'Rejected',
    value: ['No'],
  },
  {
    label: 'Not Sure',
    value: ['Maybe'],
  },
]

const openSubmission = (row) => {
  let routeData = router.resolve({
    name: 'SubmissionPage',
    params: {
      talk_id: row.name,
    },
  })
  window.open(routeData.href, '_blank')
}

const selectedStatusFilter = ref(statusFilters[0].label)
const selectedToApproveFilter = ref(toApproveFilter[0].label)

const cfpSubmissions = createResource({
  url: 'fossunited.api.reviewer.get_cfp_submissions_by_reviewer_status',
  params: {
    event: props.event,
  },
  auto: true,
  transform(data) {
    let groups = [
      {
        group: 'Open for reviews',
        rows: [],
      },
      {
        group: 'Selected Talks',
        rows: [],
      },
      {
        group: 'Rejected Talks',
        collapsed: true,
        rows: [],
      },
    ]
    data.forEach((item) => {
      if (item.status === 'Review Pending') {
        groups[0]['rows'].push(item)
      } else if (item.status === 'Rejected') {
        groups[2]['rows'].push(item)
      } else {
        groups[1]['rows'].push(item)
      }
    })

    return groups
  },
})

const filterByStatus = (filter) => {
  selectedToApproveFilter.value = toApproveFilter[0].label
  cfpSubmissions.update({
    params: {
      event: props.event,
      status_filter: filter.value,
    },
  })
  cfpSubmissions.fetch()
}

const filterByToApprove = (filter) => {
  cfpSubmissions.update({
    params: {
      event: props.event,
      status_filter: ['Reviewed'],
      to_approve_filter: filter.value,
    },
  })
  cfpSubmissions.fetch()
}
</script>
