<template>
  <TransitionRoot
    :show="inUpdate"
    enter="ease-in-out transition-all duration-300"
    enter-from="opacity-0 translate-y-4"
    enter-to="opacity-100 translate-y-0"
    leave="ease-in-out transition-all duration-300"
    leave-from="opacity-100 translate-y-0"
    leave-to="opacity-0 translate-y-4"
  >
    <Button
      v-if="inUpdate"
      label="Update"
      class="w-full"
      variant="solid"
      @click="$emit('update-campaign')"
    />
  </TransitionRoot>
  <TransitionRoot
    :show="!inUpdate"
    enter="ease-in-out transition-all duration-300"
    enter-from="opacity-0 translate-y-4"
    enter-to="opacity-100 translate-y-0"
    leave="ease-in-out transition-all duration-300"
    leave-from="opacity-100 translate-y-0"
    leave-to="opacity-0 translate-y-4"
  >
    <Popover v-if="!inUpdate">
      <template #target="{ togglePopover }">
        <Button variant="solid" label="Send" class="w-full" @click="togglePopover()" />
      </template>
      <template #body-main="{ togglePopover }">
        <div class="p-2 text-white rounded-sm flex flex-col gap-2 items-center">
          <Button
            v-for="(option, key) in sendOptions"
            :key="key"
            :label="option.label"
            :onclick="
              () => {
                togglePopover()
                option.onclick()
              }
            "
            class="w-full"
            variant="ghost"
          />
        </div>
      </template>
    </Popover>
  </TransitionRoot>
</template>
<script setup>
import { TransitionRoot } from '@headlessui/vue'
import { Popover } from 'frappe-ui'
import { computed } from 'vue'

const props = defineProps({
  inUpdate: {
    type: Boolean,
    required: true,
  },
  status: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['update-campaign', 'send-now', 'send-test', 'schedule-mail'])

const sendOptions = computed(() => {
  let options = [
    {
      label: 'Send Test Mail',
      onclick: () => {
        emit('send-test')
      },
    },
  ]

  if (props.status != 'Scheduled') {
    options.push({
      label: 'Schedule Sending',
      onclick: () => {
        emit('schedule-mail')
      },
    })
  }

  options.push({
    label: 'Send Now',
    onclick: () => {
      emit('send-now')
    },
  })

  return options
})
</script>
