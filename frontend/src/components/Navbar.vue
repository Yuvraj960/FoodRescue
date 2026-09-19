<template>
  <header class="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-slate-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      
      <!-- Brand Logo -->
      <router-link to="/" class="flex items-center space-x-2.5 group">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-green-500 flex items-center justify-center text-white shadow-md shadow-emerald-500/20 group-hover:scale-105 transition-transform">
          <span class="text-xl">🥗</span>
        </div>
        <div>
          <span class="text-xl font-black bg-gradient-to-r from-emerald-700 to-green-600 bg-clip-text text-transparent tracking-tight">FoodRescue</span>
          <span class="hidden sm:inline-block ml-1.5 text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 uppercase tracking-wider">Surplus Hub</span>
        </div>
      </router-link>

      <!-- Main Navigation -->
      <nav class="hidden md:flex items-center space-x-1 lg:space-x-2 text-sm font-medium text-slate-600">
        <router-link to="/browse" class="px-3 py-2 rounded-lg hover:text-emerald-600 hover:bg-emerald-50 transition-colors" active-class="text-emerald-700 bg-emerald-50/80 font-semibold">
          🍱 Browse Food
        </router-link>

        <router-link to="/impact" class="px-3 py-2 rounded-lg hover:text-emerald-600 hover:bg-emerald-50 transition-colors" active-class="text-emerald-700 bg-emerald-50/80 font-semibold">
          🌍 Impact
        </router-link>

        <!-- Provider Specific Navigation -->
        <template v-if="auth.isProvider">
          <router-link to="/dashboard" class="px-3 py-2 rounded-lg hover:text-emerald-600 hover:bg-emerald-50 transition-colors" active-class="text-emerald-700 bg-emerald-50/80 font-semibold">
            Dashboard
          </router-link>
          <router-link to="/create-listing" class="px-3 py-2 rounded-lg hover:text-emerald-600 hover:bg-emerald-50 transition-colors" active-class="text-emerald-700 bg-emerald-50/80 font-semibold">
            ➕ Post Surplus
          </router-link>
          <router-link to="/my-listings" class="px-3 py-2 rounded-lg hover:text-emerald-600 hover:bg-emerald-50 transition-colors" active-class="text-emerald-700 bg-emerald-50/80 font-semibold">
            My Listings
          </router-link>
          <router-link to="/pickup" class="px-3 py-2 rounded-lg hover:text-emerald-600 hover:bg-emerald-50 transition-colors" active-class="text-emerald-700 bg-emerald-50/80 font-semibold">
            Verify Pickup
          </router-link>
        </template>

        <!-- Recipient Specific Navigation -->
        <template v-if="auth.isRecipient">
          <router-link to="/dashboard" class="px-3 py-2 rounded-lg hover:text-emerald-600 hover:bg-emerald-50 transition-colors" active-class="text-emerald-700 bg-emerald-50/80 font-semibold">
            Dashboard
          </router-link>
          <router-link to="/my-reservations" class="px-3 py-2 rounded-lg hover:text-emerald-600 hover:bg-emerald-50 transition-colors" active-class="text-emerald-700 bg-emerald-50/80 font-semibold">
            My Reservations
          </router-link>
          <router-link to="/pickup" class="px-3 py-2 rounded-lg hover:text-emerald-600 hover:bg-emerald-50 transition-colors" active-class="text-emerald-700 bg-emerald-50/80 font-semibold">
            Pickup Pass
          </router-link>
        </template>

        <!-- Admin Navigation -->
        <template v-if="auth.isAdmin">
          <router-link to="/dashboard" class="px-3 py-2 rounded-lg hover:text-emerald-600 hover:bg-emerald-50 transition-colors" active-class="text-emerald-700 bg-emerald-50/80 font-semibold">
            Overview
          </router-link>
          <router-link to="/admin" class="px-3 py-2 rounded-lg hover:text-purple-600 hover:bg-purple-50 transition-colors" active-class="text-purple-700 bg-purple-50 font-semibold">
            🛡️ Admin Panel
          </router-link>
        </template>
      </nav>

      <!-- Right Action Items -->
      <div class="flex items-center space-x-3">
        
        <!-- Quick Demo Switcher (Helps instantly test different roles) -->
        <div class="relative hidden xl:block">
          <select 
            @change="switchDemoUser($event.target.value)"
            class="text-xs bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-700 rounded-lg px-2.5 py-1.5 font-medium cursor-pointer focus:outline-none"
          >
            <option value="" disabled selected>⚡ Switch Demo Role</option>
            <option value="canteen">Canteen (Provider)</option>
            <option value="bakery">Bakery (Provider)</option>
            <option value="shelter">Hope Shelter (Recipient)</option>
            <option value="ngo">Food Army (Recipient)</option>
            <option value="admin">System Admin</option>
          </select>
        </div>

        <!-- Notification Bell -->
        <router-link 
          v-if="auth.isAuthenticated"
          to="/notifications" 
          class="relative p-2 rounded-lg text-slate-500 hover:text-emerald-600 hover:bg-slate-100 transition-colors"
          title="Notifications"
        >
          <span class="text-lg">🔔</span>
          <span 
            v-if="notificationsStore.unreadCount > 0" 
            class="absolute top-1 right-1 flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[10px] font-bold text-white bg-rose-500 rounded-full animate-bounce"
          >
            {{ notificationsStore.unreadCount }}
          </span>
        </router-link>

        <!-- User Profile Pill / Auth Buttons -->
        <template v-if="auth.isAuthenticated">
          <div class="flex items-center space-x-2 pl-2 border-l border-slate-200">
            <div class="text-right hidden sm:block">
              <div class="text-xs font-bold text-slate-800 leading-tight">{{ auth.userName }}</div>
              <div class="text-[10px] font-semibold text-emerald-600 uppercase tracking-wider">
                {{ auth.role }} {{ auth.orgName ? '• ' + auth.orgName : '' }}
              </div>
            </div>
            <button 
              @click="handleLogout" 
              class="text-xs bg-slate-100 hover:bg-rose-50 hover:text-rose-600 text-slate-600 font-semibold px-3 py-1.5 rounded-lg border border-slate-200 transition-colors"
            >
              Sign Out
            </button>
          </div>
        </template>

        <template v-else>
          <router-link to="/login" class="text-sm font-semibold text-slate-700 hover:text-emerald-600 px-3 py-1.5 rounded-lg">
            Sign In
          </router-link>
          <router-link to="/register" class="text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 px-4 py-2 rounded-lg shadow-sm shadow-emerald-600/30 transition-all hover:shadow">
            Join Platform
          </router-link>
        </template>

      </div>
    </div>
  </header>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useNotificationsStore } from '../stores/notifications'

const router = useRouter()
const auth = useAuthStore()
const notificationsStore = useNotificationsStore()

onMounted(() => {
  if (auth.isAuthenticated) {
    notificationsStore.fetchUnreadCount()
  }
})

const handleLogout = () => {
  auth.logout()
  router.push('/login')
}

const switchDemoUser = async (roleKey) => {
  const credentials = {
    canteen: { email: 'canteen@foodrescue.org', password: 'provider123' },
    bakery: { email: 'bakery@foodrescue.org', password: 'provider123' },
    shelter: { email: 'shelter@foodrescue.org', password: 'recipient123' },
    ngo: { email: 'ngo@foodrescue.org', password: 'recipient123' },
    admin: { email: 'admin@foodrescue.org', password: 'admin123' },
  }

  const cred = credentials[roleKey]
  if (cred) {
    const res = await auth.login(cred.email, cred.password)
    if (res.success) {
      notificationsStore.fetchUnreadCount()
      router.push('/dashboard')
    }
  }
}
</script>
