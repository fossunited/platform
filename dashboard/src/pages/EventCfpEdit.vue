<template>
  <div v-if="cfp_form.data && cfp.doc" class="px-4 py-8 md:p-8 flex flex-col gap-4">
    <div class="flex flex-row justify-end gap-2">
      <Button
        class="w-fit"
        size="md"
        :theme="cfp.doc.is_published ? 'red' : 'green'"
        :icon-left="cfp.doc.is_published ? 'slash' : 'upload'"
        :label="cfp.doc.is_published ? 'Unpublish Form' : 'Publish Form'"
        @click="togglePublishForm"
      />

      <Button size="md" variant="solid" label="Save Changes" @click="updateCfpForm" />
    </div>
    <div>
      <div class="grid sm:grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
        <div class="flex flex-col gap-2 text-base">
          <span>Route of the CFP form</span>
          <CopyToClipboardComponent :route="whole_route" />
        </div>
      </div>
    </div>
    <div class="flex flex-col my-4 gap-6">
      <div class="font-semibold text-gray-800 border-b-2 pb-2">Edit Details</div>
      <div class="grid sm:grid-cols-1 md:grid-cols-2 gap-4">
        <div class="flex flex-col gap-2">
          <FormControl
            v-model="cfp.doc.allow_cfp_edit"
            type="checkbox"
            label="Allow Proposal Edit"
            size="md"
          />
          <span class="text-sm text-gray-600"
            >Allow users to edit their CFP after submission.</span
          >
        </div>
        <div class="flex flex-col gap-2">
          <FormControl
            v-model="cfp.doc.anonymise_proposals"
            size="md"
            type="checkbox"
            label="Anonymise Proposals?"
          />
          <span class="text-sm text-gray-600"
            >The proposals will not show the details of the submitter to the public & reviewers
            until it is approved.</span
          >
        </div>
        <div class="flex flex-col gap-2">
          <FormControl
            v-model="cfp.doc.only_workshops"
            type="checkbox"
            label="Only Workshops"
            size="md"
            @change="validateOnlyOneType"
          />
          <span class="text-sm text-gray-600">Only accept workshop proposals.</span>
        </div>
        <div class="flex flex-col gap-2">
          <FormControl
            v-model="cfp.doc.only_talk_proposals"
            type="checkbox"
            label="Only Talk Proposals"
            size="md"
            @change="validateOnlyOneType"
          />
          <span class="text-sm text-gray-600">Only accept talk proposals.</span>
        </div>
        <TextEditor
          class="col-span-2"
          label="Form Description"
          placeholder="This description will be shown on the CFP form."
          :model-value="cfp.doc.cfp_form_description"
          @update:model-value="($event) => (cfp.doc.cfp_form_description = $event)"
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
        :rows="cfp.doc.cfp_custom_questions"
        :row-key="name"
        :options="{
          emptyState: {
            title: 'No Custom Questions Added.',
            description: 'You can add custom questions to this form.',
          },
          showTooltip: false,
          selectable: false,
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
import { reactive, ref, watch, defineEmits } from 'vue'
import { useRoute } from 'vue-router'
import { toast } from 'vue-sonner'
import CopyToClipboardComponent from '@/components/CopyToClipboardComponent.vue'
import TextEditor from '@/components/ui/TextEditor.vue'

const route = useRoute()

const cfp_form = createResource({
  url: 'frappe.client.get',
  params: {
    doctype: 'FOSS Event CFP',
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
    label: 'Email',
    description: 'Email of the attendee',
    type: 'select',
  },
  {
    label: 'Picture (URL)',
    description: 'URL for a publicly hosted photo',
    type: 'url',
  },
  {
    label: 'Designation',
    description: 'Designation of the attendee',
    type: 'text',
  },
  {
    label: 'Organization',
    description: 'Organization of the attendee',
    type: 'text',
  },
  {
    label: 'Speaker Bio',
    description: 'Short bio of the speaker',
    type: 'textarea',
  },
  {
    label: 'Is this your first talk?',
    type: 'select',
  },
  {
    label: 'Session Type',
    description: 'Type of session attendee is proposing',
    type: 'select',
  },
  {
    label: 'Session Title',
    description: 'Title of the session',
    type: 'text',
  },
  {
    label: 'Session Reference',
    description: 'Link relevant references for the talk.',
    type: 'url',
  },
  {
    label: 'Session Description',
    description: 'Description of the session',
    type: 'textarea',
  },
]

const validateOnlyOneType = () => {
  if (cfp.doc.only_workshops && cfp.doc.only_talk_proposals) {
    toast.error('Invalid Selection.', {
      description: 'If you wish to accept all type of proposals, uncheck both options.',
    })
    cfp.doc.only_workshops = 0
    cfp.doc.only_talk_proposals = 0
  }
}

let cfp = reactive({})
let whole_route = ref('')

let custom_field = reactive({
  question: '',
  type: '',
  is_mandatory: 0,
  options: '',
  description: '',
})

watch(cfp_form, (newForm) => {
  cfp = createDocumentResource({
    doctype: 'FOSS Event CFP',
    name: newForm.data.name,
    fields: ['*'],
    auto: true,
    onSuccess: (doc) => {
      whole_route.value = `${window.location.origin}/${doc.route}`
      custom_field.idx = doc.cfp_custom_questions.length + 1
    },
  })
})

const emit = defineEmits(['reloadDoc'])
const togglePublishForm = () => {
  cfp.setValue.submit({
    is_published: !cfp.doc.is_published,
  })
  if (cfp.doc.is_published) {
    toast.success('CFP Form Published Successfully')
    emit('reloadDoc')
  } else {
    toast.warning('CFP Form Unpublished')
  }
}

let show_dialog = ref(false)

const addCustomField = () => {
  cfp.doc.cfp_custom_questions.push(custom_field)
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
  const index = cfp.doc.cfp_custom_questions.findIndex((field) => field.idx === custom_field.idx)
  cfp.doc.cfp_custom_questions[index] = custom_field
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

const updateCfpForm = () => {
  cfp.save
    .submit()
    .then(() => {
      toast.success('CFP Form Updated Successfully')
    })
    .catch((error) => {
      toast.error('Failed to update CFP Form', {
        description: error.message,
      })
    })
}

const deleteCustomQuestion = () => {
  cfp.doc.cfp_custom_questions = cfp.doc.cfp_custom_questions.filter(
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
