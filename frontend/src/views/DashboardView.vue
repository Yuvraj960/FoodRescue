<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    
    <!-- Welcome Header -->
    <div class="bg-gradient-to-r from-emerald-800 to-green-700 rounded-3xl p-6 sm:p-8 text-white shadow-lg mb-8 relative overflow-hidden">
      <div class="relative z-10">
        <div class="flex items-center space-x-2 text-emerald-200 text-xs font-bold uppercase tracking-wider mb-2">
          <span>{{ getRoleBadge(auth.role) }}</span>
          <span>•</span>
          <span>{{ auth.orgName || 'Community Member' }}</span>
        </div>
        <h1 class="text-2xl sm:text-4xl font-black tracking-tight">Welcome back, {{ auth.userName }}!</h1>
        <p class="text-xs sm:text-sm text-emerald-100 max-w-xl mt-1.5 leading-relaxed">
          {{ getRoleSubtitle(auth.role) }}
        </p>
      </div>
      <div class="absolute -right-8 -bottom-8 text-9xl opacity-10 select-none">
        🥗
      </div>
    </div>

    <!-- PROVIDER DASHBOARD -->
    <template v-if="auth.isProvider">
      <!-- 4 Core Metrics as specified in README -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard 
          title="Active Listings" 
          :value="providerStats.activeListings" 
          subtitle="Currently live"
          icon="📦" 
          iconBg="bg-emerald-50 text-emerald-600"
        />
        <StatCard 
          title="Meals Available" 
          :value="providerStats.mealsAvailable" 
          subtitle="Awaiting rescue"
          icon="🍱" 
          iconBg="bg-blue-50 text-blue-600"
        />
        <StatCard 
          title="Meals Distributed" 
          :value="providerStats.mealsDistributed" 
          subtitle="Successfully rescued"
          icon="🤝" 
          iconBg="bg-teal-50 text-teal-600"
        />
        <StatCard 
          title="Pending Requests" 
          :value="providerStats.pendingRequests" 
          subtitle="Awaiting your approval"
          icon="⏳" 
          iconBg="bg-amber-50 text-amber-600"
        />
      </div>

      <!-- Provider Quick Actions & Pending Requests -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        
        <!-- Left 2 Cols: Pending Requests Section -->
        <div class="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-sm font-bold uppercase tracking-wider text-slate-700">⏳ Pending Reservation Requests</h2>
            <router-link to="/my-listings" class="text-xs font-semibold text-emerald-600 hover:underline">Manage All Listings →</router-link>
          </div>

          <div v-if="pendingReservations.length === 0" class="text-center py-8 text-xs text-slate-400 bg-slate-50 rounded-xl">
            No pending reservation requests right now.
          </div>

          <div v-else class="space-y-3">
            <div 
              v-for="r in pendingReservations" 
              :key="r.id"
              class="p-4 bg-slate-50 rounded-xl border border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs"
            >
              <div>
                <div class="font-bold text-slate-900 text-sm">{{ r.listing?.title }}</div>
                <div class="text-slate-500 mt-0.5">
                  Requested by: <strong class="text-slate-700">{{ r.recipient?.organization_name || r.recipient?.name }}</strong>
                </div>
                <div class="text-slate-600 font-semibold mt-1">
                  Quantity: <span class="text-emerald-700">{{ r.quantity }} {{ r.listing?.unit }}</span> • Code: <code class="font-mono text-emerald-700">{{ r.pickup_code }}</code>
                </div>
              </div>

              <div class="flex items-center space-x-2">
                <button 
                  @click="approveReservation(r.id)"
                  class="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg shadow-sm"
                >
                  Approve
                </button>
                <button 
                  @click="rejectReservation(r.id)"
                  class="px-3 py-1.5 bg-white hover:bg-rose-50 text-rose-600 border border-slate-200 font-bold rounded-lg"
                >
                  Decline
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Col: Quick Shortcuts -->
        <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col justify-between">
          <div>
            <h3 class="text-sm font-bold uppercase tracking-wider text-slate-700 mb-3">⚡ Provider Actions</h3>
            <p class="text-xs text-slate-500 mb-4 leading-relaxed">Prepare excess meals from today's service and list them with a few clicks.</p>
            
            <div class="space-y-2.5">
              <router-link 
                to="/create-listing" 
                class="block w-full py-2.5 px-4 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl text-center shadow"
              >
                ➕ Post Surplus Food
              </router-link>
              <router-link 
                to="/pickup" 
                class="block w-full py-2.5 px-4 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold rounded-xl text-center"
              >
                📲 Verify Pickup Pass
              </router-link>
              <router-link 
                to="/impact" 
                class="block w-full py-2.5 px-4 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold rounded-xl text-center"
              >
                🌍 View Impact Metrics
              </router-link>
            </div>
          </div>

          <div class="mt-6 pt-4 border-t border-slate-100 text-[11px] text-slate-400">
            Automated Celery Beat engine continuously checks your listings for expiry and notifies recipients.
          </div>
        </div>

      </div>
    </template>

    <!-- RECIPIENT DASHBOARD -->
    <template v-else-if="auth.isRecipient">
      <!-- 4 Core Metrics as specified in README -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard 
          title="Available Donations" 
          :value="recipientStats.availableDonations" 
          subtitle="Active in your area"
          icon="🥗" 
          iconBg="bg-emerald-50 text-emerald-600"
        />
        <StatCard 
          title="My Reservations" 
          :value="recipientStats.myReservations" 
          subtitle="Currently active"
          icon="📋" 
          iconBg="bg-blue-50 text-blue-600"
        />
        <StatCard 
          title="Pending Pickups" 
          :value="recipientStats.pendingPickups" 
          subtitle="Ready for collection"
          icon="🚗" 
          iconBg="bg-amber-50 text-amber-600"
        />
        <StatCard 
          title="Completed Pickups" 
          :value="recipientStats.completedPickups" 
          subtitle="Meals rescued"
          icon="🎉" 
          iconBg="bg-teal-50 text-teal-600"
        />
      </div>

      <!-- Recipient Feeds -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        
        <!-- Left 2 Cols: Fresh Donations Feed with Dietary Tags -->
        <div class="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-sm font-bold uppercase tracking-wider text-slate-700">🍱 Fresh Surplus Food Nearby</h2>
            <router-link to="/browse" class="text-xs font-semibold text-emerald-600 hover:underline">Explore All Listings →</router-link>
          </div>

          <div v-if="freshListings.length === 0" class="text-center py-8 text-xs text-slate-400 bg-slate-50 rounded-xl">
            No active surplus donations available right now.
          </div>

          <div v-else class="space-y-3">
            <div 
              v-for="l in freshListings.slice(0, 3)" 
              :key="l.id"
              class="p-4 bg-slate-50 rounded-xl border border-slate-200 flex flex-wrap items-center justify-between gap-3"
            >
              <div>
                <div class="flex items-center space-x-2 mb-1">
                  <DietaryBadge :dietary="l.dietary_type" size="sm" />
                  <CountdownTimer :expiryTime="l.expiry_time" />
                </div>
                <h4 class="font-bold text-slate-900 text-sm">{{ l.title }}</h4>
                <div class="text-xs text-slate-500 mt-0.5">
                  {{ l.organization_name || l.provider_name }} • <strong>{{ l.remaining_quantity }} {{ l.unit }} available</strong>
                </div>
              </div>

              <router-link 
                :to="`/food/${l.id}`"
                class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-sm transition-colors"
              >
                Reserve
              </router-link>
            </div>
          </div>
        </div>

        <!-- Right Col: Ready Pickup Passes -->
        <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <h3 class="text-sm font-bold uppercase tracking-wider text-slate-700 mb-3">📲 Ready for Pickup</h3>
          
          <div v-if="approvedReservations.length === 0" class="text-xs text-slate-400 py-6 text-center">
            No approved reservations awaiting pickup right now.
          </div>

          <div v-else class="space-y-3">
            <div 
              v-for="appr in approvedReservations.slice(0, 2)" 
              :key="appr.id"
              class="p-3.5 bg-slate-900 text-white rounded-xl shadow"
            >
              <div class="text-[10px] text-emerald-400 uppercase tracking-wider font-bold">Approved Pass</div>
              <div class="font-bold text-xs truncate mt-0.5">{{ appr.listing?.title }}</div>
              <div class="text-xl font-mono font-black text-emerald-400 tracking-widest mt-1">
                {{ appr.pickup_code }}
              </div>
              <div class="text-[10px] text-slate-400 mt-1">
                📍 {{ appr.listing?.location }}
              </div>
            </div>

            <router-link to="/my-reservations" class="block text-center text-xs font-bold text-emerald-600 hover:underline pt-2">
              View All Passes →
            </router-link>
          </div>
        </div>

      </div>
    </template>

    <!-- ADMIN OVERVIEW -->
    <template v-else>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard title="System Users" :value="adminMetrics.total_users || 5" icon="👥" />
        <StatCard title="Food Providers" :value="adminMetrics.providers_count || 2" icon="🏪" />
        <StatCard title="Recipients (NGOs)" :value="adminMetrics.recipients_count || 2" icon="🤝" />
        <StatCard title="Total Listings" :value="adminMetrics.total_listings || 6" icon="📦" />
      </div>

      <div class="p-6 bg-white rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div>
          <h3 class="font-bold text-slate-900 text-base">Platform Administration Panel</h3>
          <p class="text-xs text-slate-500 mt-0.5">Verify food providers, moderate listings, and inspect system-wide audit statistics.</p>
        </div>
        <router-link 
          to="/admin" 
          class="py-2.5 px-5 bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold rounded-xl shadow"
        >
          Open Admin Panel →
        </router-link>
      </div>
    </template>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import StatCard from '../components/StatCard.vue'
