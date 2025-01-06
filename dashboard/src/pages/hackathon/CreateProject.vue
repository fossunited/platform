<template>
  <Header />
  <div v-if="hackathon.data" class="flex w-full p-4 items-center justify-center">
    <div class="w-full max-w-screen-xl">
      <Button
        variant="ghost"
        icon-left="arrow-left"
        label="Go Back"
        class="mt-4 mb-2"
        @click="
          router.push({
            name: 'MyHackathonTeam',
          })
        "
      />
      <HackathonHeader :hackathon="hackathon" :show-banner="false" />
      <hr class="my-6" />
      <div v-if="inSelectProjectType" class="grid grid-cols-1 gap-5 md:grid-cols-2 pt-6 md:p-0">
        <div
          class="w-full md:h-40 flex flex-col gap-4 items-center justify-center"
          :class="
            hackathon.data.enable_oss_contributon_projects
              ? 'md:border-r-2 sm:col-span-1'
              : 'md:col-span-2'
          "
        >
          <button
            class="px-4 py-2 w-3/4 text-center uppercase border-2 border-gray-900 md:w-fit font-semibold bg-white hover:bg-gray-900 hover:text-white transition-colors cursor-pointer"
            @click="
              () => {
                inSelectProjectType = false
                inCreateProject = true
              }
            "
          >
            Create Project
          </button>
          <p class="text-base text-center leading-normal">Create and work on your own project.</p>
        </div>
        <div
          v-if="hackathon.data.enable_oss_contributon_projects"
          class="md:hidden w-full text-center font-medium"
        >
          OR
        </div>
        <div
          v-if="hackathon.data.enable_oss_contributon_projects"
          class="w-full md:h-40 flex flex-col gap-4 items-center justify-center"
        >
          <Badge
            v-if="hackathon.data.is_contribution_project_coming_soon"
            label="Coming Soon!"
            size="lg"
            theme="gray"
          />
          <button
            class="px-4 py-2 uppercase w-3/4 text-center border-2 border-gray-900 md:w-fit font-semibold bg-white hover:bg-gray-900 hover:text-white transition-colors cursor-pointer"
            :class="
              hackathon.data.is_contribution_project_coming_soon
                ? 'text-gray-500 border-gray-500 hover:bg-white hover:text-gray-500 hover:cursor-not-allowed'
                : ''
            "
            :disabled="hackathon.data.is_contribution_project_coming_soon"
            @click="
              () => {
                inSelectProjectType = false
                inContribute = true
                project.is_contribution_project = 1
              }
            "
          >
            Contribute
          </button>
          <p
            v-if="
              hackathon.data.is_contribution_project_coming_soon &&
              hackathon.data.contribution_coming_soon_description
            "
            class="text-sm text-center leading-normal"
          >
            {{ hackathon.data.contribution_coming_soon_description }}
          </p>
          <p class="text-base text-center leading-normal">
            Contribute to open-source projects.<br />
            It can be any open-source projects or our partner projects.
          </p>
        </div>
      </div>

      <!-- FOR NEW PROJECTS -->
      <div v-if="inCreateProject">
        <Button
          variant="ghost"
          label="Go Back"
          icon-left="arrow-left"
          @click="
            () => {
              inCreateProject = false
              inSelectProjectType = true
            }
          "
        />
        <div class="prose mt-5 mb-3">
          <h3>Create Project</h3>
        </div>
      </div>

      <!-- FOR CONTRIBUTION PROJECTS -->
      <div v-if="inContribute">
        <Button
          variant="ghost"
          label="Go Back"
          icon-left="arrow-left"
          @click="
            () => {
              inContribute = false
              inSelectProjectType = true
              project.is_contribution_project = 0
              project.is_partner_project = false
            }
          "
        />
        <div
          class="grid grid-cols-1 gap-4 my-4"
          :class="
            hackathon.data.has_partner_projects && hackathon.data.partner_project_guidelines
              ? 'md:grid-cols-2'
              : ''
          "
        >
          <div
            v-if="hackathon.data.contribution_project_guidelines"
            class="w-full bg-gray-50 text-gray-800 rounded p-4"
          >
            <h3 class="text-md font-semibold">Contribution Guidelines</h3>
            <div
              class="prose leading-normal"
              v-html="markdown.render(hackathon.data.contribution_project_guidelines || '')"
            ></div>
          </div>
          <div
            v-if="hackathon.data.partner_project_guidelines && hackathon.data.has_partner_projects"
            class="w-full bg-blue-50 text-blue-800 rounded p-4"
          >
            <h3 class="text-md font-semibold">Partner Project Guidelines</h3>
            <div
              class="prose leading-normal text-blue-800"
              v-html="markdown.render(hackathon.data.partner_project_guidelines || '')"
            ></div>
          </div>
        </div>
        <div v-if="hackathon.data.has_partner_projects">
          <div class="prose my-2 flex flex-col gap-1">
            <h4>Partner Project</h4>
            <p></p>
          </div>
          <FormControl
            v-model="project.is_partner_project"
            type="checkbox"
            label="Contributing to a partner project."
          />
          <div v-if="project.is_partner_project" class="flex flex-col gap-2">
            <div class="text-base mt-4">Select Partner Project</div>
            <RadioGroup
              v-model="project.partner_project"
              class="grid grid-cols-2 md:grid-cols-3 gap-2 my-2"
            >
              <RadioGroupOption
                v-for="partner_project in partner_projects.data"
                :key="partner_project.id"
                v-slot="{ checked }"
                as="template"
                :value="partner_project.name"
                @click="
                  () => {
                    project.repo_link = partner_project.repo_link
                  }
                "
              >
                <div
                  :class="[checked ? 'bg-gray-50 border-gray-700' : 'bg-white ']"
                  class="relative flex cursor-pointer rounded-sm p-4 border focus:outline-none transition-[border]"
                >
                  <div class="flex w-full items-center justify-between">
                    <div class="flex flex-col gap-2 items-start">
                      <img :src="partner_project.logo" class="h-8" />
                      <RadioGroupLabel as="p" class="text-base font-medium">
                        {{ partner_project.project_name }}
                      </RadioGroupLabel>
                      <div class="text-sm">
                        {{ partner_project.about }}
                      </div>
                      <a
                        :href="partner_project.repo_link"
                        class="flex items-center gap-1 mt-3 text-xs text-gray-600 text-center hover:text-gray-800"
                        target="_blank"
                      >
                        <IconBrandGithub class="w-4" />
                        <span> Repo Link </span>
                      </a>
                    </div>
                  </div>
                </div>
              </RadioGroupOption>
            </RadioGroup>
          </div>
          <div class="prose mt-5 mb-3">
            <h4>Additional Details</h4>
          </div>
        </div>
      </div>

      <!-- CREAT PROJECT FORM -->
      <div v-if="inCreateProject || inContribute">
        <div class="flex flex-col md:grid md:grid-cols-2 my-4 gap-4">
          <FormControl v-model="project.title" label="Title &ast;" type="text" />
          <FormControl
            v-model="project.short_description"
            type="text"
            label="Short Description &ast;"
            description="One line description of this project."
          />
          <FormControl
            v-model="project.repo_link"
            label="Repository Link &ast;"
            :disabled="project.is_partner_project"
          />
          <FormControl
            v-model="project.demo_link"
            label="Demo Link"
            description="Demo link for the project. Can be a URL to a video demo, hosted app/website link etc. This can be added later."
          />
          <div class="flex flex-col gap-2 col-span-2">
            <div class="text-xs text-gray-600">Project Description &ast;</div>
            <TextEditor
              :placeholder="'Write a detailed description of your project'"
              :model-value="project.description"
              @update:model-value="($event) => (project.description = $event)"
            />
          </div>
        </div>
        <ErrorMessage :message="errorMessage" class="my-4" />
        <div class="flex flex-row-reverse mb-8">
          <Button
            label="Create Project"
            theme="green"
            variant="solid"
            class="w-full md:w-2/5"
            size="md"
            :loading="createProject.loading"
            @click="handleCreateProject"
          />
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import Header from '@/components/Header.vue'
import HackathonHeader from '@/components/hackathon/HackathonParticipantHeader.vue'
import TextEditor from '@/components/ui/TextEditor.vue'
import Markdownit from 'markdown-it'
import { createResource, FormControl, ErrorMessage, createListResource, Badge } from 'frappe-ui'
import { RadioGroup, RadioGroupLabel, RadioGroupOption } from '@headlessui/vue'
import { useRoute, useRouter } from 'vue-router'
import { onMounted, reactive, ref, watch } from 'vue'
import { toast } from 'vue-sonner'
import { IconBrandGithub } from '@tabler/icons-vue'

