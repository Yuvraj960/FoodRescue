<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    
    <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">Admin Moderation & Oversight</h1>
        <p class="text-xs text-slate-500 mt-1">Verify participating organizations, audit user accounts, and monitor platform transactions.</p>
      </div>
      <span class="text-xs font-bold text-purple-800 bg-purple-100 px-3 py-1.5 rounded-xl border border-purple-200">
        🛡️ System Administrator Mode
      </span>
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
      <StatCard title="Total Users" :value="stats.total_users || 0" icon="👥" />
      <StatCard title="Food Providers" :value="stats.providers_count || 0" icon="🏪" />
      <StatCard title="Recipient NGOs" :value="stats.recipients_count || 0" icon="🤝" />
      <StatCard title="Total Listings" :value="stats.total_listings || 0" icon="📦" />
    </div>

    <!-- Organization Verification Table -->
    <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm mb-8">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-sm font-bold uppercase tracking-wider text-slate-700">🏢 Organization Verification Management</h2>
        <span class="text-xs text-slate-400">{{ users.length }} registered entities</span>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs text-slate-600">
          <thead class="bg-slate-50 text-[11px] font-bold uppercase tracking-wider text-slate-400 border-b border-slate-200">
            <tr>
              <th class="p-3">User & Contact</th>
              <th class="p-3">Role</th>
              <th class="p-3">Organization</th>
              <th class="p-3">City</th>
              <th class="p-3">Verification Status</th>
              <th class="p-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="u in users" :key="u.id" class="hover:bg-slate-50/50">
              <td class="p-3">
                <div class="font-bold text-slate-900">{{ u.name }}</div>
                <div class="text-[11px] text-slate-400">{{ u.email }} • {{ u.phone || 'No phone' }}</div>
              </td>
              <td class="p-3">
                <span :class="['px-2 py-0.5 rounded-md font-bold uppercase text-[10px]', u.role === 'provider' ? 'bg-emerald-100 text-emerald-800' : (u.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800')]">
                  {{ u.role }}
                </span>
              </td>
              <td class="p-3 font-semibold text-slate-800">
                {{ u.organization?.name || 'Individual' }}
                <span v-if="u.organization?.org_type" class="text-slate-400 text-[10px] block">({{ u.organization.org_type }})</span>
              </td>
              <td class="p-3">{{ u.city || 'Chandigarh' }}</td>
              <td class="p-3">
                <span v-if="u.is_verified" class="text-emerald-700 font-bold flex items-center space-x-1">
                  <span>✓</span> <span>Verified</span>
                </span>
                <span v-else class="text-amber-600 font-bold flex items-center space-x-1">
                  <span>⏳</span> <span>Unverified</span>
                </span>
              </td>
              <td class="p-3 text-right">
                <button 
                  @click="toggleVerify(u.id)"
                  :class="[
                    'px-3 py-1 rounded-lg text-xs font-bold transition-colors',
                    u.is_verified 
                      ? 'bg-rose-50 text-rose-600 hover:bg-rose-100' 
                      : 'bg-emerald-600 text-white hover:bg-emerald-700 shadow-sm'
                  ]"
                >
                  {{ u.is_verified ? 'Revoke Status' : 'Verify Organization' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import StatCard from '../components/StatCard.vue'

const users = ref([])
const stats = ref({})

const loadAdminData = async () => {
  try {
    const [uRes, sRes] = await Promise.all([
      api.get('/admin/users'),
      api.get('/admin/stats')
    ])
    users.value = uRes.data
    stats.value = sRes.data
  } catch (err) {
    console.error('Failed to load admin data', err)
  }
}

onMounted(loadAdminData)

const toggleVerify = async (userId) => {
  try {
    await api.put(`/admin/users/${userId}/verify`)
    await loadAdminData()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to update verification')
  }
}
</script>
