<template>
  <div class="relative block min-h-0 flex-shrink-0 overflow-hidden hover:overflow-auto">
    <div
      class="fixed flex flex-col justify-between px-4 py-6 min-h-screen w-[220px] border-r bg-gray-50"
    >
      <div class="flex flex-col gap-4">
        <slot name="header"> </slot>
        <slot name="branding">
          <div>
            <div class="font-fff text-gray-900 uppercase">FOSS United</div>
            <div class="text-sm mt-2 tracking-wider text-gray-700 uppercase">Dashboard</div>
          </div>
        </slot>
        <slot name="pre-nav-items">
          <div v-if="title" class="text-lg font-semibold uppercase mt-2">{{ title }}</div>
        </slot>
        <slot name="nav-items">
          <div v-if="menuItems.length > 0" class="flex flex-col gap-2 my-2">
            <div v-for="(group, groupIndex) in menuItems" :key="groupIndex" class="my-1">
              <div
                v-if="group.parent_label"
                class="text-xs text-gray-600 font-medium uppercase tracking-wide"
              >
                {{ group.parent_label }}
              </div>
              <div class="flex flex-col my-1 gap-2 text-gray-700">
                <router-link
                  v-for="(item, index) in group.items"
                  :key="item.label"
                  :to="item.route"
                  class="w-full text-sm flex items-center gap-1 rounded-sm p-2 hover:bg-gray-100 transition-colors"
                  :class="
                    isMenuItemActive(item.route, index)
                      ? 'font-medium text-gray-900 bg-gray-100'
                      : ''
                  "
                >
                  <FeatherIcon v-if="item.icon" class="w-4 h-4" :name="item.icon" />
                  <span>{{ item.label }}</span>
                </router-link>
              </div>
            </div>
          </div>
        </slot>
        <slot name="post-nav-items"></slot>
      </div>
      <div>
        <slot name="pre-user-actions"></slot>
        <slot name="user-actions"></slot>
        <slot name="footer">
          <p class="text-gray-700 text-xs leading-snug">
            FOSS United Foundation.
            <br />CC-BY-SA.
          </p>
        </slot>
      </div>
    </div>
  </div>
</template>
<script setup>
import { createResource, FeatherIcon } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { defineProps } from 'vue'

const route = useRoute()

const props = defineProps({
  title: {
    type: String,
    default: '',
  },
  menuItems: {
    type: Array,
    required: true,
    default: () => [],
  },
})

const isMenuItemActive = (menuRoute, index) => {
  if (index == 0 && menuRoute != route.path) {
    return false
  }
  return (
    menuRoute === route.path ||
    menuRoute === '/' + route.path.split('/').filter(Boolean).slice(0, -1).join('/')
  )
}
</script>
