import { createRouter, createWebHistory } from 'vue-router'
import MainView from '../views/MainView.vue'
import AdminView from '../views/AdminView.vue'
import ReportView from '../views/ReportView.vue'
import LoginView from '../views/LoginView.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: MainView,
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/report',
      name: 'report',
      component: ReportView,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('bt_token')
  const user = localStorage.getItem('bt_user') ? JSON.parse(localStorage.getItem('bt_user')!) : null

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.requiresAdmin && user?.role !== 'admin') {
    next('/')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router
