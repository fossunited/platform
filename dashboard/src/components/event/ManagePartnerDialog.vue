<template>
  <Dialog
    v-model="show"
    :options="{
      title: isNew ? 'Add Community Partner' : 'Manage Community Partner',
    }"
  >
    <template #body-content>
      <div class="flex flex-col gap-3">
        <FormControl v-model="partner.org_name" label="Community Name" required />
        <FormControl v-model="partner.link" label="Website Link" type="url" required>
          <template #prefix>
            <IconLink class="w-4" />
          </template>
        </FormControl>
        <FileUploaderArea v-model="partner.logo" label="Community Logo" />
        <ErrorMessage :message="errorMessages" class="text-sm -mb-4" />
      </div>
    </template>
    <template #actions>
      <div class="grid grid-flow-col w-full">
        <Button v-if="isNew" label="Add" variant="solid" @click="addPartner" />
        <Button v-else label="Update" variant="solid" @click="handlePartnerUpdate" />
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

const event = inject('event')
const errorMessages = ref('')

const show = defineModel('show', { required: true, type: Boolean, default: false })
const partner = defineModel('partner', { required: true, type: Object })
const props = defineProps({
  isNew: {
    default: false,
    type: Boolean,
  },
})
const emit = defineEmits(['reload:event'])

const validateFields = () => {
  const errors = []

  if (!partner.value.org_name) {
    errors.push('Organization name is required')
  }

  if (!partner.value.link) {
    errors.push('Partner link is required')
  }

  if (!partner.value.logo) {
    errors.push('Please add logo of partner')
  }

  return errors
}
const addPartner = () => {
  const errors = validateFields()

  if (errors.length) {
    errorMessages.value = errors.join('\n')
    return
  }

  event.setValue
    .submit({
      community_partners: [...event.doc.community_partners, partner.value],
    })
    .then(() => {
      show.value = false
      partner.value = {}
      toast.success('Community Partner Added Successfully!')
    })
    .catch((err) => {
      toast.error(err)
      errorMessages.value = err
    })
}

const handlePartnerUpdate = () => {
  const errors = validateFields()

  if (errors.length) {
    errorMessages.value = errors.join('\n')
    return
  }

  const fields = {
    org_name: partner.value.org_name,
    link: partner.value.link,
    logo: partner.value.image,
  }

  createResource({
    url: 'frappe.client.set_value',
    makeParams() {
      return {
        doctype: 'FOSS Event Community Partner',
        name: partner.value.name,
        fieldname: fields,
      }
    },
    onSuccess() {
      toast.success('Community Partner Updated Successfully!')
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
