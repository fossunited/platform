<template>
  <div class="flex flex-col md:flex-row">
    <SideNavbar title="Manage Event" :menu-items="sidebarMenuItems" />
    <div class="w-full md:ml-[220px]">
      <RouterView />
    </div>
  </div>
</template>

<script setup>
import { ref, provide } from 'vue'
import { createResource, usePageMeta } from 'frappe-ui'
import { RouterView, useRoute } from 'vue-router'
import SideNavbar from '@/components/NewAppSidebar.vue'

const route = useRoute()

const sidebarMenuItems = ref([
  {
    items: [
      {
        icon: 'arrow-left',
        label: 'Go Home',
        route: '/chapter',
      },
    ],
  },
])

const event = createResource({
  url: 'frappe.client.get_value',
  params: {
    doctype: 'FOSS Chapter Event',
    fieldname: ['name', 'event_name', 'is_paid_event', 'chapter'],
    filters: { name: route.params.id },
  },
  auto: true,
  onSuccess(data) {
    chapter.fetch()
    let sidebar_items = {
      items: [
        {
          label: 'Details',
          route: `/event/${route.params.id}`,
        },
        {
          label: 'RSVP',
          route: `/event/${route.params.id}/rsvp`,
        },
        {
          label: 'CFP',
          route: `/event/${route.params.id}/cfp`,
        },
        {
          label: 'Volunteers',
          route: `/event/${route.params.id}/volunteers`,
        },
      ],
    }

    if (data.is_paid_event) {
      sidebar_items.items.splice(1, 1, {
        label: 'Tickets',
        route: `/event/${route.params.id}/tickets`,
      })
      sidebar_items.items.push({
        label: 'Check-Ins',
        route: `/event/${route.params.id}/checkins`,
      })
    }

    sidebarMenuItems.value.push(sidebar_items)
  },
})

const chapter = createResource({
  url: 'frappe.client.get_value',
  makeParams() {
    return {
      doctype: 'FOSS Chapter',
      fieldname: ['name', 'chapter_name', 'route'],
      filters: { name: event.data.chapter },
    }
  },
})

provide('chapter', chapter)

usePageMeta(() => {
  return {
    title: 'Manage Event',
  }
})
</script>
