<template>
  <div v-if="rsvp_form.data && rsvp.doc" class="px-4 py-8 md:p-8 flex flex-col gap-4">
    <div class="flex flex-col md:flex-row-reverse justify-between gap-2">
      <div class="flex items-center gap-2">
        <Button
          class="w-fit"
          size="md"
          :theme="rsvp.doc.is_published ? 'red' : 'green'"
          :icon-left="rsvp.doc.is_published ? 'slash' : 'upload'"
          :label="rsvp.doc.is_published ? 'Unpublish Form' : 'Publish Form'"
          @click="togglePublishForm"
        />
        <Button size="md" variant="solid" label="Update Form" @click="updateRsvpForm" />
      </div>
    </div>
    <div>
      <div class="grid sm:grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
        <div class="flex flex-col gap-3">
          <div class="text-lg font-semibold">
            <span>RSVP Form is </span>
            <span v-if="rsvp.doc.is_published" class="text-green-600">Live</span>
            <span v-else class="text-red-500">Unpublished</span>
          </div>

          <span v-if="rsvp.doc.is_published" class="text-sm text-gray-600"
            >Unpublishing the form will make it unaccessible to users.</span
          >
          <span v-else class="text-sm text-gray-600"
            >Publish this form to make it accessible to public.</span
          >
        </div>
        <div class="flex flex-col gap-2 text-base">
          <span>Route of the RSVP form</span>
          <CopyToClipboardComponent :route="whole_route" />
        </div>
      </div>
    </div>
    <div class="flex flex-col my-4 gap-6">
      <div class="font-semibold text-gray-800 border-b-2 pb-2">Edit Details</div>
      <div class="grid sm:grid-cols-1 md:grid-cols-2 gap-4">
        <div class="flex flex-col gap-2">
          <FormControl
            v-model="rsvp.doc.allow_edit"
            type="checkbox"
            label="Allow RSVP Edit"
            description=""
            size="md"
          />
          <span class="text-sm text-gray-600"
            >Allow users to edit their RSVP after submission.</span
          >
        </div>
        <FormControl
          v-model="rsvp.doc.max_rsvp_count"
          size="md"
          type="number"
          label="Max RSVP Count"
          description="Maximum RSVP Count for the event. Default is 100."
        />
        <TextEditor
          label="RSVP Form Description"
          class="col-span-2"
          placeholder="This description will be shown on the RSVP form."
          :model-value="rsvp.doc.rsvp_description"
          @update:model-value="($event) => (rsvp.doc.rsvp_description = $event)"
        />
      </div>
    </div>
    <div>
      <div class="font-semibold text-gray-800 border-b-2 pb-2">Standard Fields</div>
      <div class="py-4 grid sm:grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
        <FormControl
          v-for="(field, index) in standard_fields"
          :key="index"
          :size="'md'"
          :disabled="true"
          :type="field.type"
          :label="field.label"
          :description="field.description"
        />
      </div>
    </div>
    <div>
      <div class="font-semibold text-gray-800 border-b-2 pb-2">Custom Fields</div>
      <Button
        class="mt-3"
        size="md"
        icon-left="plus"
        label="Add Custom Field"
        @click="() => (show_dialog = true)"
      />
      <ListView
        class="my-4"
        :columns="[
          {
            label: 'Question',
            key: 'question',
          },
          {
            label: 'Type',
            key: 'type',
          },
        ]"
        :rows="rsvp.doc.custom_questions"
        :row-key="name"
        :options="{
          emptyState: {
            title: 'No Custom Questions Added.',
            description: 'You can add custom questions to this form.',
          },
          showTooltip: false,
          onRowClick: (row) => handleCustomRowEdit(row),
        }"
      />
    </div>
    <Dialog
      v-model="show_dialog"
      title="Add Custom Field"
      size="md"
      :options="{
        title: 'Add Custom Field',
      }"
    >
      <template #body-content>
        <div class="grid sm:grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
          <FormControl
            v-model="custom_field.question"
            class="col-span-2"
            size="md"
            type="text"
            label="Question"
            description="The question you want to ask the attendees."
          />
          <div>
            <FormControl
              v-model="custom_field.is_mandatory"
              size="md"
              type="checkbox"
              label="Is Mandatory"
              description="Whether the question is mandatory or not."
            />
            <div class="text-sm text-gray-600">Whether the question is mandatory or not.</div>
          </div>
          <FormControl
            v-model="custom_field.type"
            size="md"
            type="select"
            label="Type"
            :options="[
              { label: 'Data', value: 'Data' },
              { label: 'Select', value: 'Select' },
              { label: 'Long Text', value: 'Long Text' },
              { label: 'Text Editor', value: 'Text Editor' },
              { label: 'Check', value: 'Check' },
            ]"
            description="The type of question you want to ask."
          />
          <FormControl
            v-if="custom_field.type === 'Select'"
            v-model="custom_field.options"
            class="col-span-2"
            size="md"
            type="textarea"
            label="Options"
            description="Options for the select field. Enter each option on a new line."
          />
          <FormControl
            v-model="custom_field.description"
            class="col-span-2"
            size="md"
            type="textarea"
            label="Description"
            description="Description for the question."
          />
        </div>
      </template>
      <template #actions>
        <div
          class="grid grid-cols-1 gap-4"
          :class="inCustomEdit ? 'md:grid-cols-3' : 'md:grid-cols-2'"
        >
          <div v-if="inCustomEdit" class="col-span-2 grid grid-cols-2 gap-4">
            <Button label="Save" variant="solid" @click="updateCustomField" />
            <Button label="Delete" theme="red" @click="deleteCustomQuestion" />
          </div>
          <Button v-else label="Add Field" variant="solid" @click="addCustomField" />
          <Button label="Cancel" @click="() => (show_dialog = false)" />
        </div>
      </template>
    </Dialog>
  </div>
