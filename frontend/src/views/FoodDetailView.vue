<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    
    <!-- Back Button -->
    <router-link to="/browse" class="inline-flex items-center text-xs font-bold text-slate-500 hover:text-emerald-600 mb-6 transition-colors">
      <span class="mr-1">←</span> Back to All Surplus Listings
    </router-link>

    <div v-if="loading" class="text-center py-20">
      <div class="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
      <p class="text-xs font-bold text-slate-500">Loading food details...</p>
    </div>

    <div v-else-if="error || !listing" class="bg-rose-50 p-6 rounded-2xl border border-rose-200 text-center">
      <h3 class="text-sm font-bold text-rose-800">{{ error || 'Food listing not found' }}</h3>
      <router-link to="/browse" class="mt-3 inline-block text-xs font-bold text-rose-600 underline">Return to Browse</router-link>
    </div>

    <div v-else class="space-y-6">
      
      <!-- Main Detail Header Card -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm">
        
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
          <!-- Prominent Dietary Classification -->
          <div class="flex items-center space-x-2">
            <DietaryBadge :dietary="listing.dietary_type" size="lg" />
            <span class="text-xs font-bold text-slate-400">|</span>
            <span class="text-xs font-bold text-slate-600 bg-slate-100 px-2.5 py-1 rounded-lg">
              📂 {{ listing.category?.name || 'Cooked Food' }}
            </span>
          </div>

          <CountdownTimer :expiryTime="listing.expiry_time" />
        </div>

        <h1 class="text-2xl sm:text-3xl font-black text-slate-900 leading-snug">{{ listing.title }}</h1>
        
        <div class="text-xs text-slate-500 mt-2 flex flex-wrap items-center gap-3">
          <span>🏪 Offered by: <strong class="text-slate-800">{{ listing.organization_name || listing.provider_name }}</strong></span>
          <span>•</span>
          <span>📍 {{ listing.location }}, {{ listing.city }}</span>
          <span>•</span>
          <span>📅 Listed on {{ formatDate(listing.created_at) }}</span>
        </div>

        <!-- Prominent Allergen Warning Box -->
        <div v-if="listing.allergen_info" class="mt-5 p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 flex items-start space-x-3">
          <span class="text-xl">⚠️</span>
          <div>
            <h4 class="text-xs font-bold uppercase tracking-wider">Allergen Information & Ingredients Notice:</h4>
            <p class="text-xs mt-0.5 leading-relaxed">{{ listing.allergen_info }}</p>
          </div>
        </div>

        <!-- Description -->
        <div class="mt-6 pt-6 border-t border-slate-100">
          <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Description & Preparation</h3>
          <p class="text-sm text-slate-700 leading-relaxed whitespace-pre-line">{{ listing.description || 'No detailed preparation notes provided.' }}</p>
        </div>

      </div>

      <!-- Logistics and Stock Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        <!-- Stock & Availability Card -->
        <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">Portions & Inventory</h3>
          
          <div class="flex justify-between items-baseline mb-2">
            <span class="text-xs font-bold text-slate-600">Remaining Portions:</span>
            <span class="text-2xl font-black text-emerald-700">{{ listing.remaining_quantity }} {{ listing.unit }}</span>
          </div>
          <div class="text-xs text-slate-400 mb-3 flex justify-between">
            <span>Initial Batch: {{ listing.quantity }} {{ listing.unit }}</span>
            <span>Status: <strong class="text-slate-700">{{ listing.status }}</strong></span>
          </div>

          <!-- Progress bar -->
          <div class="w-full bg-slate-100 h-3 rounded-full overflow-hidden mb-6">
            <div 
              class="bg-emerald-500 h-3 rounded-full transition-all"
              :style="{ width: `${Math.min(100, Math.round((listing.remaining_quantity / listing.quantity) * 100))}%` }"
            ></div>
          </div>

          <button 
            @click="openModal" 
            :disabled="listing.remaining_quantity <= 0"
            class="w-full py-3 px-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl shadow-lg shadow-emerald-600/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ listing.remaining_quantity > 0 ? 'Reserve This Food Now' : 'Fully Reserved / Unavailable' }}
          </button>
        </div>

        <!-- Pickup Window & Location Card -->
        <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">Pickup Coordination</h3>

          <div class="space-y-3.5 text-xs text-slate-700">
            <div class="p-3 bg-emerald-50/60 rounded-xl border border-emerald-100">
              <div class="font-bold text-emerald-800 mb-1">⏰ Scheduled Collection Window:</div>
              <div>From: <strong>{{ formatDateTime(listing.pickup_start) }}</strong></div>
              <div>Until: <strong>{{ formatDateTime(listing.pickup_end) }}</strong></div>
            </div>

            <div class="flex items-start space-x-2">
              <span class="text-base">📍</span>
              <div>
                <div class="font-bold text-slate-800">Pickup Address:</div>
                <div class="text-slate-600">{{ listing.location }}, {{ listing.city }}</div>
              </div>
            </div>

            <div v-if="listing.provider_phone" class="flex items-center space-x-2">
              <span class="text-base">📞</span>
              <div>
                <span class="font-bold text-slate-800">Contact Number:</span>
                <span class="text-slate-600 ml-1">{{ listing.provider_phone }}</span>
              </div>
            </div>

            <div class="flex items-center space-x-2">
              <span class="text-base">⌛</span>
              <div>
                <span class="font-bold text-slate-800">Hard Expiration:</span>
                <span class="text-slate-600 ml-1">{{ formatDateTime(listing.expiry_time) }}</span>
              </div>
            </div>
          </div>

        </div>

      </div>

    </div>

    <!-- Reserve Modal -->
    <ReserveModal 
      v-if="listing"
      :isOpen="isModalOpen" 
      :listing="listing"
      @close="isModalOpen = false"
      @reserved="onReservedSuccess"
    />

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFoodStore } from '../stores/food'
import { useAuthStore } from '../stores/auth'
import DietaryBadge from '../components/DietaryBadge.vue'
import CountdownTimer from '../components/CountdownTimer.vue'
import ReserveModal from '../components/ReserveModal.vue'

const route = useRoute()
const router = useRouter()
const foodStore = useFoodStore()
const auth = useAuthStore()

const listing = ref(null)
const loading = ref(true)
const error = ref('')
const isModalOpen = ref(false)

onMounted(async () => {
  try {
    const data = await foodStore.fetchListing(route.params.id)
    listing.value = data
  } catch (err) {
    error.value = 'Failed to load listing.'
  } finally {
    loading.value = false
  }
})

const formatDate = (isoStr) => {
  if (!isoStr) return ''
  return new Date(isoStr).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })
}

const formatDateTime = (isoStr) => {
  if (!isoStr) return 'Not specified'
  return new Date(isoStr).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const openModal = () => {
  if (!auth.isAuthenticated) {
    router.push('/login')
    return
  }
  isModalOpen.value = true
}

const onReservedSuccess = () => {
  router.push('/my-reservations')
}
</script>
