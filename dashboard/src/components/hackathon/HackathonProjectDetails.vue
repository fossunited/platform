<!-- eslint-disable vue/no-mutating-props -->
<template>
  <div class="flex flex-col md:grid md:grid-cols-2 mb-4 gap-4 md:items-center">
    <div class="flex flex-col py-1">
      <div class="text-xs text-gray-600">Project's Public Page</div>
      <CopyToClipboard :route="getRoute(project.data.route)" />
    </div>
    <FormControl
      v-model="project.data.short_description"
      label="Short Description"
      placeholder="Enter a short description of the project"
    />
    <FormControl
      v-model="project.data.repo_link"
      label="Repository Link"
      :disabled="project.data.is_partner_project"
    >
      <template #prefix>
        <IconBrandGithub class="w-4" />
      </template>
    </FormControl>
    <FormControl v-model="project.data.demo_link" label="Demo Link" />
    <TextEditor
      class="col-span-2 mt-2"
      label="Project Description"
      :model-value="project.data.description"
      placeholder="Enter a detailed description of the project"
      @update:model-value="($event) => (project.data.description = $event)"
    />
  </div>
  <div>
    <ErrorMessage :message="errorMessage" />
    <div class="flex flex-row-reverse">
      <Button
        variant="solid"
        theme="green"
        label="Save"
        size="md"
        class="w-full md:w-2/5"
        @click="handleProjectUpdate"
      />
    </div>
  </div>
</template>
<script setup>
import CopyToClipboard from '@/components/CopyToClipboardComponent.vue'
import TextEditor from '@/components/TextEditor.vue'
import { defineProps, defineEmits, ref } from 'vue'
import { FormControl, ErrorMessage, createResource } from 'frappe-ui'
import { toast } from 'vue-sonner'
import { IconBrandGithub } from '@tabler/icons-vue'

const props = defineProps({
  project: {
    type: Object,
    required: true,
  },
})

const getRoute = (route) => {
  return `${window.location.origin}/${route}`
}

const errorMessage = ref('')

const updateProjectErrors = () => {
  const errors = []

  if (!props.project.data.short_description) {
    errors.push('Short description cannot be empty')
  }
  if (!props.project.data.description) {
    errors.push('Description cannot be empty')
  }
  if (!props.project.data.repo_link) {
    errors.push('Repository link cannot be empty')
  }
  if (props.project.data.repo_link && !props.project.data.repo_link.startsWith('https://')) {
    errors.push('Enter a valid repo link')
  }

  return errors
}

const handleProjectUpdate = () => {
  if (updateProjectErrors().length) {
    errorMessage.value = updateProjectErrors().join(', ')
    return
  } else {
    errorMessage.value = ''
  }

  createResource({
    url: 'frappe.client.set_value',
    makeParams() {
      return {
        doctype: 'FOSS Hackathon Project',
        name: props.project.data.name,
        fieldname: {
          short_description: props.project.data.short_description,
          description: props.project.data.description,
          repo_link: props.project.data.repo_link,
          demo_link: props.project.data.demo_link,
        },
      }
    },
    auto: true,
    onSuccess(data) {
      toast.success('Project updated successfully')
    },
    onError(error) {
      toast.error('Failed to update project' + error.message)
    },
  })
}
</script>
