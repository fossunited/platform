<template>
  <TabGroup @change="changeModelValue">
    <TabList class="flex gap-6">
      <Tab
        v-for="item in tabItems"
        :key="item.value"
        v-slot="{ selected }"
        class="focus-visible:outline-none"
      >
        <div
          class="border border-gray-900 flex items-center justify-center p-2 text-base font-medium hover:bg-gray-100 transition-colors"
          :class="{ 'bg-gray-900 text-white hover:bg-gray-800': selected }"
        >
          <component :is="item.icon" :class="{ 'fill-white': selected }" />
        </div>
      </Tab>
    </TabList>
  </TabGroup>
</template>
<script setup>
import { defineModel } from 'vue'
import { TabGroup, TabList, Tab } from '@headlessui/vue'
import { IconCarouselHorizontalFilled, IconCarouselVerticalFilled } from '@tabler/icons-vue'

const model = defineModel({
  prop: 'selectedScheduleView',
  event: 'change',
  type: String,
})

const changeModelValue = (index) => {
  model.value = tabItems[index].value
}

const tabItems = [
  {
    label: 'Vertical',
    icon: IconCarouselVerticalFilled,
    value: 'vertical',
  },
  {
    label: 'Horizontal',
    icon: IconCarouselHorizontalFilled,
    value: 'horizontal',
  },
]
</script>
