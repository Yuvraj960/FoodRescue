<template>
  <div :class="['inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-md border', timerClass]">
    <span class="mr-1">⏱️</span>
    <span>{{ displayText }}</span>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'

const props = defineProps({
  expiryTime: {
    type: String,
    required: true
  }
})

const now = ref(new Date())
let intervalId = null

const updateNow = () => {
  now.value = new Date()
}

onMounted(() => {
  intervalId = setInterval(updateNow, 1000)
})

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)
})

const diffMs = computed(() => {
  if (!props.expiryTime) return 0
  const expiry = new Date(props.expiryTime)
  return expiry.getTime() - now.value.getTime()
})

const isExpired = computed(() => diffMs.value <= 0)

const displayText = computed(() => {
  if (isExpired.value) return 'Expired'

  const totalSec = Math.floor(diffMs.value / 1000)
  const hours = Math.floor(totalSec / 3600)
  const minutes = Math.floor((totalSec % 3600) / 60)
  const seconds = totalSec % 60

  if (hours > 0) {
    return `${hours}h ${minutes}m remaining`
  }
  if (minutes > 0) {
    return `${minutes}m ${seconds}s left`
  }
  return `${seconds}s left (Urgent!)`
})

const timerClass = computed(() => {
  if (isExpired.value) {
    return 'bg-gray-100 text-gray-500 border-gray-200'
  }
  const totalMinutes = Math.floor(diffMs.value / (1000 * 60))
  if (totalMinutes < 60) {
    return 'bg-red-50 text-red-700 border-red-200 animate-pulse font-bold'
  }
  if (totalMinutes < 180) {
    return 'bg-amber-50 text-amber-800 border-amber-200'
  }
  return 'bg-blue-50 text-blue-700 border-blue-200'
})
</script>
