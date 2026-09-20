<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    
    <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">My Food Listings</h1>
        <p class="text-xs text-slate-500 mt-1">Manage surplus food posts, view real-time balances, and approve/reject recipient reservations.</p>
      </div>
      <router-link 
        to="/create-listing" 
        class="py-2.5 px-4 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-md shadow-emerald-600/25 transition-all"
      >
        ➕ Post New Surplus
      </router-link>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-16">
      <div class="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
      <p class="text-xs font-bold text-slate-500">Loading your listings...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="listings.length === 0" class="text-center py-16 bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
      <div class="text-4xl mb-2">📦</div>
      <h3 class="text-base font-bold text-slate-800">No surplus food posted yet</h3>
      <p class="text-xs text-slate-500 mt-1 mb-4">Post surplus food from your cafeteria or bakery to connect with local NGOs.</p>
      <router-link to="/create-listing" class="text-xs font-bold text-white bg-emerald-600 px-4 py-2 rounded-xl shadow">
        Create Your First Listing
      </router-link>
    </div>

    <!-- Listings Table / Cards -->
    <div v-else class="space-y-4">
      <div 
        v-for="l in listings" 
        :key="l.id"
        class="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4"
      >
        <!-- Top Summary Bar -->
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div class="flex items-center space-x-2 mb-1.5">
              <DietaryBadge :dietary="l.dietary_type" size="sm" />
              <StatusBadge :status="l.status" />
              <CountdownTimer :expiryTime="l.expiry_time" />
            </div>
            <h3 class="text-lg font-black text-slate-900 leading-snug">{{ l.title }}</h3>
            <div class="text-xs text-slate-500 mt-0.5">
              📍 {{ l.location }}, {{ l.city }} • Added {{ formatDate(l.created_at) }}
            </div>
          </div>

          <!-- Portions Badge -->
          <div class="text-right">
            <div class="text-xs font-bold text-slate-400 uppercase tracking-wider">Remaining Portions</div>
            <div class="text-2xl font-black text-emerald-700">{{ l.remaining_quantity }} / {{ l.quantity }} <span class="text-xs text-slate-500 font-normal">{{ l.unit }}</span></div>
            <div class="text-[11px] text-slate-500 font-semibold mt-0.5">
              {{ l.pending_reservations_count }} pending • {{ l.approved_reservations_count }} approved
            </div>
          </div>
        </div>

        <!-- Incoming Reservation Requests Section -->
        <div class="pt-3 border-t border-slate-100">
          <div class="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2.5 flex items-center justify-between">
            <span>🤝 Reservation Requests:</span>
            <button 
              @click="toggleReservations(l.id)" 
              class="text-emerald-600 hover:text-emerald-700 font-semibold"
            >
              {{ expandedListingId === l.id ? 'Hide Requests' : 'View Requests' }}
            </button>
          </div>

          <div v-if="expandedListingId === l.id" class="space-y-2 mt-2">
            <div v-if="getListingReservations(l.id).length === 0" class="text-xs text-slate-400 italic p-3 bg-slate-50 rounded-xl">
              No reservation requests received yet for this listing.
            </div>

            <div 
              v-for="r in getListingReservations(l.id)" 
              :key="r.id"
              class="p-3.5 bg-slate-50 rounded-xl border border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs"
            >
              <div>
                <div class="flex items-center space-x-2">
                  <span class="font-bold text-slate-900">{{ r.recipient?.name }}</span>
                  <span class="text-slate-400 font-normal">({{ r.recipient?.organization_name || 'Community Recipient' }})</span>
                  <StatusBadge :status="r.status" />
                </div>
                <div class="text-slate-500 mt-1">
                  Requested: <strong class="text-slate-800">{{ r.quantity }} {{ l.unit }}</strong> • Code: <code class="bg-white px-1.5 py-0.5 rounded border border-slate-200 font-mono font-bold text-emerald-700">{{ r.pickup_code }}</code>
                </div>
                <div v-if="r.notes" class="text-slate-600 italic mt-0.5">
                  "{{ r.notes }}"
                </div>
              </div>

              <!-- Approve / Reject Actions -->
              <div v-if="r.status === 'PENDING'" class="flex items-center space-x-2">
                <button 
                  @click="approveReservation(r.id)" 
                  class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg shadow-sm"
                >
                  Approve
                </button>
                <button 
                  @click="rejectReservation(r.id)" 
                  class="px-3 py-1.5 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 font-bold rounded-lg"
                >
                  Decline
                </button>
              </div>

              <div v-else-if="r.status === 'APPROVED'" class="text-xs text-blue-700 font-bold">
                ✓ Approved — Awaiting pickup
              </div>

              <div v-else-if="r.status === 'COMPLETED'" class="text-xs text-teal-700 font-bold">
                ✓ Collected
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import DietaryBadge from '../components/DietaryBadge.vue'
import StatusBadge from '../components/StatusBadge.vue'
import CountdownTimer from '../components/CountdownTimer.vue'

const listings = ref([])
const reservations = ref([])
const loading = ref(true)
const expandedListingId = ref(null)

const fetchData = async () => {
  loading.value = true
  try {
    const [lRes, rRes] = await Promise.all([
      api.get('/provider/listings'),
      api.get('/provider/reservations')
    ])
    listings.value = lRes.data
    reservations.value = rRes.data
  } catch (err) {
    console.error('Failed to load provider data', err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

const toggleReservations = (id) => {
  expandedListingId.value = expandedListingId.value === id ? null : id
}

const getListingReservations = (listingId) => {
  return reservations.value.filter(r => r.food_listing_id === listingId)
}

const approveReservation = async (resId) => {
  try {
    await api.put(`/reservations/${resId}/approve`)
    await fetchData()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to approve reservation')
  }
}

const rejectReservation = async (resId) => {
  const reason = prompt('Please enter rejection reason (will be sent to recipient):', 'Capacity reached or timing conflict')
  if (reason === null) return
  try {
    await api.put(`/reservations/${resId}/reject`, { reason })
    await fetchData()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to decline reservation')
  }
}

const formatDate = (isoStr) => {
  if (!isoStr) return ''
  return new Date(isoStr).toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>
