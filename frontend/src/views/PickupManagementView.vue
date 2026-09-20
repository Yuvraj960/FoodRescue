<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    
    <div class="mb-6">
      <h1 class="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">Pickup Verification & Coordination</h1>
      <p class="text-xs text-slate-500 mt-1">Verify recipient collection passes in person and complete food rescue handovers.</p>
    </div>

    <!-- Provider Code Verification Terminal (If Provider or Admin) -->
    <div v-if="auth.isProvider || auth.isAdmin" class="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm mb-8">
      <h2 class="text-base font-bold text-slate-900 mb-2 flex items-center space-x-2">
        <span>📲</span>
        <span>Recipient Code Verification Terminal</span>
      </h2>
      <p class="text-xs text-slate-500 mb-4">When a volunteer arrives with a pickup pass, enter their 6-character pickup code to confirm handover.</p>

      <form @submit.prevent="verifyCode" class="flex flex-col sm:flex-row gap-3">
        <input 
          type="text" 
          v-model="inputCode" 
          required 
          placeholder="e.g. FR-10492"
          class="flex-1 uppercase font-mono font-bold text-base tracking-wider px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-emerald-500 text-slate-900"
        />
        <button 
          type="submit" 
          :disabled="loading"
          class="py-3 px-6 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-md shadow-emerald-600/25 transition-all disabled:opacity-50 whitespace-nowrap"
        >
          {{ loading ? 'Verifying...' : 'Verify & Complete Pickup' }}
        </button>
      </form>

      <div v-if="verificationSuccess" class="mt-4 p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 font-medium flex items-center space-x-2">
        <span class="text-lg">🎉</span>
        <span>{{ verificationSuccess }}</span>
      </div>

      <div v-if="verificationError" class="mt-4 p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 font-medium">
        {{ verificationError }}
      </div>
    </div>

    <!-- Approved Reservations Ready for Pickup Table -->
    <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
      <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">
        {{ auth.isProvider ? 'Your Approved Reservations Awaiting Collection' : 'Your Active Passes' }}
      </h3>

      <div v-if="activeReservations.length === 0" class="text-xs text-slate-400 text-center py-8">
        No active approved reservations awaiting pickup at this moment.
      </div>

      <div v-else class="divide-y divide-slate-100">
        <div 
          v-for="r in activeReservations" 
          :key="r.id"
          class="py-3.5 flex flex-wrap items-center justify-between gap-3 text-xs"
        >
          <div>
            <div class="font-bold text-slate-900">{{ r.listing?.title || 'Food Donation' }}</div>
            <div class="text-slate-500 mt-0.5">
              Code: <span class="font-mono font-bold text-emerald-700">{{ r.pickup_code }}</span> • {{ r.quantity }} {{ r.listing?.unit || 'portions' }}
              <span v-if="auth.isProvider">• Recipient: {{ r.recipient?.name }} ({{ r.recipient?.organization_name }})</span>
            </div>
          </div>

          <div class="flex items-center space-x-2">
            <span class="text-[11px] font-semibold text-blue-700 bg-blue-50 px-2.5 py-1 rounded-full border border-blue-200">
              Ready for Collection
            </span>
            <button 
              v-if="auth.isProvider"
              @click="quickConfirm(r)" 
              class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg transition-colors"
            >
              Confirm Handover
            </button>
          </div>
        </div>
      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const inputCode = ref('')
const loading = ref(false)
const verificationSuccess = ref('')
const verificationError = ref('')
const activeReservations = ref([])

const loadReservations = async () => {
  try {
    const url = auth.isProvider ? '/provider/reservations' : '/reservations'
    const res = await api.get(url)
    // Filter for APPROVED status (ready for pickup)
    activeReservations.value = res.data.filter(r => r.status === 'APPROVED')
  } catch (err) {
    console.error('Failed to load reservations', err)
  }
}

onMounted(loadReservations)

const verifyCode = async () => {
  loading.value = true
  verificationSuccess.value = ''
  verificationError.value = ''

  const code = inputCode.value.trim().toUpperCase()
  const matched = activeReservations.value.find(r => r.pickup_code === code)

  if (!matched) {
    verificationError.value = `No approved reservation found matching pickup code '${code}'. Check code or approval status.`
    loading.value = false
    return
  }

  try {
    const res = await api.put(`/reservations/${matched.id}/pickup`, { pickup_code: code })
    verificationSuccess.value = `Handover verified! Rescued ${matched.quantity} portions of '${matched.listing?.title}'. Impact statistics updated!`
    inputCode.value = ''
    await loadReservations()
  } catch (err) {
    verificationError.value = err.response?.data?.error || 'Verification failed.'
  } finally {
    loading.value = false
  }
}

const quickConfirm = async (reservation) => {
  inputCode.value = reservation.pickup_code
  await verifyCode()
}
</script>
