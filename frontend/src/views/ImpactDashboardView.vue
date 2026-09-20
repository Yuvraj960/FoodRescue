<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    
    <!-- Hero Banner -->
    <div class="bg-gradient-to-br from-slate-900 via-emerald-950 to-slate-900 rounded-3xl p-8 text-white shadow-xl mb-8 relative overflow-hidden">
      <div class="relative z-10 max-w-2xl">
        <div class="inline-flex items-center space-x-1.5 bg-emerald-500/20 text-emerald-300 text-xs font-bold px-3 py-1 rounded-full mb-3 border border-emerald-500/30">
          <span>🌍</span>
          <span>ENVIRONMENTAL & SOCIAL IMPACT REPORT</span>
        </div>
        <h1 class="text-3xl sm:text-5xl font-black tracking-tight leading-tight">
          Food Waste Prevention in Numbers
        </h1>
        <p class="text-xs sm:text-sm text-slate-300 mt-2 leading-relaxed">
          Every rescued meal prevents greenhouse gases and directly nourishes communities. Tracking food redistributed across restaurants, caterers, and shelters.
        </p>
      </div>
      <div class="absolute -right-10 -bottom-10 text-[180px] opacity-5 select-none">
        ♻️
      </div>
    </div>

    <!-- 4 High-Impact Counters -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8">
      
      <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex flex-col justify-between">
        <div>
          <span class="text-xs font-bold uppercase tracking-wider text-slate-400">🍱 Total Meals Rescued</span>
          <div class="text-3xl sm:text-4xl font-black text-emerald-600 tracking-tight mt-1">
            {{ formatNumber(summary.meals_rescued || 0) }}
          </div>
        </div>
        <p class="text-[11px] text-slate-400 mt-3 pt-3 border-t border-slate-100">
          Portions redistributed before expiry
        </p>
      </div>

      <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex flex-col justify-between">
        <div>
          <span class="text-xs font-bold uppercase tracking-wider text-slate-400">🌱 Carbon Avoided (CO₂e)</span>
          <div class="text-3xl sm:text-4xl font-black text-teal-600 tracking-tight mt-1">
            {{ formatNumber(summary.carbon_saved_kg || 0) }} <span class="text-sm font-semibold text-slate-400">kg</span>
          </div>
        </div>
        <p class="text-[11px] text-slate-400 mt-3 pt-3 border-t border-slate-100">
          Calculated at 2.5 kg CO₂e saved per portion
        </p>
      </div>

      <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex flex-col justify-between">
        <div>
          <span class="text-xs font-bold uppercase tracking-wider text-slate-400">🏪 Active Food Providers</span>
          <div class="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight mt-1">
            {{ formatNumber(summary.active_providers || 0) }}
          </div>
        </div>
        <p class="text-[11px] text-slate-400 mt-3 pt-3 border-t border-slate-100">
          Restaurants, bakeries & campus canteens
        </p>
      </div>

      <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex flex-col justify-between">
        <div>
          <span class="text-xs font-bold uppercase tracking-wider text-slate-400">🤝 Participating NGOs</span>
          <div class="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight mt-1">
            {{ formatNumber(summary.participating_orgs || 0) }}
          </div>
        </div>
        <p class="text-[11px] text-slate-400 mt-3 pt-3 border-t border-slate-100">
          Shelters & verified relief foodbanks
        </p>
      </div>

    </div>

    <!-- Charts Section (Monthly Rescues Bar Chart + Category Donut Chart) -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      
      <!-- Left 2 Cols: Monthly Rescued Meals (Bar Chart) -->
      <div class="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-sm font-bold uppercase tracking-wider text-slate-700">📈 Food Rescued Monthly (Portions)</h3>
            <p class="text-xs text-slate-400 mt-0.5">Surplus portions successfully collected and distributed</p>
          </div>
        </div>

        <div class="h-72 flex items-center justify-center">
          <Bar v-if="barChartData.labels.length" :data="barChartData" :options="barOptions" />
          <div v-else class="text-xs text-slate-400">Loading chart data...</div>
        </div>
      </div>

      <!-- Right 1 Col: Category Breakdown (Doughnut Chart) -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <div>
          <h3 class="text-sm font-bold uppercase tracking-wider text-slate-700">🍩 Breakdown by Food Category</h3>
          <p class="text-xs text-slate-400 mt-0.5">Distribution across dietary types</p>
        </div>

        <div class="h-72 flex items-center justify-center mt-2">
          <Doughnut v-if="doughnutChartData.labels.length" :data="doughnutChartData" :options="doughnutOptions" />
          <div v-else class="text-xs text-slate-400">Loading breakdown...</div>
        </div>
      </div>

    </div>

    <!-- Impact Methodology Explainer Box -->
    <div class="bg-emerald-50/70 border border-emerald-200 rounded-2xl p-6">
      <h4 class="text-xs font-bold uppercase tracking-wider text-emerald-900 mb-1 flex items-center space-x-1.5">
        <span>🔬</span>
        <span>Impact Calculation Methodology</span>
      </h4>
      <p class="text-xs text-emerald-800 leading-relaxed max-w-3xl">
        According to international food waste and agricultural lifecycle analyses (FAO / EPA benchmarks), rescuing 1 portion of prepared surplus food prevents approximately <strong>2.5 kg of CO₂ equivalent emissions</strong> that would otherwise occur via decomposition in landfills and wasted supply chain resources.
      </p>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement
} from 'chart.js'
import { Bar, Doughnut } from 'vue-chartjs'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement)

const summary = ref({})
const barChartData = ref({ labels: [], datasets: [] })
const doughnutChartData = ref({ labels: [], datasets: [] })

const barOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: { color: '#f1f5f9' },
      ticks: { font: { size: 10 } }
    },
    x: {
      grid: { display: false },
      ticks: { font: { size: 10 } }
    }
  }
}

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom', labels: { font: { size: 10 }, boxWidth: 12 } }
  }
}

onMounted(async () => {
  try {
    const [sumRes, monthRes, catRes] = await Promise.all([
      api.get('/analytics/impact'),
      api.get('/analytics/monthly'),
      api.get('/analytics/categories')
    ])

    summary.value = sumRes.data

    // Monthly Bar Chart
    const monthlyList = monthRes.data || []
    barChartData.value = {
      labels: monthlyList.map(m => m.label),
      datasets: [
        {
          label: 'Meals Rescued',
          backgroundColor: '#10b981',
          borderRadius: 8,
          data: monthlyList.map(m => m.meals)
        }
      ]
    }

    // Category Doughnut Chart
    const categoryList = (catRes.data || []).filter(c => c.quantity > 0)
    doughnutChartData.value = {
      labels: categoryList.map(c => c.category),
      datasets: [
        {
          backgroundColor: ['#10b981', '#f59e0b', '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'],
          data: categoryList.map(c => c.quantity)
        }
      ]
    }

  } catch (err) {
    console.error('Failed to load impact analytics', err)
  }
})

const formatNumber = (num) => {
  return new Intl.NumberFormat().format(num)
}
</script>
