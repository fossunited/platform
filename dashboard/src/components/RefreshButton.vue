<template>
  <Button>
    <IconRefresh class="w-4 h-4" :class="{ inSpin: 'animate-spin' }" />
  </Button>
</template>
<script setup>
import { IconRefresh } from '@tabler/icons-vue'
import { defineProps } from 'vue'

defineProps({
  inSpin: Boolean,
})
</script>
