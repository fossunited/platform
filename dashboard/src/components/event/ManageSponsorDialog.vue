<template>
  <Dialog
    v-model="show"
    :options="{
      title: isNew ? 'Add Sponsor' : 'Manage Sponsor',
    }"
  >
    <template #body-content>
      <div class="flex flex-col gap-3">
        <FormControl
          v-model="sponsor.tier"
          label="Sponsorship Tier"
          type="select"
          :options="sponsorOptions"
          required
        />
        <FormControl
          v-if="sponsor.tier === 'Custom'"
          v-model="sponsor.custom_tier"
          label="Custom Tier"
          :required="sponsor.tier === 'Custom'"
        />
        <FormControl v-model="sponsor.sponsor_name" label="Sponsor Name" required />
        <FormControl v-model="sponsor.link" label="Website Link" type="url" required>
          <template #prefix>
            <IconLink class="w-4" />
          </template>
        </FormControl>
        <FileUploaderArea v-model="sponsor.image" label="Sponsor Image" />
        <ErrorMessage :message="errorMessages" class="text-sm -mb-4" />
      </div>
    </template>
    <template #actions>
      <div class="grid grid-flow-col w-full">
        <Button v-if="isNew" label="Add" variant="solid" @click="addSponsor" />
        <Button v-else label="Update" variant="solid" @click="handleSponsorUpdate" />
      </div>
    </template>
  </Dialog>
</template>
<script setup>
import { toast } from 'vue-sonner'
import { inject, ref } from 'vue'
import { Dialog, FormControl, ErrorMessage, createResource } from 'frappe-ui'
import { IconLink } from '@tabler/icons-vue'
import FileUploaderArea from '@/components/ui/FileUploaderArea.vue'

const sponsorOptions = ref(['Platinum', 'Gold', 'Silver', 'Bronze', 'Venue Partner', 'Custom'])

const event = inject('event')
const errorMessages = ref('')

const show = defineModel('show', { required: true, type: Boolean, default: false })
const sponsor = defineModel('sponsor', { required: true, type: Object })
const props = defineProps({
  isNew: {
    default: false,
    type: Boolean,
  },
})
const emit = defineEmits(['reload:event'])

const validateFields = () => {
  const errors = []

  if (!sponsor.value.tier) {
    errors.push('Tier is required')
  }

  if (sponsor.value.tier == 'Custom' && !sponsor.value.custom_tier) {
    errors.push('Custom Tier cannot be null')
  }

  if (!sponsor.value.sponsor_name) {
    errors.push('Sponsor name is required')
  }

  if (!sponsor.value.link) {
    errors.push('Sponsor link is required')
  }

  if (!sponsor.value.image) {
    errors.push('Please add logo of sponsor')
  }

  return errors
}
const addSponsor = () => {
  const errors = validateFields()

  if (errors.length) {
    errorMessages.value = errors.join('\n')
    return
  }

  event.setValue
    .submit({
      sponsor_list: [...event.doc.sponsor_list, sponsor.value],
    })
    .then(() => {
      errorMessages.value = ''
      show.value = false
      sponsor.value = {}
      toast.success('Sponsor Added Successfully!')
    })
    .catch((err) => {
      toast.error(err)
      errorMessages.value = err
    })
}

const handleSponsorUpdate = () => {
  const errors = validateFields()

  if (errors.length) {
    errorMessages.value = errors.join('\n')
    return
  }

  const fields = {
    tier: sponsor.value.tier,
    custom_tier: sponsor.value.custom_tier,
    sponsor_name: sponsor.value.sponsor_name,
    link: sponsor.value.link,
    image: sponsor.value.image,
  }

  createResource({
    url: 'frappe.client.set_value',
    makeParams() {
      return {
        doctype: 'FOSS Event Sponsor',
        name: sponsor.value.name,
        fieldname: fields,
      }
    },
    onSuccess() {
      toast.success('Sponsor Updated Successfully!')
      emit('reload:event')
      show.value = false
    },
    onError(err) {
      errorMessages.value = err
      toast.error(err)
    },
    auto: true,
  })
}
</script>
