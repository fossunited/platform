<template>
  <div class="flex gap-1 items-center">
    <div
      v-for="(item, index) in items"
      :key="index"
      class="text-base flex gap-1 items-center my-2"
      :class="index == items.length - 1 ? 'font-medium text-gray-800' : 'text-gray-600 '"
    >
      <router-link
        v-if="item.route"
        class="hover:text-gray-700 transition-colors"
        :to="item.route"
      >
        {{ item.label }}
      </router-link>
      <a v-else-if="item.link" :href="item.link" class="hover:text-gray-700 transition-colors">
        {{ item.label }}
      </a>
      <span v-else>
        {{ item.label }}
      </span>
      <span v-if="index !== items.length - 1">
        <IconChevronRight class="w-5" />
      </span>
    </div>
  </div>
</template>
<script setup>
import { IconChevronRight } from '@tabler/icons-vue'
import { defineProps } from 'vue'

const props = defineProps({
  items: {
    type: Array,
    required: true,
  },
})
</script>
