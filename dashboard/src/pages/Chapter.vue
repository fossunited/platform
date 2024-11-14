<template>
  <Dialog
    v-model="showDialog"
    class="z-50"
    :options="{
      title: 'Error',
      message: dialogMessage,
    }"
  />
  <div v-if="chapter.data" class="flex flex-col md:flex-row">
    <SideNavbar title="Manage Chapter" :menu-items="sidebarMenuItems" />
    <div class="w-full md:ml-[220px]">
      <RouterView />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { usePageMeta, createResource, Dialog } from 'frappe-ui'
import { useRoute, useRouter, RouterView } from 'vue-router'
import SideNavbar from '@/components/NewAppSidebar.vue'

const route = useRoute()
const router = useRouter()
const session = inject('$session')
const dialogMessage = ref('')
const showDialog = ref(false)

onMounted(() => {
  isChapterMember.fetch()
})

const sidebarMenuItems = [
  {
    items: [
      {
        icon: 'arrow-left',
        label: 'Go Home',
        route: '/chapter',
      },
    ],
  },
  {
    items: [
      {
        label: 'Details',
        route: `/chapter/${route.params.id}`,
      },
      {
        label: 'Events',
        route: `/chapter/${route.params.id}/events`,
      },
      {
        label: 'Members',
        route: `/chapter/${route.params.id}/members`,
      },
    ],
  },
]

const isChapterMember = createResource({
  url: 'fossunited.api.chapter.check_if_chapter_member',
  makeParams() {
    return {
      chapter: route.params.id,
      user: session.user,
    }
  },
  onSuccess(data) {
    if (data) {
      chapter.fetch()
      return
    }
    dialogMessage.value = 'You are not a member of this chapter'
    showDialog.value = true
    setTimeout(() => {
      router.push('/')
    }, 2000)
  },
  onError(error) {
    dialogMessage.value = error.messages
    showDialog.value = true
  },
})

const chapter = createResource({
  url: 'frappe.client.get',
  makeParams() {
    return {
      doctype: 'FOSS Chapter',
      name: route.params.id,
      fields: ['*'],
    }
  },
})

usePageMeta(() => {
  return {
    title: 'Manage Chapter',
  }
})
</script>
