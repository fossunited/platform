<template>
  <Dialog
    v-model="show"
    class="z-[80]"
    :options="{
      icon: {
        name: 'link',
        appearance: 'gray',
      },
      title: 'Insert Link',
      size: 'md',
    }"
  >
    <template #body-content>
      <div class="flex flex-col gap-2">
        <FormControl v-model="linkData.newText" label="Text" autofocus />
        <FormControl v-model="linkData.newValue" label="URL" />
      </div>
    </template>
    <template #actions>
      <Button class="w-full" label="Insert" variant="solid" @click="emit('insert-link')" />
    </template>
  </Dialog>
</template>
<script setup>
import { Dialog, FormControl } from 'frappe-ui'

const show = defineModel('show', { type: Boolean })
const linkData = defineModel('linkData', { type: Object })
const emit = defineEmits(['insert-link'])
</script>
