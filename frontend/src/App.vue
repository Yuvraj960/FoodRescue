<template>
  <div class="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans">
    <Navbar />
    
    <main class="flex-1">
      <router-view />
    </main>

    <footer class="bg-white border-t border-slate-200 py-6 mt-12 text-xs text-slate-500">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div class="flex items-center space-x-2">
          <span class="text-base">🥗</span>
          <span class="font-bold text-slate-800">FoodRescue</span>
          <span>— Surplus Food Redistribution Platform</span>
        </div>
        <div class="flex items-center space-x-3 text-[11px]">
          <span class="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-semibold">UN SDG 12.3 • Halve Food Waste</span>
          <span>•</span>
          <span>Celery & Redis Expiry Engine</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
</script>
