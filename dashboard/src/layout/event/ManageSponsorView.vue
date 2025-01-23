<template>
  <ManageSponsorDialog
    v-model:show="showSponsorDialog"
    v-model:sponsor="selectedSponsor"
    :is-new="inAddNew"
    class="z-50"
    @reload:event="event.reload()"
  />
  <div class="flex flex-col gap-4 my-6">
    <div class="flex flex-col gap-2">
      <div class="prose">
        <h2>Sponsors</h2>
      </div>
      <Button label="Add Sponsor" class="w-fit mb-1" @click="handleAddNew" />
      <div v-if="event.doc.sponsor_list.length == 0" class="text-sm text-gray-800">
        No sponsors added for this event.
      </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <SponsorCard
          v-for="sponsor in event.doc.sponsor_list"
          :key="sponsor.name"
          :sponsor="sponsor"
          @edit-sponsor="handleEditSponsor(sponsor)"
        />
      </div>
    </div>
  </div>
</template>
<script setup>
import { inject, ref } from 'vue'

import SponsorCard from '@/components/event/SponsorCard.vue'
import ManageSponsorDialog from '@/components/event/ManageSponsorDialog.vue'

const inAddNew = ref(false)
let selectedSponsor = ref({})
const showSponsorDialog = ref(false)
const event = inject('event')

const handleAddNew = () => {
  inAddNew.value = true
  selectedSponsor.value = {}
  showSponsorDialog.value = true
}

const handleEditSponsor = (sponsor) => {
  inAddNew.value = false
  selectedSponsor.value = sponsor
  showSponsorDialog.value = true
}
</script>
