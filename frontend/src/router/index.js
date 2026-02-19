import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { title: 'Dashboard', icon: 'pi pi-home' },
  },
  {
    path: '/models',
    name: 'Models',
    component: () => import('../views/ModelsView.vue'),
    meta: { title: 'Mevcut Skorkartlar', icon: 'pi pi-list' },
  },
  {
    path: '/models/:id',
    name: 'ModelDetail',
    component: () => import('../views/ModelDetailView.vue'),
    meta: { title: 'Model Detay' },
  },
  {
    path: '/development',
    name: 'Development',
    component: () => import('../views/DevelopmentView.vue'),
    meta: { title: 'Geliştirilen Skorkartlar', icon: 'pi pi-cog' },
  },
  {
    path: '/development/:id',
    name: 'ProjectDetail',
    component: () => import('../views/ProjectDetailView.vue'),
    meta: { title: 'Proje Detay' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  document.title = `${to.meta.title || 'MT Dashboard'} | MT Dashboard`
})

export default router
