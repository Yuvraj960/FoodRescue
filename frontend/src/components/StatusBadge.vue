<template>
  <span :class="['inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border', statusClasses]">
    <span class="w-1.5 h-1.5 rounded-full mr-1.5" :class="dotColor"></span>
    {{ formattedStatus }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true
  }
})

const config = {
  AVAILABLE: {
    label: 'Available',
    classes: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    dot: 'bg-emerald-500'
  },
  PARTIALLY_RESERVED: {
    label: 'Partially Reserved',
    classes: 'bg-amber-50 text-amber-700 border-amber-200',
    dot: 'bg-amber-500'
  },
  FULLY_RESERVED: {
    label: 'Fully Reserved',
    classes: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    dot: 'bg-indigo-500'
  },
  EXPIRED: {
    label: 'Expired',
    classes: 'bg-slate-100 text-slate-600 border-slate-200',
    dot: 'bg-slate-400'
  },
  COMPLETED: {
    label: 'Completed',
    classes: 'bg-teal-50 text-teal-700 border-teal-200',
    dot: 'bg-teal-500'
  },
  CANCELLED: {
    label: 'Cancelled',
    classes: 'bg-rose-50 text-rose-700 border-rose-200',
    dot: 'bg-rose-500'
  },
  PENDING: {
    label: 'Pending Approval',
    classes: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    dot: 'bg-yellow-500'
  },
  APPROVED: {
    label: 'Ready for Pickup',
    classes: 'bg-blue-50 text-blue-700 border-blue-200',
    dot: 'bg-blue-500'
  },
  REJECTED: {
    label: 'Declined',
    classes: 'bg-red-50 text-red-700 border-red-200',
    dot: 'bg-red-500'
  }
}

const item = computed(() => config[props.status] || {
  label: props.status,
  classes: 'bg-gray-100 text-gray-700 border-gray-200',
  dot: 'bg-gray-400'
})

const formattedStatus = computed(() => item.value.label)
const statusClasses = computed(() => item.value.classes)
const dotColor = computed(() => item.value.dot)
</script>
