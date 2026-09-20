<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    
    <!-- Hero / Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-black text-slate-900 tracking-tight">Available Surplus Food Donations</h1>
      <p class="text-sm text-slate-500 mt-1">Discover, verify dietary specifications, and reserve surplus food before it expires.</p>
    </div>

    <!-- Prominent Dietary Quick Filters (Prominently Highlighted for NGOs) -->
    <div class="mb-6 bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
      <div class="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2.5 flex items-center justify-between">
        <span>🥗 Filter by Food Classification (Dietary Type):</span>
        <span class="text-slate-400 font-normal">Know what food it is before booking</span>
      </div>
      <div class="flex flex-wrap gap-2">
        <button 
          v-for="d in dietaryOptions" 
          :key="d.value"
          @click="selectDietary(d.value)"
          :class="[
            'px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-1.5 border',
            foodStore.filters.dietary_type === d.value 
              ? 'bg-emerald-600 text-white border-emerald-600 shadow-md shadow-emerald-600/25' 
              : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100 hover:border-slate-300'
          ]"
        >
          <span>{{ d.icon }}</span>
          <span>{{ d.label }}</span>
        </button>
      </div>
    </div>

    <!-- Search and Location Filters -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-8">
      <div class="md:col-span-2 relative">
        <input 
          type="text" 
          v-model="foodStore.filters.search"
          @input="debounceSearch"
          placeholder="🔍 Search food title, ingredients, location..." 
          class="w-full pl-4 pr-10 py-3 rounded-xl border border-slate-300 text-sm bg-white focus:ring-2 focus:ring-emerald-500"
        />
        <button 
          v-if="foodStore.filters.search" 
          @click="clearSearch"
          class="absolute right-3 top-3.5 text-xs text-slate-400 hover:text-slate-600 font-bold"
        >
          ✕
        </button>
      </div>

      <div>
        <select 
          v-model="foodStore.filters.city" 
          @change="foodStore.fetchListings()"
          class="w-full py-3 px-4 rounded-xl border border-slate-300 text-sm bg-white focus:ring-2 focus:ring-emerald-500 font-medium text-slate-700"
        >
          <option value="">📍 All Cities</option>
          <option value="Chandigarh">Chandigarh</option>
          <option value="Mohali">Mohali</option>
          <option value="Panchkula">Panchkula</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="foodStore.loading" class="text-center py-16">
      <div class="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
      <p class="text-xs font-bold text-slate-500">Checking for fresh surplus listings...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="foodStore.listings.length === 0" class="text-center py-16 bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
      <div class="text-4xl mb-3">🍲</div>
      <h3 class="text-lg font-bold text-slate-800">No surplus food listings found</h3>
      <p class="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-4">No active food matches your current dietary or location filters. Try clearing your filters or check back shortly.</p>
      <button 
        @click="resetFilters" 
        class="text-xs font-bold text-emerald-600 bg-emerald-50 hover:bg-emerald-100 px-4 py-2 rounded-xl transition-colors"
      >
        Clear All Filters
      </button>
    </div>

    <!-- Food Cards Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="listing in foodStore.listings" 
        :key="listing.id"
        class="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-lg transition-all flex flex-col justify-between group"
      >
        <!-- Card Top Section -->
        <div class="p-5">
          
          <!-- Badges Bar -->
          <div class="flex items-center justify-between gap-2 mb-3">
            <DietaryBadge :dietary="listing.dietary_type" size="md" />
            <CountdownTimer :expiryTime="listing.expiry_time" />
          </div>

          <!-- Title & Provider -->
          <router-link :to="`/food/${listing.id}`" class="block group-hover:text-emerald-700 transition-colors">
            <h3 class="text-lg font-black text-slate-900 leading-snug line-clamp-2">{{ listing.title }}</h3>
          </router-link>

          <div class="text-xs text-slate-500 mt-1 flex items-center space-x-1">
            <span>🏪</span>
            <span class="font-semibold text-slate-700">{{ listing.organization_name || listing.provider_name }}</span>
            <span>•</span>
            <span>📍 {{ listing.city }}</span>
          </div>

          <!-- Description -->
          <p class="text-xs text-slate-600 mt-3 line-clamp-2 leading-relaxed">
            {{ listing.description || 'Fresh surplus food available for reservation and community pickup.' }}
          </p>

          <!-- Allergen Notice if present -->
          <div v-if="listing.allergen_info" class="mt-2.5 p-2 bg-amber-50/80 rounded-lg text-[11px] text-amber-900 border border-amber-200/60 flex items-start space-x-1.5">
            <span>⚠️</span>
            <span class="line-clamp-1"><strong class="font-bold">Allergens:</strong> {{ listing.allergen_info }}</span>
          </div>

          <!-- Remaining Portions Meter -->
          <div class="mt-4 p-3 bg-slate-50 rounded-xl border border-slate-100">
            <div class="flex justify-between items-center text-xs mb-1.5">
              <span class="font-bold text-slate-700">Available:</span>
              <span class="font-black text-emerald-700">{{ listing.remaining_quantity }} / {{ listing.quantity }} {{ listing.unit }}</span>
            </div>
            <!-- Progress bar -->
            <div class="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
              <div 
                class="bg-emerald-500 h-2 rounded-full transition-all"
                :style="{ width: `${Math.min(100, Math.round((listing.remaining_quantity / listing.quantity) * 100))}%` }"
              ></div>
            </div>
          </div>

          <!-- Pickup Time Slot -->
          <div class="mt-3 text-[11px] text-slate-500 flex items-center justify-between">
            <span>⏰ Pickup Window:</span>
            <span class="font-bold text-slate-700">{{ formatHour(listing.pickup_start) }} - {{ formatHour(listing.pickup_end) }}</span>
          </div>

        </div>

        <!-- Card Action Footer -->
        <div class="p-4 bg-slate-50/70 border-t border-slate-100 flex items-center space-x-2">
          <router-link 
            :to="`/food/${listing.id}`"
            class="flex-1 text-center py-2.5 px-3 rounded-xl border border-slate-200 bg-white text-xs font-bold text-slate-700 hover:bg-slate-100 transition-colors"
          >
            Details
          </router-link>

          <button 
            @click="openReserveModal(listing)"
            :disabled="listing.remaining_quantity <= 0"
            class="flex-1 py-2.5 px-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-sm shadow-emerald-600/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ listing.remaining_quantity > 0 ? 'Reserve Food' : 'Fully Reserved' }}
          </button>
        </div>

      </div>
    </div>

    <!-- Reservation Modal -->
    <ReserveModal 
      v-if="selectedListing"
      :isOpen="isModalOpen" 
      :listing="selectedListing"
      @close="isModalOpen = false"
      @reserved="onReservedSuccess"
    />

    <!-- Notification Toast -->
    <div 
      v-if="toastMessage" 
      class="fixed bottom-6 right-6 z-50 bg-slate-900 text-white text-xs font-bold px-4 py-3 rounded-xl shadow-2xl flex items-center space-x-2 animate-slide-up"
    >
      <span>🎉</span>
      <span>{{ toastMessage }}</span>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFoodStore } from '../stores/food'