import DietaryBadge from '../components/DietaryBadge.vue'
import CountdownTimer from '../components/CountdownTimer.vue'

const auth = useAuthStore()

const providerStats = reactive({
  activeListings: 0,
  mealsAvailable: 0,
  mealsDistributed: 0,
  pendingRequests: 0,
})

const recipientStats = reactive({
  availableDonations: 0,
  myReservations: 0,
  pendingPickups: 0,
  completedPickups: 0,
})

const adminMetrics = ref({})
const pendingReservations = ref([])
const freshListings = ref([])
const approvedReservations = ref([])

onMounted(async () => {
  if (auth.isProvider) {
    await loadProviderDashboard()
  } else if (auth.isRecipient) {
    await loadRecipientDashboard()
  } else if (auth.isAdmin) {
    await loadAdminDashboard()
  }
})

const loadProviderDashboard = async () => {
  try {
    const [lRes, rRes] = await Promise.all([
      api.get('/provider/listings'),
      api.get('/provider/reservations')
    ])
    const listings = lRes.data
    const reservations = rRes.data

    providerStats.activeListings = listings.filter(l => ['AVAILABLE', 'PARTIALLY_RESERVED'].includes(l.status)).length
    providerStats.mealsAvailable = listings
      .filter(l => ['AVAILABLE', 'PARTIALLY_RESERVED'].includes(l.status))
      .reduce((acc, l) => acc + (l.remaining_quantity || 0), 0)
    providerStats.mealsDistributed = reservations
      .filter(r => r.status === 'COMPLETED')
      .reduce((acc, r) => acc + (r.quantity || 0), 0)
    
    pendingReservations.value = reservations.filter(r => r.status === 'PENDING')
    providerStats.pendingRequests = pendingReservations.value.length
  } catch (err) {
    console.error('Failed to load provider dashboard', err)
  }
}

