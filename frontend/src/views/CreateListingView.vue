<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    
    <div class="mb-6">
      <h1 class="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">Post Surplus Food</h1>
      <p class="text-xs text-slate-500 mt-1">List edible surplus food for verified NGOs, shelters, and community volunteers to rescue.</p>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-6 bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm">
      
      <!-- Basic Details -->
      <div class="space-y-4">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Food Item Title *</label>
          <input 
            type="text" 
            v-model="form.title" 
            required 
            placeholder="e.g., Vegetable Biryani & Raita, Sourdough Bread Loaves" 
            class="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500"
          />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Category *</label>
            <select 
              v-model="form.category_id" 
              required
              class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500"
            >
              <option value="" disabled>Select category</option>
              <option v-for="cat in foodStore.categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block text-xs font-bold text-slate-700 mb-1">Quantity *</label>
              <input 
                type="number" 
                v-model.number="form.quantity" 
                min="1" 
                required 
                placeholder="40" 
                class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-700 mb-1">Unit</label>
              <select 
                v-model="form.unit" 
                class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500"
              >
                <option value="portions">portions</option>
                <option value="meals">meals</option>
                <option value="items">items</option>
                <option value="kg">kg</option>
                <option value="boxes">boxes</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Prominent Dietary Classification Selector (Requested by User) -->
        <div class="p-4 bg-slate-50 border border-slate-200 rounded-xl">
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
            🥗 Dietary Classification (Crucial for Recipient NGOs) *
          </label>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <button 
              type="button"
              v-for="diet in dietaryOptions"
              :key="diet.value"
              @click="form.dietary_type = diet.value"
              :class="[
                'p-2.5 text-xs font-bold rounded-xl border text-center transition-all flex flex-col items-center justify-center space-y-1',
                form.dietary_type === diet.value 
                  ? 'bg-emerald-600 text-white border-emerald-600 shadow-md shadow-emerald-600/20' 
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
              ]"
            >
              <span class="text-base">{{ diet.icon }}</span>
              <span>{{ diet.label }}</span>
            </button>
          </div>

          <div class="mt-3">
            <label class="block text-xs font-bold text-slate-700 mb-1">Allergen Information & Ingredients</label>
            <input 
              type="text" 
              v-model="form.allergen_info" 
              placeholder="e.g. Contains dairy (ghee), gluten, nut-free, vegan..." 
              class="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500"
            />
          </div>
        </div>

        <!-- Expiration and Timing -->
        <div class="p-4 bg-amber-50/50 border border-amber-200/80 rounded-xl space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold uppercase tracking-wider text-amber-900">⏰ Expiry & Timings</span>
            <div class="flex space-x-1.5">
              <button 
                type="button" 
                @click="setQuickExpiry(2)"
                class="px-2 py-1 bg-white hover:bg-amber-100 text-amber-900 border border-amber-200 text-[10px] font-bold rounded-md"
              >
                +2 Hours
              </button>
              <button 
                type="button" 
                @click="setQuickExpiry(4)"
                class="px-2 py-1 bg-white hover:bg-amber-100 text-amber-900 border border-amber-200 text-[10px] font-bold rounded-md"
              >
                +4 Hours
              </button>
              <button 
                type="button" 
                @click="setQuickExpiry(6)"
                class="px-2 py-1 bg-white hover:bg-amber-100 text-amber-900 border border-amber-200 text-[10px] font-bold rounded-md"
              >
                +6 Hours
              </button>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div>
              <label class="block font-bold text-slate-700 mb-1">Expiry Date & Time *</label>
              <input 
                type="datetime-local" 
                v-model="form.expiry_time" 
                required 
                class="w-full px-3 py-2 rounded-xl border border-slate-300 focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label class="block font-bold text-slate-700 mb-1">Pickup Window Start</label>
              <input 
                type="datetime-local" 
                v-model="form.pickup_start" 
                class="w-full px-3 py-2 rounded-xl border border-slate-300 focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label class="block font-bold text-slate-700 mb-1">Pickup Window End</label>
              <input 
                type="datetime-local" 
                v-model="form.pickup_end" 
                class="w-full px-3 py-2 rounded-xl border border-slate-300 focus:ring-2 focus:ring-emerald-500"
              />
            </div>
          </div>
        </div>

        <!-- Location -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div class="sm:col-span-2">
            <label class="block text-xs font-bold text-slate-700 mb-1">Pickup Location / Counter Address *</label>
            <input 
              type="text" 
              v-model="form.location" 
              required 
              placeholder="e.g. Canteen Gate 2, Kitchen Counter..." 
              class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">City *</label>
            <input 
              type="text" 
              v-model="form.city" 
              required 
              placeholder="Chandigarh" 
              class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500"
            />
          </div>
        </div>

        <!-- Description -->
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Description & Packing Details</label>
          <textarea 
            v-model="form.description" 
            rows="3" 
            placeholder="Describe preparation, containers (e.g. packed in clean thermoware or recipient should bring containers)..."
            class="w-full px-3.5 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-emerald-500"
          ></textarea>
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
        {{ loading ? 'Publishing Listing...' : 'Publish Surplus Food Listing' }}
      </button>

    </form>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFoodStore } from '../stores/food'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const foodStore = useFoodStore()
const auth = useAuthStore()

const loading = ref(false)
const error = ref('')

const dietaryOptions = [
  { label: 'Vegetarian', value: 'VEGETARIAN', icon: '🟢' },
  { label: 'Non-Veg', value: 'NON_VEGETARIAN', icon: '🔴' },
  { label: 'Pure Vegan', value: 'VEGAN', icon: '🌱' },
  { label: 'Bakery', value: 'BAKERY', icon: '🍞' }
]

// Default to 3 hours ahead
const getIsoForHours = (h) => {
  const d = new Date(Date.now() + h * 3600 * 1000)
  return d.toISOString().slice(0, 16)
}

const form = reactive({
  title: '',
  category_id: '',
  quantity: 25,
  unit: 'portions',
  dietary_type: 'VEGETARIAN',
  allergen_info: '',
  location: auth.user?.address || 'Kitchen Pickup Counter',
  city: auth.user?.city || 'Chandigarh',
  expiry_time: getIsoForHours(4),
  pickup_start: getIsoForHours(0.5),
  pickup_end: getIsoForHours(3.5),
  description: ''
})

onMounted(async () => {
  await foodStore.fetchCategories()
  if (foodStore.categories.length > 0) {
    form.category_id = foodStore.categories[0].id
  }
})

const setQuickExpiry = (hours) => {
  form.expiry_time = getIsoForHours(hours)
  form.pickup_end = getIsoForHours(hours - 0.5)
}

const handleSubmit = async () => {
  loading.value = true
  error.value = ''

  const res = await foodStore.createListing(form)
  loading.value = false

  if (res.success) {
    router.push('/my-listings')
  } else {
    error.value = res.error
  }
}
</script>
