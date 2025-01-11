<template>
  <Dialog
    :options="{
      title: 'Add New Member',
    }"
  >
    <template #body-content>
      <div class="flex flex-col gap-2">
        <div class="text-p-base text-gray-700">
          Enter the username of the new member you want to add to the team.
        </div>
        <Autocomplete
          v-model="newMembers"
          :options="memberOptions.data"
          placeholder="Search for a user"
          :multiple="true"
        >
          <template #item-prefix="{ option }">
            <Avatar shape="circle" :image="option.avatar" :label="option.label" size="lg" />
          </template>
        </Autocomplete>
      </div>
    </template>
    <template #actions>
      <div class="grid grid-cols-2 gap-3">
        <Button label="Cancel" @click="$emit('close-dialog')" />
        <Button label="Add" variant="solid" @click="$emit('update:add-member', newMembers)" />
      </div>
    </template>
  </Dialog>
</template>
<script setup>
import { Dialog, Autocomplete, createResource, Avatar } from 'frappe-ui'
import { ref, defineProps, defineEmits, computed } from 'vue'

const props = defineProps({
  chapter: {
    type: Object,
    default: () => null,
  },
  event: {
    type: Object,
    default: () => null,
  },
})

const existingMembers = computed(() => {
  if (props.chapter) {
    return props.chapter.doc.chapter_members.map((member) => member.chapter_member).join(',')
  } else if (props.event) {
    return props.event.doc.event_members.map((member) => member.member).join(',')
  }

  return []
})

const emits = defineEmits(['update:add-member', 'close-dialog'])

const memberOptions = createResource({
  url: 'fossunited.api.dashboard.get_user_profile_list',
  makeParams() {
    return {
      filters: {
        name: ['not in', existingMembers.value],
      },
    }
  },
  auto: true,
  realtime: true,
  transform(data) {
    return data.map((user) => {
      return {
        value: user.name,
        label: user.username,
        description: user.full_name,
        avatar: user.profile_photo
          ? user.profile_photo
          : '/assets/fossunited/images/defaults/user_profile_image.png',
      }
    })
  },
})

const newMembers = ref([])
</script>
