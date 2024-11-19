<template>
  <div class="flex flex-col md:flex-row">
    <SideNavbar v-if="navItems.data" :menu-items="navItems.data" />
    <div class="w-full md:ml-[220px]">
      <RouterView />
    </div>
  </div>
</template>

<script setup>
import { inject, ref } from 'vue'
import { usePageMeta, createResource } from 'frappe-ui'
import SideNavbar from '@/components/NewAppSidebar.vue'

const session = inject('$session')

const navItems = createResource({
  url: 'fossunited.api.sidebar.get_sidebar_items',
  makeParams() {
    return {
      user: session.user,
    }
  },
  auto: true,
})

usePageMeta(() => {
  return {
    title: 'Dashboard',
  }
})
</script>