const route = useRoute()
const router = useRouter()
const markdown = new Markdownit()

const inSelectProjectType = ref(true)
const inCreateProject = ref(false)
const inContribute = ref(false)

const project = reactive({
  hackathon: '',
  team: '',
  title: '',
  repo_link: '',
  demo_link: '',
  short_description: '',
  description: '',
  is_contribution_project: 0,
  is_partner_project: false,
  partner_project: '',
})

const partner_projects = createListResource({
  doctype: 'FOSS Hackathon Partner Project',
  pageLength: 999,
  fields: ['*'],
})

const hackathon = createResource({
  url: 'fossunited.api.hackathon.get_hackathon_from_permalink',
  params: {
    permalink: route.params.permalink,
  },
  auto: true,
  onSuccess(data) {
    project.hackathon = data.name
    partner_projects.update({
      filters: {
        hackathon: data.name,
      },
    })
    partner_projects.fetch()
  },
})

onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  project.team = params.get('team')
})

watch(
  () => project.is_partner_project,
  (value) => {
    if (!value) {
      project.partner_project = ''
      project.repo_link = ''
    }
  },
)

const errorMessage = ref('')

const validateCreateProject = () => {
  let errors = []

  if (!project.title) {
    errors.push('Title is required')
  }
  if (!project.short_description) {
    errors.push('Write a short description')
  }
  if (!project.description) {
    errors.push('Project description is required')
  }
  if (!project.repo_link) {
    errors.push('Repository link is required')
  }
  if (project.repo_link && !project.repo_link.startsWith('https://')) {
    errors.push('Enter a valid repo link')
  }
  return errors
}

const createProject = createResource({
  url: 'fossunited.api.hackathon.create_project',
  makeParams() {
    return {
      hackathon: project.hackathon,
      team: project.team,
      project: project,
    }
  },
  onSuccess(data) {
    createResource({
      url: 'frappe.client.set_value',
      makeParams() {
        return {
          doctype: 'FOSS Hackathon Team',
          name: route.query.team,
          fieldname: 'project',
          value: data.name,
        }
      },
      auto: true,
    })
    router.push({
      name: 'MyHackathonTeam',
    })
  },
  onError(error) {
    toast.error('Failed to create project')
  },
})

const handleCreateProject = () => {
  const errors = validateCreateProject()
  if (errors.length) {
    errorMessage.value = errors.join(', ')
    return
  } else {
    errorMessage.value = ''
  }
  createProject.fetch()
}
</script>
