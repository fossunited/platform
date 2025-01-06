<template>
  <div v-if="event.doc" class="px-4 py-8 md:p-8 flex flex-col gap-4">
    <div class="flex flex-col md:flex-row justify-between gap-2">
      <div class="text-xl font-medium">Create RSVP Form</div>
      <Button size="md" label="Create" variant="solid" @click="createRsvpForm" />
    </div>
    <div>
      <div class="grid sm:grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
        <div class="flex flex-col gap-2">
          <FormControl
            v-model="rsvp_doc.allow_edit"
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
          v-model="rsvp_doc.max_rsvp_count"
          size="md"
          type="number"
          label="Max RSVP Count"
          description="Maximum RSVP Count for the event. Default is 100."
        />
        <TextEditor
          class="col-span-2"
          label="RSVP Form Description"
          placeholder="Write a description to be shown in the RSVP Form"
          :model-value="rsvp_doc.rsvp_description"
          @update:model-value="($event) => (rsvp_doc.rsvp_description = $event)"
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
        class="mt-4"
        :columns="[
          { label: 'Question', key: 'question' },
          { label: 'Type', key: 'type' },
        ]"
        :rows="rsvp_doc.custom_questions"
        row-key="idx"
        :options="{
          emptyState: {
            title: 'No Custom Fields',
            description: 'No custom fields have been added yet.',
          },
          onRowClick: (row) => handleCustomRowEdit(row),
        }"
      ></ListView>
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
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Button v-if="inCustomEdit" label="Save" variant="solid" @click="updateCustomField" />
          <Button v-else label="Add Field" variant="solid" @click="addCustomField" />
          <Button label="Cancel" theme="red" @click="() => (show_dialog = false)" />
        </div>
      </template>
    </Dialog>
  </div>
</template>
<script setup>
import { createDocumentResource, FormControl, ListView, Dialog, createResource } from 'frappe-ui'
import { reactive, ref, defineEmits } from 'vue'
import { useRoute } from 'vue-router'
import { toast } from 'vue-sonner'
import TextEditor from '@/components/ui/TextEditor.vue'

const route = useRoute()
const emit = defineEmits(['rsvpCreated'])

const event = createDocumentResource({
  doctype: 'FOSS Chapter Event',
  name: route.params.id,
  fields: ['*'],
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

let rsvp_doc = reactive({
  doctype: 'FOSS Event RSVP',
  event: route.params.id,
  allow_edit: 0,
  max_rsvp_count: 100,
  rsvp_description: '',
  custom_questions: [],
})

let custom_field = reactive({
  idx: 1,
  question: '',
  type: '',
  is_mandatory: 0,
  options: '',
  description: '',
})
let show_dialog = ref(false)

const addCustomField = () => {
  rsvp_doc.custom_questions.push(custom_field)
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
  const index = rsvp_doc.custom_questions.findIndex((field) => field.idx === custom_field.idx)
  rsvp_doc.custom_questions[index] = custom_field
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

const createRsvpForm = () => {
  let rsvp = createResource({
    url: 'frappe.client.insert',
    params: {
      doc: rsvp_doc,
    },
  })
  rsvp
    .submit()
    .then((result) => {
      toast.success('RSVP Form created successfully')
      emit('rsvpCreated')
    })
    .catch((err) => {
      toast.error('Failed to create RSVP Form', {
        description: err.message,
      })
    })
}
</script>
