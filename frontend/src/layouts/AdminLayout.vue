<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => {
  if (route.path.startsWith('/customers')) return '/customers'
  return route.path
})

function navigate(path) {
  router.push(path)
}
</script>

<template>
  <el-container class="admin-shell">
    <el-header class="topbar">
      <div class="brand-block">
        <div class="brand-mark">EH</div>
        <div>
          <div class="brand-name">Event Horizon</div>
          <div class="brand-caption">AI SALES INTELLIGENCE</div>
        </div>
      </div>
      <div class="topbar-status">
        <span class="status-dot"></span>
        AI 分析服务运行中
      </div>
    </el-header>

    <el-container class="workspace">
      <el-aside width="232px" class="sidebar">
        <div class="menu-label">工作台</div>
        <el-menu :default-active="activeMenu" class="side-menu" @select="navigate">
          <el-menu-item index="/customers">
            <span class="menu-icon">客</span>
            <span>客户管理</span>
          </el-menu-item>
          <el-menu-item index="/sales-analysis">
            <span class="menu-icon">析</span>
            <span>销售分析</span>
          </el-menu-item>
        </el-menu>
        <div class="sidebar-note">
          <span>Phase 5</span>
          <strong>管理后台基础版</strong>
        </div>
      </el-aside>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>
