<template>
  <TransitionRoot as="template" :show="open">
    <Dialog class="relative z-50" @close="open = false">
      <TransitionChild
        as="template"
        enter="ease-in-out duration-500"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in-out duration-500"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-gray-700/50 transition-opacity" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-hidden">
        <div class="absolute inset-0 overflow-hidden">
          <div class="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">
            <TransitionChild
              as="template"
              enter="transform transition ease-in-out duration-500 sm:duration-700"
              enter-from="translate-x-full"
              enter-to="translate-x-0"
              leave="transform transition ease-in-out duration-500 sm:duration-700"
              leave-from="translate-x-0"
              leave-to="translate-x-full"
            >
              <DialogPanel class="pointer-events-auto relative w-screen" :class="[sizes[size]]">
                <TransitionChild
                  as="template"
                  enter="ease-in-out duration-500"
                  enter-from="opacity-0"
                  enter-to="opacity-100"
                  leave="ease-in-out duration-500"
                  leave-from="opacity-100"
                  leave-to="opacity-0"
                >
                  <div class="absolute left-0 top-0 -ml-8 flex pr-2 pt-4 sm:-ml-10 sm:pr-4">
                    <button
                      type="button"
                      class="relative rounded-md text-gray-300 hover:text-white focus:outline-none focus:ring-2 focus:ring-white"
                      @click="open = false"
                    >
                      <span class="absolute -inset-2.5" />
                      <span class="sr-only">Close panel</span>
                      <Button icon="x" />
                    </button>
                  </div>
                </TransitionChild>
                <div class="flex h-full flex-col overflow-y-scroll bg-white py-6 shadow-xl">
                  <div class="px-4 sm:px-6 flex gap-2">
                    <slot name="pre-title"></slot>
                    <DialogTitle class="text-2xl font-semibold text-gray-900">
                      <slot name="dialog-title">{{ title }}</slot>
                    </DialogTitle>
                    <slot name="post-title"></slot>
                  </div>
                  <div class="relative mt-6 flex-1 px-4 sm:px-6">
                    <slot></slot>
                  </div>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>
<script setup>
import { reactive, ref } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'

const open = defineModel({ type: Boolean })

const sizes = reactive({
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
})

const props = defineProps({
  size: {
    type: String,
    default: 'xl',
  },
  title: {
    type: String,
    default: '',
  },
})
</script>
