<template>
  <header
    class="sticky top-0 z-50 flex items-center justify-between border-b bg-white px-5 py-2.5"
  >
    <div class="flex gap-1">
      <FossUnitedLogo class="w-auto h-8" fill="black"></FossUnitedLogo>
    </div>
    <div v-if="session.isLoggedIn" class="flex items-center">
      <Dropdown
        :options="[
          {
            label: 'My Profile',
            icon: 'user',
            onClick: redirectToProfile,
          },
          {
            label: 'Go to website',
            icon: 'globe',
            onClick: goToPublicSite,
          },
          {
            label: 'Logout',
            icon: 'log-out',
            onClick: () => {
              session.logout.fetch()
            },
          },
        ]"
      >
        <Avatar
          v-if="user_profile.data"
          :shape="'circle'"
          class="cursor-pointer"
          :image="
            user_profile.data.profile_photo ||
            '/assets/fossunited/images/defaults/user_profile_image.png'
          "
          :label="user_profile.data.full_name[0].toUpperCase()"
          size="xl"
        />
      </Dropdown>
    </div>
    <div v-else>
      <a href="/login" class="text-black font-medium text-base hover:text-gray-800">Login</a>
    </div>
  </header>
</template>
<script setup>
import { inject, computed } from 'vue'
import { Avatar, Dropdown, createResource } from 'frappe-ui'
import FossUnitedLogo from '@/components/FossUnitedLogo.vue'

const session = inject('$session')

const user_profile = createResource({
  url: 'fossunited.api.dashboard.get_session_user_profile',
})

if (session.isLoggedIn && session.user != 'Guest' && session.user != 'Administrator') {
  user_profile.fetch()
}

const redirectToProfile = () => {
  window.location.pathname = '/me'
}

const goToPublicSite = () => {
  window.location.pathname = ''
}
</script>
