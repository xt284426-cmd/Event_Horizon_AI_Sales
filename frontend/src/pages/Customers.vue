<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { getCustomers } from '../api/customer'

const router = useRouter()
const customers = ref([])
const loading = ref(false)

function levelType(level) {
  return { 高: 'danger', 高意向: 'danger', 中等: 'warning', 中: 'warning', 低: 'info' }[level] || 'info'
}

function formatTime(value) {
  return value ? new Date(value).toLocaleString('zh-CN', { hour12: false }) : '尚未分析'
}

async function loadCustomers() {
  loading.value = true
  try {
    customers.value = await getCustomers({ offset: 0, limit: 100 })
  } finally {
    loading.value = false
  }
}

onMounted(loadCustomers)
</script>

<template>
  <section>
    <div class="page-heading">
      <div>
        <p class="eyebrow">CUSTOMER INTELLIGENCE</p>
        <h1>客户管理</h1>
        <p>查看客户价值、最新评分与 AI 分析进度。</p>
      </div>
      <el-button type="primary" plain @click="loadCustomers">刷新数据</el-button>
    </div>

    <div class="summary-grid">
      <div class="summary-card">
        <span>客户总数</span>
        <strong>{{ customers.length }}</strong>
      </div>
      <div class="summary-card accent">
        <span>已完成 AI 分析</span>
        <strong>{{ customers.filter((item) => item.latest_ai_analysis_time).length }}</strong>
      </div>
      <div class="summary-card">
        <span>高意向客户</span>
        <strong>{{ customers.filter((item) => ['高', '高意向'].includes(item.level)).length }}</strong>
      </div>
    </div>

    <el-card shadow="never" class="data-card">
      <el-table v-loading="loading" :data="customers" stripe empty-text="暂无客户数据">
        <el-table-column prop="id" label="ID" width="88" />
        <el-table-column prop="name" label="客户姓名" min-width="180" />
        <el-table-column label="意向等级" width="130">
          <template #default="scope">
            <el-tag :type="levelType(scope.row.level)" effect="light">
              {{ scope.row.level || '待评估' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最新评分" width="130">
          <template #default="scope">{{ scope.row.latest_score ?? '—' }}</template>
        </el-table-column>
        <el-table-column label="最近 AI 分析" min-width="210">
          <template #default="scope">{{ formatTime(scope.row.latest_ai_analysis_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="110" fixed="right">
          <template #default="scope">
            <el-button link type="primary" @click="router.push(`/customers/${scope.row.id}`)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </section>
</template>
