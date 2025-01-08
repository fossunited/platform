<template>
  <div v-if="chapter.doc" class="px-4 py-8 md:p-8 w-full z-0">
    <div class="flex flex-col md:flex-row my-4 gap-4 md:justify-between">
      <ChapterHeader :chapter="chapter" />
      <div class="flex justify-between items-start gap-5 md:flex-col md:items-end">
        <Button
          class="w-fit"
          size="md"
          label="Update Details"
          icon-left="edit"
          @click="updateDetails()"
        ></Button>
        <Button
          class="w-fit bg-green-600 text-white hover:bg-green-700 disabled:opacity-80 disabled:text-white disabled:cursor-not-allowed"
          size="md"
          label="See on website"
          icon-left="external-link"
          :disabled="!chapter.doc.is_published"
          @click="redirectRoute(`${chapter.doc.route}`)"
        ></Button>
      </div>
    </div>
    <div class="flex flex-col my-6">
      <div class="font-semibold text-gray-800 border-b-2 pb-2">Banner Image</div>
      <div class="p-2 my-1">
        <img
          :src="getBannerImage()"
          alt="Banner Image"
          class="object-cover rounded-lg w-full aspect-[4.96/1]"
        />
        <div class="flex my-2 gap-2">
          <FileUploader
            :file-types="'image/*'"
            :validate-file="validateFile"
            @success="(file) => setBannerImage(file)"
          >
            <template #default="{ progress, uploading, openFileSelector }">
              <Button
                :variant="'subtle'"
                :size="'md'"
                :label="
                  uploading
                    ? `Uploading ${progress}`
                    : chapter.doc.banner_image
                      ? 'Change Image'
                      : 'Upload Image'
                "
                @click="openFileSelector"
              />
            </template>
          </FileUploader>
          <Button
            v-if="chapter.doc.banner_image"
            :variant="'subtle'"
            theme="red"
            :size="'md'"
            :label="'Remove Image'"
            @click="() => setBannerImage({ file_url: '' })"
          />
        </div>
        <div class="text-sm text-gray-600">
          The ideal dimensions for a banner image are: 1240 x 300 (WxH)
        </div>
      </div>
    </div>
    <div class="flex flex-col my-6">
      <div class="font-semibold text-gray-800 border-b-2 pb-2">Edit Details</div>
      <div class="p-2 my-1 grid sm:grid-cols-1 md:grid-cols-2 gap-4">
        <FormControl
          v-model="chapter.doc.chapter_name"
          :type="'text'"
          size="md"
          :disabled="true"
          :label="chapter.doc.chapter_type == 'FOSS Club' ? 'Club Name' : 'Community Name'"
        />
        <FormControl
          v-model="chapter.doc.chapter_type"
          :type="'text'"
          size="md"
          :disabled="true"
          label="Chapter Type"
        />
        <div class="col-span-2">
          <TextEditor
            label="About Chapter"
            placeholder="Write a description about the chapter"
            :model-value="chapter.doc.about_chapter"
            @update:model-value="($event) => (chapter.doc.about_chapter = $event)"
          />
        </div>
      </div>
      <div class="font-semibold text-gray-800 border-b-2 pb-2">Location</div>
      <div class="p-2 my-1 grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormControl
          v-model="chapter.doc.city"
          :type="'text'"
          :disabled="true"
          size="md"
          label="City"
        />
        <FormControl
          v-model="chapter.doc.state"
          :type="'text'"
          size="md"
          :disabled="true"
          label="State"
        />
        <FormControl
          v-model="chapter.doc.country"
          :type="'text'"
          size="md"
          :disabled="true"
          label="Country"
        />
        <FormControl
          v-model="chapter.doc.google_map_link"
          :type="'text'"
          size="md"
          label="Map Link"
        />
      </div>
      <div class="font-semibold text-gray-800 border-b-2 pb-2">Socials</div>
      <p class="mt-2 text-base text-gray-600 leading-normal">
        Add your social media links to help people connect with you.
        <br />Please enter the whole url of your social media profile.
        <i>Eg: https://twitter.com/fossunited</i>
      </p>
      <div class="p-2 my-1 grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormControl v-model="chapter.doc.email" :type="'email'" size="md" label="Email">
          <template #prefix>
            <IconAt class="w-5 text-gray-800" />
          </template>
        </FormControl>
        <FormControl v-model="chapter.doc.x" :type="'url'" size="md" label="Twitter">
          <template #prefix>
            <IconBrandX class="w-5 text-gray-800" />
          </template>
        </FormControl>
        <FormControl v-model="chapter.doc.facebook" :type="'url'" size="md" label="Facebook">
          <template #prefix>
            <IconBrandFacebook class="w-5 text-gray-800" />
          </template>
        </FormControl>
        <FormControl v-model="chapter.doc.linkedin" :type="'url'" size="md" label="LinkedIn">
          <template #prefix>
            <IconBrandLinkedin class="w-5 text-gray-800" />
          </template>
        </FormControl>
        <FormControl v-model="chapter.doc.instagram" :type="'url'" size="md" label="Instagram">
          <template #prefix>
            <IconBrandInstagram class="w-5 text-gray-800" />
          </template>
        </FormControl>
        <FormControl v-model="chapter.doc.mastodon" :type="'url'" size="md" label="Mastodon">
          <template #prefix>
            <IconBrandMastodon class="w-5 text-gray-800" />
          </template>
        </FormControl>
      </div>
    </div>
  </div>
</template>
<script setup>
import { useRoute } from 'vue-router'
import { createDocumentResource, FormControl, FileUploader } from 'frappe-ui'
import ChapterHeader from '@/components/ChapterHeader.vue'
import { redirectRoute } from '@/helpers/utils'
import { toast } from 'vue-sonner'
import TextEditor from '@/components/ui/TextEditor.vue'
import {
  IconAt,
  IconBrandFacebook,
  IconBrandInstagram,
  IconBrandLinkedin,
  IconBrandMastodon,
  IconBrandX,
} from '@tabler/icons-vue'

const route = useRoute()

const chapter = createDocumentResource({
  doctype: 'FOSS Chapter',
  name: route.params.id,
  fields: ['*'],
  auto: true,
})

const getBannerImage = () => {
  if (chapter.doc.banner_image) {
    return chapter.doc.banner_image
  } else if (chapter.doc.chapter_type == 'FOSS Club') {
    return '/assets/fossunited/images/chapter/foss_club_banner.png'
  } else {
    return '/assets/fossunited/images/chapter/city_community_banner.png'
  }
}

const validateFile = (file) => {
  let extn = file.name.split('.').pop().toLowerCase()
  if (!['png', 'jpg'].includes(extn)) {
    return 'Only PNG and JPG images are allowed'
  }
}
const setBannerImage = (file) => {
  chapter.setValue.submit({
    banner_image: file.file_url,
  })
  if (file.file_url) {
    toast.success('Banner Image updated successfully')
  } else {
    toast.info('Banner Image removed successfully')
  }
}

const updateDetails = () => {
  chapter.save
    .submit()
    .then(() => {
      toast.success('Chapter details updated successfully')
    })
    .catch((error) => {
      toast.error('Failed to update chapter details', {
        description: error.message,
      })
    })
}
</script>
