<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { getCustomerDetail } from '../api/customer'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const detail = ref(null)

const customer = computed(() => detail.value?.customer || {})
const profileEntries = computed(() => Object.entries(detail.value?.profile || {}))
const analysis = computed(() => detail.value?.latest_ai_analysis)
const followSuggestion = computed(() => detail.value?.follow_suggestion || {})

function displayValue(value) {
  if (Array.isArray(value)) return value.join('、') || '—'
  if (value && typeof value === 'object') return JSON.stringify(value)
  return value ?? '—'
}

async function loadDetail() {
  loading.value = true
  try {
    detail.value = await getCustomerDetail(route.params.id)
  } finally {
    loading.value = false
  }
}

onMounted(loadDetail)
</script>

<template>
  <section v-loading="loading">
    <div class="back-row">
      <el-button link @click="router.push('/customers')">← 返回客户列表</el-button>
    </div>
    <div class="page-heading detail-heading">
      <div>
        <p class="eyebrow">CUSTOMER PROFILE</p>
        <h1>{{ customer.name || '客户详情' }}</h1>
        <p>客户信息、画像洞察与下一步跟进建议。</p>
      </div>
      <el-tag type="success" effect="dark">{{ customer.status || '未知状态' }}</el-tag>
    </div>

    <div v-if="detail" class="detail-grid">
      <el-card shadow="never" class="info-card">
        <template #header><strong>基础信息</strong></template>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="客户 ID">{{ customer.id }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ customer.phone || '—' }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ customer.email || '—' }}</el-descriptions-item>
          <el-descriptions-item label="来源渠道">{{ customer.source || '—' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card shadow="never" class="info-card profile-card">
        <template #header><strong>客户画像</strong></template>
        <div v-if="profileEntries.length" class="profile-list">
          <div v-for="([key, value]) in profileEntries" :key="key" class="profile-item">
            <span>{{ key }}</span>
            <strong>{{ displayValue(value) }}</strong>
          </div>
        </div>
        <el-empty v-else description="暂无客户画像" :image-size="72" />
      </el-card>

      <el-card shadow="never" class="info-card analysis-card">
        <template #header>
          <div class="card-title-row">
            <strong>最近 AI 分析</strong>
            <el-tag v-if="analysis" type="success">{{ analysis.status }}</el-tag>
          </div>
        </template>
        <template v-if="analysis">
          <div class="analysis-meta">
            <span>模型：{{ analysis.model_name || 'simulation' }}</span>
            <span>置信度：{{ analysis.confidence ?? '—' }}</span>
          </div>
          <pre class="result-preview">{{ JSON.stringify(analysis.result, null, 2) }}</pre>
        </template>
        <el-empty v-else description="尚未生成 AI 分析" :image-size="72" />
      </el-card>

      <el-card shadow="never" class="info-card follow-card">
        <template #header><strong>跟进建议</strong></template>
        <div v-if="Object.keys(followSuggestion).length" class="suggestion-content">
          <div>
            <span class="suggestion-label">下一步动作</span>
            <p>{{ displayValue(followSuggestion['下一步动作'] || followSuggestion.next_actions) }}</p>
          </div>
          <div>
            <span class="suggestion-label">推荐话术</span>
            <blockquote>{{ followSuggestion['推荐话术'] || followSuggestion.recommended_script || '—' }}</blockquote>
          </div>
        </div>
        <el-empty v-else description="暂无跟进建议" :image-size="72" />
      </el-card>
    </div>
  </section>
</template>
