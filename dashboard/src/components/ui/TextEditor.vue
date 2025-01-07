<template>
  <div v-if="editor" class="flex flex-col gap-1 w-full">
    <TextEditorLinkDialog
      v-model:show="showDialog"
      v-model:link-data="linkData"
      v-model:editor="editor"
      @insert-link="handleLinkInsert(editor)"
    />
    <div class="text-base text-gray-600">{{ props.label }}</div>
    <section
      class="flex flex-wrap items-center gap-x-4 border-t border-l border-r border-gray-200 buttons font-mono p-2"
    >
      <button
        class="p-1 rounded-sm"
        :disabled="!editor.can().chain().focus().toggleBold().run()"
        :class="{ 'bg-gray-200': editor.isActive('bold') }"
        @click="editor.chain().focus().toggleBold().run()"
      >
        <IconBold class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :disabled="!editor.can().chain().focus().toggleItalic().run()"
        :class="{ 'bg-gray-200': editor.isActive('italic') }"
        @click="editor.chain().focus().toggleItalic().run()"
      >
        <IconItalic class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :disabled="!editor.can().chain().focus().toggleUnderline().run()"
        :class="{ 'bg-gray-200': editor.isActive('underline') }"
        @click="editor.chain().focus().toggleUnderline().run()"
      >
        <IconUnderline class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :disabled="!editor.can().chain().focus().toggleStrike().run()"
        :class="{ 'bg-gray-200': editor.isActive('strike') }"
        @click="editor.chain().focus().toggleStrike().run()"
      >
        <IconStrikethrough class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{ 'bg-gray-200': editor.isActive('paragraph') }"
        @click="editor.chain().focus().setParagraph().run()"
      >
        <IconPilcrow class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{ 'bg-gray-200': editor.isActive('link') }"
        @click="handleToggleLink(editor)"
      >
        <IconLink class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{
          'bg-gray-200': editor.isActive('heading', { level: 1 }),
        }"
        @click="editor.chain().focus().toggleHeading({ level: 1 }).run()"
      >
        <IconH1 class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{
          'bg-gray-200': editor.isActive('heading', { level: 2 }),
        }"
        @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
      >
        <IconH2 class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{
          'bg-gray-200': editor.isActive('heading', { level: 3 }),
        }"
        @click="editor.chain().focus().toggleHeading({ level: 3 }).run()"
      >
        <IconH3 class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{
          'bg-gray-200': editor.isActive('heading', { level: 4 }),
        }"
        @click="editor.chain().focus().toggleHeading({ level: 4 }).run()"
      >
        <IconH4 class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{
          'bg-gray-200': editor.isActive('heading', { level: 5 }),
        }"
        @click="editor.chain().focus().toggleHeading({ level: 5 }).run()"
      >
        <IconH5 class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{
          'bg-gray-200': editor.isActive('heading', { level: 6 }),
        }"
        @click="editor.chain().focus().toggleHeading({ level: 6 }).run()"
      >
        <IconH6 class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{ 'bg-gray-200': editor.isActive('bulletList') }"
        @click="editor.chain().focus().toggleBulletList().run()"
      >
        <IconList class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{ 'bg-gray-200': editor.isActive('orderedList') }"
        @click="editor.chain().focus().toggleOrderedList().run()"
      >
        <IconListNumbers class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{ 'bg-gray-200': editor.isActive('codeBlock') }"
        @click="editor.chain().focus().toggleCodeBlock().run()"
      >
        <IconCode class="w-5 h-5" />
      </button>
      <button
        class="p-1 rounded-sm"
        :class="{ 'bg-gray-200': editor.isActive('blockquote') }"
        @click="editor.chain().focus().toggleBlockquote().run()"
      >
        <IconBlockquote class="w-5 h-5" />
      </button>
      <button class="p-1 rounded-sm" @click="editor.chain().focus().setHorizontalRule().run()">
        <IconSeparatorHorizontal class="w-5 h-5" />
      </button>
    </section>
    <EditorContent :editor="editor" />
  </div>
</template>
<script setup>
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import Placeholder from '@tiptap/extension-placeholder'
import Link from '@tiptap/extension-link'
import { defineProps, defineEmits, ref, reactive } from 'vue'
import {
  IconBold,
  IconItalic,
  IconUnderline,
  IconStrikethrough,
  IconLink,
  IconPilcrow,
  IconH1,
  IconH2,
  IconH3,
  IconH4,
  IconH5,
  IconH6,
  IconList,
  IconListNumbers,
  IconCode,
  IconBlockquote,
  IconSeparatorHorizontal,
} from '@tabler/icons-vue'
import TextEditorLinkDialog from './TextEditorLinkDialog.vue'

const showDialog = ref(false)
const linkData = reactive({
  previousText: '',
  previousValue: '',
  newText: '',
  newValue: '',
})
const emit = defineEmits(['update:modelValue'])

const props = defineProps({
  placeholder: {
    type: String,
    required: false,
    default: '',
  },
  modelValue: {
    /*
        modelValue is the v-model binding for the editor.
    */
    type: String,
    default: '',
  },
  label: {
    type: String,
    default: '',
  },
})

const editor = useEditor({
  content: props.modelValue,
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML())
  },
  editorProps: {
    attributes: {
      class:
        'border border-gray-200 rounded-sm max-w-none p-2 focus:outline-none min-h-[12rem] max-h-[12rem] overflow-y-auto focus:border-gray-400 prose text-base',
    },
  },
  extensions: [
    StarterKit,
    Underline,
    Placeholder.configure({
      placeholder: props.placeholder,
    }),
    Link.extend({ inclusive: false }).configure({
      protocols: ['ftp', 'mailto'],
      openOnClick: true,
      defaultProtocol: 'https',
      HTMLAttributes: {
        rel: 'noopener noreferrer',
        target: '_blank',
      },
    }),
  ],
})

const handleToggleLink = (editor) => {
  const selectedText = getSelectionText(editor)
  const selectedURL = editor.getAttributes('link').href || '' // Default to empty string

  linkData.previousText = selectedText
  linkData.previousValue = selectedURL
  linkData.newText = selectedText || ''
  linkData.newValue = selectedURL || ''
  showDialog.value = true
}

const getSelectionText = (editor) => {
  const { from, to, empty } = editor.state.selection

  if (empty) {
    return ''
  }

  return editor.state.doc.textBetween(from, to, ' ')
}

const handleLinkInsert = (editor) => {
  let { previousText, previousValue, newText, newValue } = linkData

  if (!newValue) {
    // Case 1: Remove link if URL is empty
    editor.chain().focus().extendMarkRange('link').unsetLink().run()
    showDialog.value = false
    resetLinkData()
    return
  }

  if (!newValue.startsWith('http://') && !newValue.startsWith('https://')) {
    newValue = `https://${newValue}`
  }

  if (previousText === newText && previousValue !== newValue) {
    // Case 2: Update only the URL
    editor.chain().focus().extendMarkRange('link').setLink({ href: newValue }).run()
    showDialog.value = false
    resetLinkData()
    return
  }

  // Case 3: Insert a new link or Change the text
  editor.chain().focus().extendMarkRange('link').unsetLink().run() // Clear any existing link formatting
  editor
    .chain()
    .focus()
    .insertContent(`<a href="${newValue}" target="_blank">${newText}</a>`, { parse: true })
    .run()

  showDialog.value = false
  resetLinkData()
}

const resetLinkData = () => {
  linkData.previousText = ''
  linkData.previousValue = ''
  linkData.newText = ''
  linkData.newValue = ''
}
</script>
