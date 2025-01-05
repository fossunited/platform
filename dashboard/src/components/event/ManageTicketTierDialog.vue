<template>
  <Dialog
    v-model="showDialog"
    class="z-50"
    :options="{
      title: inCreateMode ? 'Create Ticket Tier' : 'Manage Ticket Tier',
    }"
  >
    <template #body-content>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-if="!inCreateMode"
          class="col-span-2 flex items-end justify-between border border-gray-600 p-3 border-dashed rounded-sm"
        >
          <div class="flex flex-col gap-2">
            <div class="text-sm text-gray-600">Status</div>
            <div
              class="font-medium text-sm uppercase flex items-center gap-2"
              :class="tier.enabled ? 'text-green-600' : ''"
            >
              <LivePing v-if="tier.enabled" />
              <span>
                {{ tier.enabled ? 'Active' : 'Disabled' }}
              </span>
            </div>
          </div>
          <Button
            :label="tier.enabled ? 'Disable' : 'Enable'"
            :variant="tier.enabled ? 'subtle' : 'solid'"
            class="w-fit"
            @click="toggleTierStatus.fetch()"
          />
        </div>
        <FormControl
          v-if="inCreateMode"
          v-model="modifyTier.enabled"
          label="Enable?"
          type="checkbox"
          class="col-span-2 mb-1"
        />
        <Input v-model="modifyTier.title" label="Title" class="w-full" required />
        <Input v-model="modifyTier.price" label="Price" class="w-full" placeholder="0.00" required>
          <template #input-prefix>
            <IconCurrencyRupee class="h-5 w-5" />
          </template>
        </Input>
        <div>
          <div class="text-sm text-gray-600 mb-1">Closes On</div>
          <DatePicker
            v-model="modifyTier.valid_till"
            variant="subtle"
            input-class="bg-white border-none hover:bg-white px-0"
          />
        </div>
        <Input
          v-model="modifyTier.maximum_tickets"
          label="Maximum Tickets"
          class="w-full"
          placeholder="0"
          required
        />
        <div class="col-span-2">
          <div class="text-sm text-gray-600 mb-1">Description</div>
          <textarea
            v-model="modifyTier.description"
            class="w-full border border-gray-300 rounded-sm p-2 text-base"
            rows="4"
            placeholder="Add a description"
          ></textarea>
          <small class="text-gray-700">You can use <code>Markdown</code>.</small>
        </div>
      </div>
      <ErrorMessage class="mt-2" :message="errorMessages" />
    </template>
    <template #actions>
      <div class="grid grid-cols-2 gap-2">
        <Button label="Cancel" size="sm" @click="showDialog = false" />
        <Button
          v-if="inCreateMode"
          label="Create"
          variant="solid"
          size="sm"
          @click="handleCreate"
        />
        <Button v-else label="Update" variant="solid" size="sm" @click="handleSubmit" />
      </div>
    </template>
  </Dialog>
</template>
<script setup>
import { createResource, Dialog, DatePicker, ErrorMessage, FormControl } from 'frappe-ui'
import { defineProps, defineModel, defineEmits, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { IconCurrencyRupee } from '@tabler/icons-vue'
import Input from '@/components/Input.vue'
import LivePing from '@/components/animation/LivePing.vue'

const props = defineProps({
  tier: {
    type: Object,
    default: () => ({}),
  },
  inCreateMode: {
    type: Boolean,
    default: false,
  },
})
const emit = defineEmits(['update-tier'])

const route = useRoute()

const showDialog = defineModel({
  type: Boolean,
  default: false,
})

const modifyTier = reactive({
  enabled: false,
  title: '',
  price: 0,
  currency: 'INR',
  valid_till: '',
  maximum_tickets: 0,
  description: '',
})

onMounted(() => {
  if (props.tier && !props.inCreateMode) {
    Object.assign(modifyTier, props.tier)
  }
})

const updateTier = createResource({
  url: 'frappe.client.set_value',
  makeParams() {
    return {
      doctype: 'FOSS Ticket Tier',
      name: props.tier.name,
      fieldname: {
        title: modifyTier.title,
        price: modifyTier.price,
        currency: modifyTier.currency,
        valid_till: modifyTier.valid_till,
        maximum_tickets: modifyTier.maximum_tickets,
        description: modifyTier.description,
      },
    }
  },
  onSuccess() {
    emit('update-tier')
    showDialog.value = false
  },
})

const errorMessages = ref('')

const validateTierFields = () => {
  const errors = []
  if (!modifyTier.title) {
    errors.push('Title is required')
  }
  if (!modifyTier.price) {
    errors.push('Price is required')
  }
  if (modifyTier.price <= 0) {
    errors.push('Price should be greater than 0')
  }
  if (!modifyTier.valid_till) {
    errors.push('Closing Date is required')
  }
  if (
    props.tier.valid_till != modifyTier.valid_till &&
    new Date(modifyTier.valid_till) < new Date()
  ) {
    errors.push('Valid till should be a future date')
  }
  if (!modifyTier.maximum_tickets) {
    errors.push('Maximum tickets is required')
  }
  if (modifyTier.maximum_tickets <= 0) {
    errors.push('Maximum tickets should be greater than 0')
  }

  return errors
}

const handleSubmit = () => {
  const errors = validateTierFields()
  if (errors.length) {
    errorMessages.value = errors.join(', ')
    return
  }

  updateTier.fetch()
}

const toggleTierStatus = createResource({
  url: 'frappe.client.set_value',
  makeParams() {
    return {
      doctype: 'FOSS Ticket Tier',
      name: props.tier.name,
      fieldname: 'enabled',
      value: Boolean(!props.tier.enabled),
    }
  },
  onSuccess() {
    emit('update-tier')
  },
})

const createTier = createResource({
  url: 'frappe.client.insert',
  makeParams() {
    return {
      doc: {
        doctype: 'FOSS Ticket Tier',
        title: modifyTier.title,
        price: modifyTier.price,
        currency: modifyTier.currency,
        valid_till: modifyTier.valid_till,
        maximum_tickets: modifyTier.maximum_tickets,
        description: modifyTier.description,
        enabled: modifyTier.enabled,
        parent: route.params.id,
        parentfield: 'tiers',
        parenttype: 'FOSS Chapter Event',
      },
    }
  },
  onSuccess() {
    emit('update-tier')
    showDialog.value = false
  },
})

const handleCreate = () => {
  const errors = validateTierFields()
  if (errors.length) {
    errorMessages.value = errors.join(', ')
    return
  }

  createTier.fetch()
}
</script>