</template>
<script setup>
import { createDocumentResource, createResource, FormControl, ListView, Dialog } from 'frappe-ui'
import { reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { toast } from 'vue-sonner'
import CopyToClipboardComponent from '../components/CopyToClipboardComponent.vue'
import TextEditor from '@/components/ui/TextEditor.vue'

const route = useRoute()

const rsvp_form = createResource({
  url: 'frappe.client.get',
  params: {
    doctype: 'FOSS Event RSVP',
    filters: {
      event: route.params.id,
    },
  },
  auto: true,
})

const standard_fields = [
  {
    label: 'Name',
    description: 'Full Name of the attendee',
    type: 'text',
  },
  {
    label: "I'm a",
    description: 'Current Profession of the attendee',
    type: 'select',
  },
]

let rsvp = reactive({})
let whole_route = ref('')

let custom_field = reactive({
  question: '',
  type: '',
  is_mandatory: 0,
  options: '',
  description: '',
})

watch(rsvp_form, (newForm) => {
  rsvp = createDocumentResource({
    doctype: 'FOSS Event RSVP',
    name: newForm.data.name,
    fields: ['*'],
    auto: true,
    onSuccess: (doc) => {
      whole_route.value = `${window.location.origin}/${doc.route}`
      custom_field.idx = doc.custom_questions.length + 1
    },
  })
})

const togglePublishForm = () => {
  rsvp.setValue.submit({
    is_published: !rsvp.doc.is_published,
  })
  if (rsvp.doc.is_published) {
    toast.success('RSVP Form Published Successfully')
  } else {
    toast.warning('RSVP Form Unpublished')
  }
}

let show_dialog = ref(false)

const addCustomField = () => {
  rsvp.doc.custom_questions.push(custom_field)
  custom_field = {
    idx: custom_field.idx + 1,
    question: '',
    type: '',
    is_mandatory: 0,
    options: '',
    description: '',
  }
  show_dialog.value = false
}

let inCustomEdit = ref(false)

const handleCustomRowEdit = (row) => {
  inCustomEdit.value = true
  custom_field = row
  show_dialog.value = true
}

const updateCustomField = () => {
  const index = rsvp.doc.custom_questions.findIndex((field) => field.idx === custom_field.idx)
  rsvp.doc.custom_questions[index] = custom_field
  show_dialog.value = false
  inCustomEdit.value = false
  custom_field = {
    idx: custom_field.idx + 1,
    question: '',
    type: '',
    is_mandatory: 0,
    options: '',
    description: '',
  }
}

const updateRsvpForm = () => {
  rsvp.save
    .submit()
    .then(() => {
      toast.success('RSVP Form Updated Successfully')
    })
    .catch((error) => {
      toast.error('Failed to update RSVP Form', {
        description: error.message,
      })
    })
}

const deleteCustomQuestion = () => {
  rsvp.doc.custom_questions = rsvp.doc.custom_questions.filter(
    (field) => field.idx !== custom_field.idx,
  )
  show_dialog.value = false
  inCustomEdit.value = false
  custom_field = {
    idx: custom_field.idx + 1,
    question: '',
    type: '',
    is_mandatory: 0,
    options: '',
    description: '',
  }
}
</script>
