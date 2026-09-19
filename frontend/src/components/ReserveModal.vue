<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
    <div class="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-100 transform transition-all">
      
      <!-- Modal Header -->
      <div class="flex items-start justify-between pb-4 border-b border-slate-100">
        <div>
          <span class="text-xs font-bold text-emerald-600 uppercase tracking-wider">Surplus Food Reservation</span>
          <h3 class="text-xl font-extrabold text-slate-800 leading-snug mt-0.5">{{ listing.title }}</h3>
          <p class="text-xs text-slate-500 mt-0.5">Offered by <span class="font-semibold text-slate-700">{{ listing.organization_name || listing.provider_name }}</span></p>
        </div>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-600 text-xl font-bold p-1">&times;</button>
      </div>

      <!-- Prominent Dietary & Safety Notice (Requested by User) -->
      <div class="mt-4 p-3.5 rounded-xl bg-slate-50 border border-slate-200">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-bold text-slate-600 uppercase">Food Classification:</span>
          <DietaryBadge :dietary="listing.dietary_type" size="md" />
        </div>

        <div v-if="listing.allergen_info" class="flex items-start space-x-2 mt-2 pt-2 border-t border-slate-200/80 text-xs text-amber-800 bg-amber-50/70 p-2 rounded-lg">
          <span class="text-base leading-none">⚠️</span>
          <div>
            <span class="font-bold">Allergen Notice:</span> {{ listing.allergen_info }}
          </div>
        </div>

        <div class="text-xs text-slate-500 mt-2 flex items-center justify-between">
          <span>📦 Total Remaining: <strong>{{ listing.remaining_quantity }} {{ listing.unit }}</strong></span>
          <span>📍 {{ listing.location }}, {{ listing.city }}</span>
        </div>
      </div>

      <!-- Reservation Form -->
      <form @submit.prevent="handleReserve" class="mt-4 space-y-4">
        
        <!-- Quantity Input -->
        <div>
          <div class="flex justify-between items-center mb-1.5">
            <label class="text-xs font-bold text-slate-700">Portions to Reserve</label>
            <span class="text-xs font-semibold text-emerald-600">Max available: {{ listing.remaining_quantity }} {{ listing.unit }}</span>
          </div>
          <div class="flex items-center space-x-3">
            <input 
              type="number" 
              v-model.number="quantity" 
              :min="1" 
              :max="listing.remaining_quantity" 
              required
              class="w-full px-4 py-2.5 rounded-xl border border-slate-300 font-bold text-slate-800 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
            />
            <button 
              type="button" 
              @click="quantity = listing.remaining_quantity"
              class="text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-2.5 rounded-xl transition-colors whitespace-nowrap"
            >
              Take All
            </button>
          </div>
        </div>

        <!-- Pickup Window Info -->
        <div class="p-3 bg-emerald-50/60 rounded-xl border border-emerald-100 text-xs text-emerald-800">
          <div class="font-bold mb-1">⏰ Scheduled Pickup Window</div>
          <div>From: <span class="font-semibold">{{ formatTime(listing.pickup_start) }}</span></div>
          <div>Until: <span class="font-semibold">{{ formatTime(listing.pickup_end) }}</span></div>
        </div>

        <!-- Notes / Special Instructions -->
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Pickup Notes / Vehicle Details</label>
          <textarea 
            v-model="notes" 
            rows="2" 
            placeholder="e.g., Arriving with refrigerated van, estimated 2:00 PM arrival..."
            class="w-full px-3.5 py-2 text-xs rounded-xl border border-slate-300 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
          ></textarea>
        </div>

        <!-- Mandatory NGO Dietary Verification Checkbox -->
        <div class="flex items-start space-x-2.5 p-3 rounded-xl bg-slate-100 border border-slate-200">
          <input 
            type="checkbox" 
            id="dietary-confirm" 
            v-model="dietaryConfirmed" 
            required 
            class="mt-0.5 rounded text-emerald-600 focus:ring-emerald-500 h-4 w-4"
          />
          <label for="dietary-confirm" class="text-xs text-slate-700 leading-snug cursor-pointer">
            I confirm that our organization has verified the dietary categorization (<strong class="text-slate-900">{{ listing.dietary_type }}</strong>) and allergen details for safe distribution.
          </label>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl font-medium">
          {{ error }}
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center space-x-3 pt-2">
          <button 
            type="button" 
            @click="$emit('close')" 
            class="flex-1 px-4 py-2.5 text-xs font-bold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-xl transition-colors"
          >
            Cancel
          </button>
          <button 
            type="submit" 
            :disabled="loading || !dietaryConfirmed || quantity <= 0 || quantity > listing.remaining_quantity"
            class="flex-1 px-4 py-2.5 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl shadow-md shadow-emerald-600/25 transition-all"
          >
            {{ loading ? 'Submitting...' : `Confirm (${quantity} ${listing.unit})` }}
          </button>
        </div>

      </form>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import DietaryBadge from './DietaryBadge.vue'
import { useFoodStore } from '../stores/food'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  listing: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'reserved'])
const foodStore = useFoodStore()

const quantity = ref(Math.min(10, props.listing.remaining_quantity))
const notes = ref('')
const dietaryConfirmed = ref(false)
const loading = ref(false)
const error = ref('')

const formatTime = (isoString) => {
  if (!isoString) return 'Not specified'
  const d = new Date(isoString)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', month: 'short', day: 'numeric' })
}

const handleReserve = async () => {
  if (!dietaryConfirmed.value) {
    error.value = 'Please confirm the dietary check before proceeding.'
    return
  }

  loading.value = true
  error.value = ''

  const res = await foodStore.reserveFood(props.listing.id, quantity.value, notes.value)
  loading.value = false

  if (res.success) {
    emit('reserved', res.data)
    emit('close')
  } else {
    error.value = res.error
  }
}
</script>
