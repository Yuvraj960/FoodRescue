import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import DashboardView from '../views/DashboardView.vue'
import BrowseFoodView from '../views/BrowseFoodView.vue'
import FoodDetailView from '../views/FoodDetailView.vue'
import CreateListingView from '../views/CreateListingView.vue'
import MyListingsView from '../views/MyListingsView.vue'
import MyReservationsView from '../views/MyReservationsView.vue'
import PickupManagementView from '../views/PickupManagementView.vue'
import NotificationsView from '../views/NotificationsView.vue'
import ImpactDashboardView from '../views/ImpactDashboardView.vue'
import AdminDashboardView from '../views/AdminDashboardView.vue'

const routes = [
  {
    path: '/',
    redirect: () => {
      const token = localStorage.getItem('foodrescue_token')
      return token ? '/dashboard' : '/browse'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { guestOnly: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { guestOnly: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/browse',
    name: 'BrowseFood',
    component: BrowseFoodView
  },
  {
    path: '/food/:id',
    name: 'FoodDetail',
    component: FoodDetailView
  },
  {
    path: '/create-listing',
    name: 'CreateListing',
    component: CreateListingView,
    meta: { requiresAuth: true, roles: ['provider', 'admin'] }
  },
  {
    path: '/my-listings',
    name: 'MyListings',
    component: MyListingsView,
    meta: { requiresAuth: true, roles: ['provider', 'admin'] }
  },
  {
    path: '/my-reservations',
    name: 'MyReservations',
    component: MyReservationsView,
    meta: { requiresAuth: true, roles: ['recipient', 'admin'] }
  },
  {
    path: '/pickup',
    name: 'PickupManagement',
    component: PickupManagementView,
    meta: { requiresAuth: true }
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: NotificationsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/impact',
    name: 'Impact',
    component: ImpactDashboardView
  },
  {
    path: '/admin',
    name: 'Admin',
    component: AdminDashboardView,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

// Navigation Guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('foodrescue_token')
  const user = JSON.parse(localStorage.getItem('foodrescue_user') || 'null')

  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }

  if (to.meta.guestOnly && token) {
    return next('/dashboard')
  }

  if (to.meta.roles && user) {
    if (!to.meta.roles.includes(user.role) && user.role !== 'admin') {
      return next('/dashboard')
    }
  }

  next()
})

export default router