import { useAuthStore } from '../stores/auth'
import DietaryBadge from '../components/DietaryBadge.vue'
import CountdownTimer from '../components/CountdownTimer.vue'
import ReserveModal from '../components/ReserveModal.vue'

const router = useRouter()
const foodStore = useFoodStore()
const auth = useAuthStore()

const dietaryOptions = [
  { label: 'All Diets', value: 'ALL', icon: '🍽️' },
  { label: '100% Vegetarian', value: 'VEGETARIAN', icon: '🟢' },
  { label: 'Non-Vegetarian', value: 'NON_VEGETARIAN', icon: '🔴' },
  { label: 'Pure Vegan', value: 'VEGAN', icon: '🌱' },
  { label: 'Bakery & Bread', value: 'BAKERY', icon: '🍞' }
]

const selectedListing = ref(null)
const isModalOpen = ref(false)
const toastMessage = ref('')
let searchTimeout = null

onMounted(async () => {
  await foodStore.fetchCategories()
  await foodStore.fetchListings()
})

const selectDietary = (val) => {
  foodStore.filters.dietary_type = val
  foodStore.fetchListings()
}

const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    foodStore.fetchListings()
  }, 350)
}

const clearSearch = () => {
  foodStore.filters.search = ''
  foodStore.fetchListings()
}

const resetFilters = () => {
  foodStore.filters.search = ''
  foodStore.filters.city = ''
  foodStore.filters.dietary_type = 'ALL'
  foodStore.fetchListings()
}

const formatHour = (isoStr) => {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const openReserveModal = (listing) => {
  if (!auth.isAuthenticated) {
    router.push('/login')
    return
  }
  selectedListing.value = listing
  isModalOpen.value = true
}

const onReservedSuccess = (data) => {
  toastMessage.value = `Reservation submitted! Pickup code: ${data.reservation.pickup_code}`
  foodStore.fetchListings()
  setTimeout(() => {
    toastMessage.value = ''
  }, 5000)
}
</script>
