<template>
  <div
    class="relative hidden md:block min-h-0 flex-shrink-0 overflow-hidden hover:overflow-auto"
    :class="toggleSidebar ? '!block' : ''"
  >
    <div
      class="fixed flex justify-between min-h-screen w-[220px] flex-col border-r bg-gray-50 p-4 z-50 transform transition-transform duration-500 ease-in-out"
      :class="toggleSidebar ? 'translate-x-0' : '-translate-x-full md:translate-x-0'"
    >
      <div class="flex flex-col gap-4">
        <slot name="header"> </slot>
        <slot name="branding">
          <div class="mb-3 flex justify-between items-center">
            <div>
              <div class="font-fff text-gray-900 uppercase">FOSS United</div>
              <div class="text-sm mt-2 tracking-wider text-gray-700 uppercase">Dashboard</div>
            </div>
            <Button
              class="block md:hidden -mr-8 !rounded-full w-8 h-8"
              variant="outline"
              icon="arrow-left"
              @click="toggleSidebar = false"
            >
            </Button>
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
              <div class="flex flex-col my-1 gap-1 text-gray-700">
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
                  @click="handleClick()"
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
        <slot name="user-actions">
          <div class="hidden md:flex items-center justify-between text-gray-800 py-2 my-1">
            <div class="flex items-center gap-2">
              <img
                v-if="user_profile.data?.profile_photo"
                :src="user_profile.data?.profile_photo"
                class="w-6 h-6 rounded-full"
              />
              <FeatherIcon v-else name="user" class="w-3 h-3" fill="black" />
              <span class="text-sm font-medium">{{ user_profile.data?.full_name }}</span>
            </div>
            <div>
              <Popover>
                <template #target="{ togglePopover }">
                  <Button icon="more-vertical" variant="ghost" @click="togglePopover()" />
                </template>
                <template #body-main>
                  <div class="flex flex-col gap-1 p-2">
                    <Button
                      class="!justify-start !text-sm rounded-sm cursor-pointer"
                      label="My Profile"
                      :link="createAbsoluteUrlFromRoute('me')"
                      variant="ghost"
                    />
                    <Button
                      class="!justify-start !text-sm rounded-sm cursor-pointer"
                      label="Go To Website"
                      :link="createAbsoluteUrlFromRoute('')"
                      variant="ghost"
                    />
                    <Button
                      variant="ghost"
                      theme="red"
                      class="!justify-start !text-sm rounded-sm cursor-pointer"
                      label="Logout"
                      @click="session.logout.fetch()"
                    />
                  </div>
                </template>
              </Popover>
            </div>
          </div>
        </slot>
        <slot name="footer">
          <p class="text-gray-700 text-xs leading-snug">
            FOSS United Foundation.
            <br />CC-BY-SA.
          </p>
        </slot>
      </div>
    </div>
  </div>

  <!-- For mobile screens -->
  <div class="md:hidden px-4 py-3 flex justify-between bg-white">
    <div class="flex items-center gap-2">
      <Button icon="menu" class="text-black" variant="ghost" @click="toggleSidebar = true" />
    </div>
    <div class="flex items-center gap-2">
      <Popover>
        <template #target="{ togglePopover }">
          <button @click="togglePopover()">
            <img
              v-if="user_profile.data?.profile_photo"
              :src="user_profile.data?.profile_photo"
              class="w-6 h-6 rounded-full"
            />
            <FeatherIcon v-else name="user" class="w-4 h-4" fill="black" />
          </button>
        </template>
        <template #body-main>
          <div class="flex flex-col gap-1 p-2">
            <Button
              class="!justify-start !text-sm rounded-sm cursor-pointer"
              label="My Profile"
              :link="createAbsoluteUrlFromRoute('me')"
              variant="ghost"
            />
            <Button
              class="!justify-start !text-sm rounded-sm cursor-pointer"
              label="Go To Website"
              :link="createAbsoluteUrlFromRoute('')"
              variant="ghost"
            />
            <Button
              variant="ghost"
              theme="red"
              class="!justify-start !text-sm rounded-sm cursor-pointer"
              label="Logout"
              @click="session.logout.fetch()"
            />
          </div>
        </template>
      </Popover>
    </div>
  </div>

  <!-- Dark background overlay -->
  <div
    v-if="toggleSidebar"
    class="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity duration-500 md:hidden"
    @click="toggleSidebar = false"
  ></div>
</template>
<script setup>
import { createResource, FeatherIcon, Popover } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { ref, defineProps, inject } from 'vue'
import { createAbsoluteUrlFromRoute } from '@/helpers/utils'

const route = useRoute()
const session = inject('$session')
const toggleSidebar = ref(false)

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

const user_profile = createResource({
  url: 'fossunited.api.dashboard.get_session_user_profile',
})

if (session.isLoggedIn && session.user != 'Guest' && session.user != 'Administrator') {
  user_profile.fetch()
}

const isMenuItemActive = (menuRoute, index) => {
  if (index == 0 && menuRoute != route.path) {
    return false
  }
  return (
    menuRoute === route.path ||
    menuRoute === '/' + route.path.split('/').filter(Boolean).slice(0, -1).join('/')
  )
}

const handleClick = () => {
  if (window.screen.width < 768) {
    toggleSidebar.value = false
  }
}
</script>
