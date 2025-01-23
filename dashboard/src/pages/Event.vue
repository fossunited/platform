<template>
  <div class="flex flex-col md:flex-row">
    <SideNavbar title="Manage Event" :menu-items="sidebarMenuItems" />
    <div class="w-full md:ml-[220px]">
      <RouterView />
    </div>
  </div>
</template>

<script setup>
import { ref, provide, watch } from 'vue'
import { createResource, usePageMeta, createDocumentResource } from 'frappe-ui'
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

const event = createDocumentResource({
  doctype: 'FOSS Chapter Event',
  name: route.params.id,
  auto: true,
})

watch(
  () => event.doc,
  (doc) => {
    if (doc) {
      // If sidebar items already set, don't append items again
      if (sidebarMenuItems.value.length > 1) {
        return
      }
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
            label: 'Partners',
            route: `/event/${route.params.id}/partner`,
          },
          {
            label: 'Volunteers',
            route: `/event/${route.params.id}/volunteers`,
          },
          {
            label: 'Mailing',
            route: `/event/${route.params.id}/mailing`,
          },
        ],
      }

      if (doc.is_paid_event) {
        sidebar_items.items.splice(1, 1, {
          label: 'Tickets',
          route: `/event/${route.params.id}/tickets`,
        })
        sidebar_items.items.push({
          label: 'Check-Ins',
          route: `/event/${route.params.id}/checkins`,
        })
      }

      sidebarMenuItems.value = [...sidebarMenuItems.value, sidebar_items]
    }
  },
)

provide('event', event)

const chapter = createResource({
  url: 'frappe.client.get_value',
  makeParams() {
    return {
      doctype: 'FOSS Chapter',
      fieldname: ['*'],
      filters: { name: event.doc.chapter },
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
