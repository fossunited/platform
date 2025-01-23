<template>
  <div class="flex flex-col gap-2">
    <label v-if="label" class="text-xs text-gray-600">{{ label }}</label>
    <div class="relative">
      <!-- Image Preview -->
      <div v-if="modelValue" class="mb-2">
        <div class="relative w-full h-40 group">
          <img
            :src="modelValue"
            class="w-full h-40 object-contain rounded border bg-gray-50"
            :alt="label || 'Image preview'"
          />
          <div
            class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2"
          >
            <button
              class="p-2 rounded-full bg-white/20 hover:bg-white/30 transition-colors"
              @click="removeImage"
            >
              <IconTrash class="w-5 h-5 text-white" />
            </button>
            <button
              class="p-2 rounded-full bg-white/20 hover:bg-white/30 transition-colors"
              @click="$refs.fileUploader.openFileSelector()"
            >
              <IconEdit class="w-5 h-5 text-white" />
            </button>
          </div>
        </div>
      </div>

      <FileUploader
        ref="fileUploader"
        :file-types="fileTypes"
        :validate-file="validateFile"
        @success="handleSuccess"
        @failure="handleError"
      >
        <template #default="{ uploading, progress, openFileSelector, error }">
          <div
            :class="[
              'transition-all duration-200',
              'border-2 border-dashed rounded-lg',
              modelValue ? 'p-3' : 'p-8 hover:cursor-pointer',
            ]"
            @click="openFileSelector"
          >
            <!-- Upload Progress -->
            <div v-if="uploading" class="flex flex-col items-center gap-2">
              <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  class="h-full bg-blue-500 transition-all duration-200"
                  :style="{ width: `${progress}%` }"
                />
              </div>
              <span class="text-sm text-gray-600">Uploading... {{ progress }}%</span>
            </div>

            <!-- Upload Prompt -->
            <div v-if="!modelValue" class="flex flex-col items-center gap-3">
              <IconPhotoScan
                :class="[
                  'w-8 h-8 transition-colors duration-200',
                  isDragging ? 'text-blue-500' : 'text-gray-400',
                ]"
              />
              <div class="text-center">
                <p class="text-sm font-medium text-gray-700">Click to browse files</p>
              </div>
            </div>
          </div>

          <!-- Error Message -->
          <p v-if="error" class="mt-2 text-sm text-red-600">
            {{ error }}
          </p>
        </template>
      </FileUploader>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { FileUploader } from 'frappe-ui'
import { IconPhotoScan, IconTrash, IconEdit } from '@tabler/icons-vue'

const fileUploader = ref(null)
const isDragging = ref(false)

const model = defineModel({ type: String, default: '' })

const props = defineProps({
  // modelValue: {
  //   type: String,
  //   default: '',
  // },
  label: {
    type: String,
    default: '',
  },
  fileTypes: {
    type: Array,
    default: () => ['image/*', 'image/svg+xml'],
  },
  maxFileSize: {
    type: Number,
    default: 5,
  },
})

const emit = defineEmits(['update:modelValue', 'error'])

const validateFile = (file) => {
  if (file.size > props.maxFileSize * 1024 * 1024) {
    return `File size should not exceed ${props.maxFileSize}MB`
  }
  return null
}

const handleSuccess = (response) => {
  // emit('update:modelValue', response.file_url)
  model.value = response.file_url
}

const handleError = (error) => {
  emit('error', error)
}

const removeImage = () => {
  // emit('update:modelValue', '')
  model.value = ''
}
</script>
