<template>
  <Dialog
    v-model="showDialog"
    class="z-50"
    :options="{
      title: 'Change Mode of Attendance',
    }"
  >
    <template #body-content>
      <div
        class="flex flex-col gap-2 items-center text-center p-3 rounded w-full bg-orange-50 text-orange-600 border-2 border-dashed border-orange-600 text-xs"
      >
        <IconAlertCircle />
        <p>
          <b>Attention!</b> You are about to change your attendance mode for this hackathon.<br /><br />
          Please note that requests for in-person attendance are subject to approval by the
          organizers due to limited on-site availability.
        </p>
      </div>
      <FormControl
        v-model="attendanceMode"
        label="Mode of Attendance"
        type="select"
        class="mt-4"
        :options="attendanceModeOptions"
      />
      <FormControl
        v-if="attendanceMode == 'local'"
        v-model="participant_localhost.data.localhost_name"
        label="Your Localhost"
        :disabled="1"
        class="mt-4"
      />
      <div v-if="attendanceMode == 'local-pending'">
        <FormControl
          v-if="localhosts.data.length > 0"
          v-model="selectedLocalhost"
          label="Select LocalHost"
          type="select"
          class="mt-4"
          :options="
            localhosts.data.map((localhost) => ({
              label: `${localhost.localhost_name}`,
              value: localhost.name,
            }))
          "
        />
        <div v-else class="mt-2 text-sm text-red-500">
          <span>No LocalHost slots available at this moment.</span>
        </div>
      </div>
      <ErrorMessage :message="errorMessage" class="mt-2" />
    </template>
    <template #actions>
      <div class="grid grid-cols-2 gap-4">
        <Button label="Cancel" size="sm" theme="gray" @click="showDialog = false" />
        <Button
          label="Change"
          size="sm"
          theme="green"
          :disabled="handleDisabled()"
          @click="handleAttendanceModeChange"
        />
      </div>
    </template>
  </Dialog>
  <div
    class="flex flex-col gap-1 border-2 rounded border-gray-500 border-dashed min-w-[220px] p-4"
  >
    <h5 class="text-xs text-gray-700 uppercase font-medium">Your Mode of attendance</h5>
    <div class="flex w-full items-center justify-between">
      <div
        class="text-base font-medium"
        :class="attendanceMode == 'local-pending' ? 'text-orange-600' : ''"
      >
        {{
          attendanceMode == 'remote'
            ? 'Remote'
            : attendanceMode == 'local-pending'
              ? `${participant_localhost.data?.localhost_name} - On-Site (Pending Request)`
              : `${participant_localhost.data?.localhost_name} - On-Site`
        }}
      </div>
      <Button
        v-if="hackathon.data.has_localhosts"
        label="Change"
        size="sm"
        class="w-fit !text-sm"
        @click="showDialog = true"
      />
    </div>
  </div>
</template>
<script setup>
import { createResource, createListResource, Dialog, FormControl, ErrorMessage } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { defineProps, ref } from 'vue'
import { toast } from 'vue-sonner'
import { IconAlertCircle } from '@tabler/icons-vue'

const route = useRoute()
const showDialog = ref(false)
const attendanceMode = ref(null)
const selectedLocalhost = ref(null)
const attendanceModeOptions = [
  {
    label: 'Remote',
    value: 'remote',
  },
]

const originalAttendanceMode = ref(null)
const originalLocalhost = ref(null)

const props = defineProps({
  hackathon: {
    type: Object,
    required: true,
  },
})

const participant_localhost = createResource({
  url: 'frappe.client.get',
  makeParams() {
    return {
      doctype: 'FOSS Hackathon LocalHost',
      name: participant.data.localhost,
    }
  },
})

const participant = createResource({
  url: 'fossunited.api.hackathon.get_session_participant',
  makeParams() {
    return {
      hackathon: props.hackathon.data.name,
    }
  },
  auto: true,
  onSuccess(data) {
    setAttendanceMode(data)
    participant_localhost.fetch()
  },
})

const setAttendanceMode = (data) => {
  if (data.wants_to_attend_locally) {
    if (data.localhost_request_status == 'Accepted') {
      attendanceMode.value = 'local'
      originalAttendanceMode.value = 'local'
      originalLocalhost.value = data.localhost
      attendanceModeOptions.push({
        label: 'On-site',
        value: 'local',
      })
      attendanceModeOptions.push({
        label: 'Change Localhost Venue',
        value: 'local-pending',
      })
      return
    } else {
      selectedLocalhost.value = data.localhost
      attendanceMode.value = 'local-pending'
      originalAttendanceMode.value = 'local-pending'
      originalLocalhost.value = data.localhost
      attendanceModeOptions.push({
        label: 'Pending On-site Request',
        value: 'local-pending',
      })
      return
    }
  }
  attendanceModeOptions.push({
    label: 'Request In-Person Attendance',
    value: 'local-pending',
  })
  attendanceMode.value = 'remote'
  originalAttendanceMode.value = 'remote'
}

const localhosts = createListResource({
  doctype: 'FOSS Hackathon LocalHost',
  filters: {
    parent_hackathon: props.hackathon.data.name,
    is_accepting_attendees: 1,
  },
  fields: ['localhost_name', 'name', 'city', 'state', 'location', 'map_link'],
  auto: true,
})

const handleDisabled = () => {
  if (attendanceMode.value == originalAttendanceMode.value) {
    if (attendanceMode.value == 'local' || attendanceMode.value == 'local-pending') {
      return selectedLocalhost.value == originalLocalhost.value
    }
    return true
  }
  return false
}

const errorMessage = ref('')

const updateParticipantLocalhost = (localhost) => {
  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'FOSS Hackathon Participant',
      name: participant.data.name,
      fieldname: {
        wants_to_attend_locally: 1,
        localhost: localhost,
      },
    },
    auto: true,
    onSuccess(data) {
      participant.fetch()
      showDialog.value = false
      errorMessage.value = ''
      toast.success('Attendance mode updated successfully!')
    },
    onError(err) {
      toast.error('Failed to update attendance mode.' + err.message)
    },
  })
}

const makeParticipantRemote = () => {
  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'FOSS Hackathon Participant',
      name: participant.data.name,
      fieldname: {
        wants_to_attend_locally: 0,
        localhost: null,
      },
    },
    auto: true,
    onSuccess(data) {
      showDialog.value = false
      errorMessage.value = ''
      toast.success('Attendance mode updated successfully!')
    },
    onError(err) {
      toast.error('Failed to update attendance mode.' + err.message)
    },
  })
}

const handleAttendanceModeChange = () => {
  if (attendanceMode.value == 'local-pending' && selectedLocalhost.value == null) {
    errorMessage.value = 'Please select a LocalHost'
    return
  }

  if (attendanceMode.value == 'local-pending') {
    updateParticipantLocalhost(selectedLocalhost.value)
    return
  }

  if (attendanceMode.value == 'remote') {
    makeParticipantRemote()
  }
}
</script>
