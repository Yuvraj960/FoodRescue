<template>
  <div :class="['inline-flex items-center font-medium rounded-full transition-all', sizeClasses, colorClasses]">
    <span class="mr-1.5 flex-shrink-0 text-base leading-none">{{ icon }}</span>
    <span class="tracking-wide">{{ label }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  dietary: {
    type: String,
    default: 'VEGETARIAN'
  },
  size: {
    type: String,
    default: 'md' // sm, md, lg
  }
})

const config = {
  VEGETARIAN: {
    label: 'Vegetarian',
    icon: '🟢',
    colorClasses: 'bg-green-100 text-green-800 border border-green-200 shadow-sm'
  },
  NON_VEGETARIAN: {
    label: 'Non-Vegetarian',
    icon: '🔴',
    colorClasses: 'bg-red-100 text-red-800 border border-red-200 shadow-sm'
  },
  VEGAN: {
    label: '100% Pure Vegan',
    icon: '🌱',
    colorClasses: 'bg-emerald-100 text-emerald-800 border border-emerald-300 shadow-sm'
  },
  BAKERY: {
    label: 'Bakery & Bread',
    icon: '🍞',
    colorClasses: 'bg-amber-100 text-amber-900 border border-amber-300 shadow-sm'
  },
  OTHER: {
    label: 'Standard Meal',
    icon: '🍱',
    colorClasses: 'bg-slate-100 text-slate-800 border border-slate-200'
  }
}

const current = computed(() => {
  const key = (props.dietary || 'VEGETARIAN').toUpperCase()
  return config[key] || config.OTHER
})

const label = computed(() => current.value.label)
const icon = computed(() => current.value.icon)
const colorClasses = computed(() => current.value.colorClasses)

const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'px-2 py-0.5 text-xs font-semibold'
    case 'lg':
      return 'px-3.5 py-1.5 text-sm font-bold shadow'
    case 'md':
    default:
      return 'px-2.5 py-1 text-xs font-bold'
  }
})
</script>
