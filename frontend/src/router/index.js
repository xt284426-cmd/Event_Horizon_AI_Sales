import { createRouter, createWebHistory } from 'vue-router'

import AdminLayout from '../layouts/AdminLayout.vue'
import CustomerDetail from '../pages/CustomerDetail.vue'
import Customers from '../pages/Customers.vue'
import SalesAnalysis from '../pages/SalesAnalysis.vue'

const routes = [
  {
    path: '/',
    component: AdminLayout,
    redirect: '/customers',
    children: [
      { path: 'customers', name: 'customers', component: Customers, meta: { title: '客户管理' } },
      { path: 'customers/:id', name: 'customer-detail', component: CustomerDetail, meta: { title: '客户详情' } },
      { path: 'sales-analysis', name: 'sales-analysis', component: SalesAnalysis, meta: { title: '销售分析' } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach((to) => {
  document.title = `${to.meta.title || '管理后台'} · Event Horizon`
})

export default router
