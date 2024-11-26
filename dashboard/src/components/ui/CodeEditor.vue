<template>
  <Codemirror
    v-model="code"
    :style="{ height: '300px' }"
    :autofocus="true"
    :indent-with-tab="true"
    :tab-size="2"
    :extensions="extensions"
    @ready="handleReady"
  />
</template>
<script setup>
import { ref, computed, shallowRef } from 'vue'
import { Codemirror } from 'vue-codemirror'
import { javascript } from '@codemirror/lang-javascript'
import { markdown } from '@codemirror/lang-markdown'
import { html } from '@codemirror/lang-html'
import { json } from '@codemirror/lang-json'

const props = defineProps({
  lang: {
    type: String,
    default: 'html',
  },
})

const code = defineModel({ type: String })

const languages = computed(() => {
  if (props.lang == 'javascript' || props.lang == 'js') {
    return javascript()
  } else if (props.lang == 'markdown' || props.lang == 'md') {
    return markdown()
  } else if (props.lang == 'json') {
    return json()
  }

  return html()
})

const extensions = ref([languages.value])

const view = shallowRef()
const handleReady = (payload) => {
  view.value = payload.view
}

const getCodemirrorStates = () => {
  const state = view.value.state
  const ranges = state.selection.ranges
  const selected = ranges.reduce((r, range) => r + range.to - range.from, 0)
  const cursor = ranges[0].anchor
  const length = state.doc.length
  const lines = state.doc.lines
}
</script>