const loadRecipientDashboard = async () => {
  try {
    const [foodRes, resRes] = await Promise.all([
      api.get('/food', { params: { only_active: true } }),
      api.get('/reservations')
    ])
    freshListings.value = foodRes.data
    const myRes = resRes.data

    recipientStats.availableDonations = freshListings.value.length
    recipientStats.myReservations = myRes.filter(r => ['PENDING', 'APPROVED'].includes(r.status)).length
    
    approvedReservations.value = myRes.filter(r => r.status === 'APPROVED')
    recipientStats.pendingPickups = approvedReservations.value.length
    recipientStats.completedPickups = myRes.filter(r => r.status === 'COMPLETED').length
  } catch (err) {
    console.error('Failed to load recipient dashboard', err)
  }
}

const loadAdminDashboard = async () => {
  try {
    const res = await api.get('/admin/stats')
    adminMetrics.value = res.data
  } catch (err) {
    console.error('Failed to load admin stats', err)
  }
}

const approveReservation = async (id) => {
  try {
    await api.put(`/reservations/${id}/approve`)
    await loadProviderDashboard()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to approve')
  }
}

const rejectReservation = async (id) => {
  const reason = prompt('Rejection reason:')
  if (reason === null) return
  try {
    await api.put(`/reservations/${id}/reject`, { reason })
    await loadProviderDashboard()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to reject')
  }
}

const getRoleBadge = (role) => {
  switch (role) {
    case 'provider': return '🏪 FOOD PROVIDER PORTAL'
    case 'recipient': return '🤝 NGO / RECIPIENT PORTAL'
    case 'admin': return '🛡️ ADMINISTRATOR'
    default: return 'PORTAL'
  }
}

const getRoleSubtitle = (role) => {
  switch (role) {
    case 'provider': return 'Review incoming reservation requests, track food expiry, and coordinate handovers.'
    case 'recipient': return 'Find nearby food donations, review dietary specifications, and manage your collection passes.'
    case 'admin': return 'Monitor surplus distribution health, verify organizations, and manage users.'
    default: return 'Connecting surplus food with communities in need.'
  }
}
</script>
