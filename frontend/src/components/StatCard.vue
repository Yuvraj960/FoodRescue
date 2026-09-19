<template>
  <div class="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex items-center justify-between transition-hover hover:shadow-md">
    <div>
      <p class="text-xs font-medium uppercase tracking-wider text-slate-500 mb-1">{{ title }}</p>
      <div class="text-2xl font-bold text-slate-800 tracking-tight">{{ value }}</div>
      <p v-if="subtitle" class="text-xs text-slate-400 mt-1">{{ subtitle }}</p>
    </div>
    <div :class="['w-12 h-12 rounded-xl flex items-center justify-center text-xl shadow-inner', iconBg]">
      {{ icon }}
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: '📊'
  },
  iconBg: {
    type: String,
    default: 'bg-emerald-50 text-emerald-600'
  }
})
</script>
