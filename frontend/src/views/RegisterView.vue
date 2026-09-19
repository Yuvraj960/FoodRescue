<template>
  <div class="min-h-[85vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-lg w-full space-y-6 bg-white p-8 rounded-2xl border border-slate-200 shadow-xl">
      
      <!-- Brand Header -->
      <div class="text-center">
        <h2 class="text-2xl font-black text-slate-900 tracking-tight">Join FoodRescue</h2>
        <p class="text-xs text-slate-500 mt-1">Register as a Food Provider or Recipient Organization</p>
      </div>

      <!-- Role Selection Tabs -->
      <div class="grid grid-cols-2 gap-2 p-1.5 bg-slate-100 rounded-xl">
        <button 
          type="button" 
          @click="role = 'provider'"
          :class="['py-2.5 text-xs font-bold rounded-lg transition-all', role === 'provider' ? 'bg-white text-emerald-700 shadow-sm' : 'text-slate-600 hover:text-slate-900']"
        >
          🏪 Food Provider
          <span class="block text-[10px] font-normal text-slate-400">Restaurant, Canteen, Bakery</span>
        </button>

        <button 
          type="button" 
          @click="role = 'recipient'"
          :class="['py-2.5 text-xs font-bold rounded-lg transition-all', role === 'recipient' ? 'bg-white text-emerald-700 shadow-sm' : 'text-slate-600 hover:text-slate-900']"
        >
          🤝 Food Recipient
          <span class="block text-[10px] font-normal text-slate-400">NGO, Shelter, Volunteer</span>
        </button>
      </div>

      <!-- Registration Form -->
      <form @submit.prevent="handleRegister" class="space-y-4">
        
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Your Full Name</label>
            <input 
              type="text" 
              v-model="name" 
              required 
              placeholder="e.g. Ramesh Verma"
              class="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Email Address</label>
            <input 
              type="email" 
              v-model="email" 
              required 
              placeholder="contact@domain.com"
              class="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Password</label>
            <input 
              type="password" 
              v-model="password" 
              required 
              placeholder="••••••••"
              class="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Phone Number</label>
            <input 
              type="tel" 
              v-model="phone" 
              placeholder="+91 98765 43210"
              class="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500"
            />
          </div>
        </div>

        <div class="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
          <div class="text-[11px] font-bold text-slate-600 uppercase tracking-wider">
            Organization Details
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Organization / Entity Name</label>
            <input 
              type="text" 
              v-model="orgName" 
              required 
              :placeholder="role === 'provider' ? 'e.g. Central Canteen, Royal Bakers' : 'e.g. Hope Community Shelter'"
              class="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-bold text-slate-700 mb-1">Organization Type</label>
              <select 
                v-model="orgType" 
                class="w-full px-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500"
              >
                <template v-if="role === 'provider'">
                  <option value="restaurant">Restaurant</option>
                  <option value="canteen">College / Corporate Canteen</option>
                  <option value="bakery">Bakery / Confectionery</option>
                  <option value="caterer">Event Caterer</option>
                  <option value="hostel">Hostel Mess</option>
                  <option value="grocery">Grocery Store</option>
                </template>
                <template v-else>
                  <option value="ngo">Registered NGO</option>
                  <option value="shelter">Night Shelter / Orphanage</option>
                  <option value="community">Community Kitchen</option>
                  <option value="volunteer">Volunteer Network</option>
                </template>
              </select>
            </div>

            <div>
              <label class="block text-xs font-bold text-slate-700 mb-1">City</label>
              <input 
                type="text" 
                v-model="city" 
                required 
                placeholder="e.g. Chandigarh"
                class="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Physical Address / Pickup Point</label>
            <input 
              type="text" 
              v-model="address" 
              required 
              placeholder="e.g. Sector 17-C, Near Bus Stand"
              class="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500"
            />
          </div>
        </div>

        <div v-if="error" class="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl font-medium">
          {{ error }}
        </div>

        <button 
          type="submit" 
          :disabled="loading"
          class="w-full py-3 px-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl shadow-lg shadow-emerald-600/25 transition-all disabled:opacity-50"
        >
          {{ loading ? 'Creating account...' : 'Complete Registration' }}
        </button>

      </form>

      <div class="text-center text-xs text-slate-500">
        Already registered? 
        <router-link to="/login" class="font-bold text-emerald-600 hover:underline">Sign In</router-link>
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

const role = ref('recipient')
const name = ref('')
const email = ref('')
const password = ref('')
const phone = ref('')
const orgName = ref('')
const orgType = ref('ngo')
const city = ref('Chandigarh')
const address = ref('')
const loading = ref(false)
const error = ref('')

const handleRegister = async () => {
  loading.value = true
  error.value = ''

  const res = await auth.register({
    name: name.value,
    email: email.value,
    password: password.value,
    phone: phone.value,
    role: role.value,
    organization_name: orgName.value,
    organization_type: orgType.value,
    city: city.value,
    address: address.value
  })

  loading.value = false
  if (res.success) {
    router.push('/dashboard')
  } else {
    error.value = res.error
  }
}
</script>
