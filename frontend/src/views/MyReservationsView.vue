<template>
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    
    <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">My Food Reservations</h1>
        <p class="text-xs text-slate-500 mt-1">Track reservation approvals, access your digital pickup pass, and manage food collection.</p>
      </div>
      <router-link 
        to="/browse" 
        class="py-2.5 px-4 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-md shadow-emerald-600/25 transition-all"
      >
        🍱 Browse More Food
      </router-link>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-16">
      <div class="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
      <p class="text-xs font-bold text-slate-500">Loading your reservations...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="reservations.length === 0" class="text-center py-16 bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
      <div class="text-4xl mb-2">🤝</div>
      <h3 class="text-base font-bold text-slate-800">No active food reservations</h3>
      <p class="text-xs text-slate-500 mt-1 mb-4">You haven't reserved any surplus food yet. Browse available donations from nearby restaurants and bakeries.</p>
      <router-link to="/browse" class="text-xs font-bold text-white bg-emerald-600 px-4 py-2 rounded-xl shadow">
        Find Surplus Food
      </router-link>
    </div>

    <!-- Reservation Cards Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div 
        v-for="r in reservations" 
        :key="r.id"
        class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col justify-between"
      >
        <div>
          <!-- Header Status & Dietary -->
          <div class="flex items-center justify-between gap-2 mb-3">
            <StatusBadge :status="r.status" />
            <DietaryBadge :dietary="r.listing?.dietary_type" size="sm" />
          </div>

          <!-- Food Title -->
          <h3 class="text-lg font-black text-slate-900 leading-snug">{{ r.listing?.title || 'Food Listing' }}</h3>
          
          <div class="text-xs text-slate-500 mt-1">
            Offered by: <strong class="text-slate-800">{{ r.listing?.organization_name || r.listing?.provider_name }}</strong>
          </div>

          <!-- Digital Collection Pass -->
          <div class="mt-4 p-4 rounded-xl bg-gradient-to-br from-slate-900 to-slate-800 text-white shadow-md">
            <div class="flex justify-between items-center text-xs text-slate-300 mb-1">
              <span>DIGITAL PICKUP PASS</span>
              <span>{{ r.quantity }} {{ r.listing?.unit || 'portions' }}</span>
            </div>
            <div class="text-2xl font-mono font-black tracking-wider text-emerald-400 py-1">
              {{ r.pickup_code }}
            </div>
            <div class="text-[10px] text-slate-400 mt-1">
              Show this code to provider staff upon arrival for collection verification.
            </div>
          </div>

          <!-- Pickup Time & Location Details -->
          <div class="mt-4 space-y-2 text-xs text-slate-600 bg-slate-50 p-3.5 rounded-xl border border-slate-100">
            <div class="flex items-center justify-between">
              <span class="font-semibold text-slate-500">⏰ Collection Window:</span>
              <span class="font-bold text-slate-800">{{ formatHour(r.listing?.pickup_start) }} - {{ formatHour(r.listing?.pickup_end) }}</span>
            </div>
            <div class="flex items-start justify-between">
              <span class="font-semibold text-slate-500">📍 Location:</span>
              <span class="font-bold text-slate-800 text-right">{{ r.listing?.location }}, {{ r.listing?.city }}</span>
            </div>
            <div v-if="r.notes" class="pt-2 border-t border-slate-200/60 text-[11px] text-slate-500 italic">
              Your note: "{{ r.notes }}"
            </div>
            <div v-if="r.provider_notes" class="pt-2 border-t border-slate-200/60 text-[11px] text-rose-600 font-semibold">
              Provider note: "{{ r.provider_notes }}"
            </div>
          </div>
        </div>

        <!-- Action Footer -->
        <div class="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between">
          <span class="text-[11px] text-slate-400">
            Reserved {{ formatDate(r.reserved_at) }}
          </span>

          <button 
            v-if="['PENDING', 'APPROVED'].includes(r.status)"
            @click="cancelReservation(r.id)"
            class="text-xs font-bold text-rose-600 hover:text-rose-700 hover:bg-rose-50 px-3 py-1.5 rounded-lg transition-colors border border-rose-200"
          >
            Cancel Reservation
          </button>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import StatusBadge from '../components/StatusBadge.vue'
import DietaryBadge from '../components/DietaryBadge.vue'

const reservations = ref([])
const loading = ref(true)

const fetchReservations = async () => {
  loading.value = true
  try {
    const res = await api.get('/reservations')
    reservations.value = res.data
  } catch (err) {
    console.error('Failed to load reservations', err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchReservations)

const cancelReservation = async (id) => {
  if (!confirm('Are you sure you want to cancel this reservation? The portions will be released back to the food listing immediately.')) {
    return
  }
  try {
    await api.put(`/reservations/${id}/cancel`)
    await fetchReservations()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to cancel reservation')
  }
}

const formatHour = (isoStr) => {
  if (!isoStr) return ''
  return new Date(isoStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const formatDate = (isoStr) => {
  if (!isoStr) return ''
  return new Date(isoStr).toLocaleDateString([], { month: 'short', day: 'numeric' })
}
</script>
