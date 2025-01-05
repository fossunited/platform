<template>
  <!-- Add PR/Issue Dialog -->
  <Dialog
    v-model="showAddDialog"
    class="z-50"
    :options="{
      title: 'Add Issue / PR / Discussion',
    }"
  >
    <template #body-content>
      <div class="flex flex-col gap-4">
        <FormControl
          v-model="newIssuePr.link"
          type="url"
          label="Link &ast;"
          @input="getPrIssueTitle.fetch()"
        />
        <div v-if="getPrIssueTitle.loading" class="flex gap-1">
          <LoadingIndicator class="w-4 h-4" />
          <small>Fetching details...</small>
        </div>
        <div v-if="fetchTitleError">
          <small class="text-gray-700">{{ fetchTitleError }}</small>
        </div>
        <FormControl v-model="newIssuePr.title" label="Title &ast;" />
        <FormControl
          v-model="newIssuePr.type"
          type="select"
          :options="[
            {
              label: 'Issue',
              value: 'Issue',
            },
            {
              label: 'Pull Request',
              value: 'Pull Request',
            },
            {
              label: 'Discussion',
              value: 'Discussion',
            },
          ]"
          label="Type &ast;"
        />
        <ErrorMessage :message="addIssueErrors" />
      </div>
    </template>
    <template #actions>
      <div class="grid w-full grid-cols-2 gap-4">
        <Button
          label="Add"
          variant="solid"
          :loading="addIssuePr.loading"
          @click="handleAddIssuePr"
        />
        <Button
          label="Cancel"
          theme="gray"
          @click="
            () => {
              newIssuePr.title = ''
              newIssuePr.link = ''
              newIssuePr.type = ''
              showAddDialog = false
            }
          "
        />
      </div>
    </template>
  </Dialog>

  <!-- Issue / PR ListView -->
  <div v-if="project.data.issue_pr_table.length > 0" class="flex flex-row-reverse w-full p-2 mb-2">
    <Button
      class="w-full md:w-fit"
      label="Link Issue / PR / Discussion"
      icon-left="plus"
      variant="solid"
      @click="showAddDialog = true"
    />
  </div>
  <ListView
    class="h-[440px]"
    :columns="[
      {
        label: 'Title',
        key: 'title',
      },
      {
        label: 'Link',
        key: 'link',
      },
      {
        label: '',
        key: 'actions',
        width: 1 / 4,
      },
    ]"
    :rows="project.data.issue_pr_table"
    :options="{
      selectable: false,
      showTooltip: false,
      resizeColumn: false,
      onRowClick: (row) => {},
      emptyState: {
        title: 'No issues or PRs linked to the project',
        description: 'You can link issues and PRs to the project to keep track of them.',
        button: {
          label: 'Link Issue / PR / Discussion',
          variant: 'solid',
          'icon-left': 'plus',
          onClick: () => {
            showAddDialog = true
          },
        },
      },
    }"
    row-key="name"
  >
    <template #cell="{ item, row, column }">
      <div v-if="column.label == 'Link'">
        <a :href="item" target="_blank" class="text-gray-900 text-base underline flex gap-1">
          <span>
            {{ item }}
          </span>
          <IconArrowUpRight class="w-4 h-4" />
        </a>
      </div>
      <div v-else-if="column.key == 'actions'">
        <Button icon="trash" size="sm" theme="red" variant="subtle" @click="deleteIssuePr(row)" />
      </div>
      <div v-else class="text-base">
        {{ item }}
      </div>
    </template>
  </ListView>
</template>
<script setup>
import { ref, defineProps, defineEmits, reactive } from 'vue'
import {
  ErrorMessage,
  FormControl,
  ListView,
  Dialog,
  createResource,
  LoadingIndicator,
} from 'frappe-ui'
import { toast } from 'vue-sonner'
import { IconArrowUpRight } from '@tabler/icons-vue'

const props = defineProps({
  project: {
    type: Object,
    required: true,
  },
})

const emits = defineEmits(['fetch-project'])

const newIssuePr = reactive({
  title: '',
  link: '',
  type: '',
})

const showAddDialog = ref(false)
const addIssueErrors = ref('')

const addIssuePrErrors = () => {
  const errors = []

  if (!newIssuePr.link) {
    errors.push('Link cannot be empty')
  }
  if (newIssuePr.link && !newIssuePr.link.startsWith('https://')) {
    errors.push('Enter a valid link')
  }
  if (!newIssuePr.title) {
    errors.push('Title cannot be empty')
  }
  if (!newIssuePr.type) {
    errors.push('Type cannot be empty')
  }

  return errors
}

const fetchTitleError = ref('')

const getPrIssueTitle = createResource({
  url: 'fossunited.api.hackathon.get_issue_pr_title',
  makeParams() {
    return {
      url: newIssuePr.link,
    }
  },
  onSuccess(data) {
    fetchTitleError.value = ''
    addIssueErrors.value = ''
    newIssuePr.title = data.title
    newIssuePr.type = data.type
  },
  onError(err) {
    newIssuePr.title = ''
    newIssuePr.type = ''
    if (err.messages[0] == 'Not a Github URL.') {
      fetchTitleError.value = 'Failed to fetch title :( \nPlease enter data manually.'
      return
    }
    addIssueErrors.value = 'Failed to fetch title : \n' + err.message
  },
})

const addIssuePr = createResource({
  url: 'fossunited.api.hackathon.add_pr_issue_to_project',
  makeParams() {
    return {
      project: props.project.data.name,
      details: newIssuePr,
    }
  },
  onSuccess() {
    showAddDialog.value = false
    emits('fetch-project')
    newIssuePr.title = ''
    newIssuePr.link = ''
    newIssuePr.type = ''
  },
  onError(err) {
    addIssueErrors.value = 'Failed to add issue / PR : \n' + err.message
  },
})

const handleAddIssuePr = () => {
  let errors = addIssuePrErrors()
  if (errors.length) {
    addIssueErrors.value = errors.join(', ')
    return
  }
  addIssueErrors.value = ''
  addIssuePr.fetch()
}

const deleteIssuePr = (row) => {
  createResource({
    url: 'fossunited.api.hackathon.remove_pr_issue_from_project',
    makeParams() {
      return {
        project: props.project.data.name,
        issue_pr: row.name,
      }
    },
    onSuccess() {
      toast.info('Issue / PR deleted successfully')
      emits('fetch-project')
    },
    onError(err) {
      toast.error('Failed to delete issue / PR : \n' + err.message)
    },
  }).fetch()
}
</script>
