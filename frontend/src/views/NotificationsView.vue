<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    
    <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">Notification Center</h1>
        <p class="text-xs text-slate-500 mt-1">Rule-based matches, reservation updates, and food expiration alerts.</p>
      </div>
      <button 
        v-if="notificationsStore.unreadCount > 0"
        @click="notificationsStore.markAllRead()"
        class="text-xs font-bold text-emerald-700 hover:text-emerald-800 bg-emerald-50 hover:bg-emerald-100 px-3.5 py-2 rounded-xl transition-colors border border-emerald-200"
      >
        ✓ Mark All as Read
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="notificationsStore.loading" class="text-center py-16">
      <div class="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
      <p class="text-xs font-bold text-slate-500">Checking for alerts...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="notificationsStore.notifications.length === 0" class="text-center py-16 bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
      <div class="text-4xl mb-2">🔔</div>
      <h3 class="text-base font-bold text-slate-800">You're all caught up!</h3>
      <p class="text-xs text-slate-500 mt-1">New surplus food matches and reservation updates will appear here.</p>
    </div>

    <!-- Notifications List -->
    <div v-else class="space-y-3">
      <div 
        v-for="n in notificationsStore.notifications" 
        :key="n.id"
        :class="[
          'p-4 rounded-2xl border transition-all flex items-start space-x-3.5',
          n.is_read ? 'bg-white border-slate-200 opacity-80' : 'bg-emerald-50/40 border-emerald-200 shadow-sm'
        ]"
      >
        <div class="w-9 h-9 rounded-xl flex items-center justify-center text-lg flex-shrink-0 bg-white border border-slate-100 shadow-sm">
          {{ getTypeIcon(n.notification_type) }}
        </div>

        <div class="flex-1 text-xs">
          <div class="flex items-center justify-between">
            <h4 class="font-bold text-slate-900 text-sm leading-tight">{{ n.title }}</h4>
            <span class="text-[10px] text-slate-400">{{ formatDate(n.created_at) }}</span>
          </div>
          <p class="text-slate-600 mt-1 leading-relaxed">{{ n.message }}</p>

          <div class="mt-2.5 flex items-center space-x-3">
            <router-link 
              v-if="n.reference_id"
              :to="`/food/${n.reference_id}`" 
              class="font-bold text-emerald-700 hover:underline"
            >
              View Listing →
            </router-link>

            <button 
              v-if="!n.is_read"
              @click="notificationsStore.markAsRead(n.id)"
              class="text-slate-400 hover:text-slate-700 font-semibold"
            >
              Mark Read
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useNotificationsStore } from '../stores/notifications'

const notificationsStore = useNotificationsStore()

onMounted(() => {
  notificationsStore.fetchNotifications()
})

const getTypeIcon = (type) => {
  switch (type) {
    case 'MATCH': return '🥗'
    case 'RESERVATION': return '🤝'
    case 'EXPIRY': return '⏱️'
    case 'REMINDER': return '⏰'
    default: return '🔔'
  }
}

const formatDate = (isoStr) => {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return d.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>
