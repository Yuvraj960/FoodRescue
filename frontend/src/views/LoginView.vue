<template>
  <div class="min-h-[85vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-white p-8 rounded-2xl border border-slate-200 shadow-xl">
      
      <!-- Brand Header -->
      <div class="text-center">
        <div class="w-14 h-14 bg-emerald-100 text-emerald-600 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-3 shadow-inner">
          🥗
        </div>
        <h2 class="text-2xl font-black text-slate-900 tracking-tight">Welcome to FoodRescue</h2>
        <p class="text-xs text-slate-500 mt-1">Surplus food redistribution & zero-waste platform</p>
      </div>

      <!-- Quick 1-Click Demo Logins -->
      <div class="p-3.5 bg-slate-50 border border-slate-200 rounded-xl">
        <div class="text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center justify-between">
          <span>⚡ 1-Click Demo Accounts</span>
          <span class="text-emerald-600 font-normal">Click to fill</span>
        </div>
        <div class="grid grid-cols-2 gap-2 text-xs">
          <button 
            type="button"
            @click="fillCredentials('canteen@foodrescue.org', 'provider123')"
            class="p-2 bg-white hover:bg-emerald-50 border border-slate-200 hover:border-emerald-300 rounded-lg text-left transition-colors"
          >
            <div class="font-bold text-slate-800">Canteen Provider</div>
            <div class="text-[10px] text-slate-400">Campus cafeteria</div>
          </button>
          
          <button 
            type="button"
            @click="fillCredentials('bakery@foodrescue.org', 'provider123')"
            class="p-2 bg-white hover:bg-emerald-50 border border-slate-200 hover:border-emerald-300 rounded-lg text-left transition-colors"
          >
            <div class="font-bold text-slate-800">Bakery Provider</div>
            <div class="text-[10px] text-slate-400">Artisan breads</div>
          </button>

          <button 
            type="button"
            @click="fillCredentials('shelter@foodrescue.org', 'recipient123')"
            class="p-2 bg-white hover:bg-emerald-50 border border-slate-200 hover:border-emerald-300 rounded-lg text-left transition-colors"
          >
            <div class="font-bold text-slate-800">Hope Shelter</div>
            <div class="text-[10px] text-slate-400">Recipient NGO</div>
          </button>

          <button 
            type="button"
            @click="fillCredentials('ngo@foodrescue.org', 'recipient123')"
            class="p-2 bg-white hover:bg-emerald-50 border border-slate-200 hover:border-emerald-300 rounded-lg text-left transition-colors"
          >
            <div class="font-bold text-slate-800">Food Army</div>
            <div class="text-[10px] text-slate-400">Recipient NGO</div>
          </button>
        </div>
        <div class="mt-2 text-center">
          <button 
            type="button"
            @click="fillCredentials('admin@foodrescue.org', 'admin123')"
            class="text-[11px] font-semibold text-purple-600 hover:underline"
          >
            🛡️ Or sign in as System Admin
          </button>
        </div>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Email Address</label>
          <input 
            type="email" 
            v-model="email" 
            required 
            placeholder="name@organization.org"
            class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Password</label>
          <input 
            type="password" 
            v-model="password" 
            required 
            placeholder="••••••••"
            class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
          />
        </div>

        <div v-if="error" class="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl font-medium">
          {{ error }}
        </div>

        <button 
          type="submit" 
          :disabled="loading"
          class="w-full py-3 px-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl shadow-lg shadow-emerald-600/25 transition-all disabled:opacity-50"
        >
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>

      <!-- Footer Link -->
      <div class="text-center text-xs text-slate-500">
        Don't have an account? 
        <router-link to="/register" class="font-bold text-emerald-600 hover:underline">Register your Organization</router-link>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const email = ref('canteen@foodrescue.org')
const password = ref('provider123')
const loading = ref(false)
const error = ref('')

const fillCredentials = (e, p) => {
  email.value = e
  password.value = p
}

const handleSubmit = async () => {
  loading.value = true
  error.value = ''
  const res = await auth.login(email.value, password.value)
  loading.value = false
  if (res.success) {
    router.push('/dashboard')
  } else {
    error.value = res.error
  }
}
</script>
