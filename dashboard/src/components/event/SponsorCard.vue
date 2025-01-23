<template>
  <Dialog
    v-model="showConfimation"
    class="z-50"
    :options="{
      title: 'Remove Sponsor?',
      message: `Are you sure you want to remove sponsor - ${sponsor.sponsor_name} ?`,
      icon: {
        name: 'alert-triangle',
        appearance: 'warning',
      },
      actions: [
        {
          label: 'Cancel',
          onClick: () => (showConfimation = false),
        },
        {
          label: 'Remove',
          theme: 'red',
          onClick: handleDelete,
        },
      ],
    }"
  />
  <div class="border p-4 flex flex-col gap-2 rounded items-center">
    <div class="relative w-full">
      <div v-if="editable" class="top-0 right-0 absolute flex flex-row-reverse gap-2 w-full">
        <Button icon="trash" theme="red" @click="showConfimation = true" />
        <Button icon="edit" @click="emit('edit-sponsor')" />
      </div>
      <img
        :src="sponsor.image"
        class="w-full h-20 px-5 object-contain"
        :alt="label || 'Image preview'"
      />
    </div>
    <h4 class="text-md font-medium">{{ sponsor.sponsor_name }}</h4>
    <p class="text-base text-gray-700">
      {{ sponsor.tier == 'Custom' ? sponsor.custom_tier : sponsor.tier }}
    </p>
  </div>
</template>
<script setup>
import { inject, ref } from 'vue'
import { toast } from 'vue-sonner'
import { Dialog } from 'frappe-ui'

const showConfimation = ref(false)
const event = inject('event')

const emit = defineEmits(['edit-sponsor', 'reload:event'])

const props = defineProps({
  sponsor: {
    type: Object,
    required: true,
  },
  editable: {
    type: Boolean,
    default: () => true,
  },
})

const handleDelete = () => {
  toast.info('Removing sponsor...')
  event.setValue
    .submit({
      sponsor_list: event.doc.sponsor_list.filter((s) => s.name !== props.sponsor.name),
    })
    .then(() => {
      toast.info('Sponsor removed successfully')
      emit('reload:event')
      showConfimation.value = false
    })
    .catch((err) => {
      toast.error('Failed to remove sponsor' + err)
    })
}
</script>
