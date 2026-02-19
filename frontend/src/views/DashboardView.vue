<script setup>
import { ref, onMounted } from 'vue'
import { Bar, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement,
  ArcElement, Title, Tooltip, Legend
} from 'chart.js'
import { dashboardApi } from '../api'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend)

const summary = ref({ models: {}, development: {} })
const giniData = ref([])
const modelTypesData = ref([])
const progressData = ref([])
const loading = ref(true)

const giniChartData = ref({ labels: [], datasets: [] })
const typeChartData = ref({ labels: [], datasets: [] })

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom' } },
}

onMounted(async () => {
  try {
    const [summaryRes, giniRes, typesRes, progressRes] = await Promise.all([
      dashboardApi.getSummary(),
      dashboardApi.getGiniOverview(),
      dashboardApi.getModelTypes(),
      dashboardApi.getDevelopmentProgress(),
    ])

    summary.value = summaryRes.data
    giniData.value = giniRes.data
    modelTypesData.value = typesRes.data
    progressData.value = progressRes.data

    // Gini bar chart
    giniChartData.value = {
      labels: giniData.value.map(m => m.model_name),
      datasets: [
        {
          label: 'Geliştirme Gini',
          data: giniData.value.map(m => m.gini_development),
          backgroundColor: 'rgba(59, 130, 246, 0.7)',
        },
        {
          label: 'Validasyon Gini',
          data: giniData.value.map(m => m.gini_validation),
          backgroundColor: 'rgba(16, 185, 129, 0.7)',
        },
        {
          label: 'Güncel Gini',
          data: giniData.value.map(m => m.gini_current),
          backgroundColor: 'rgba(245, 158, 11, 0.7)',
        },
      ],
    }

    // Model types doughnut
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
    typeChartData.value = {
      labels: modelTypesData.value.map(t => t.type),
      datasets: [{
        data: modelTypesData.value.map(t => t.count),
        backgroundColor: colors.slice(0, modelTypesData.value.length),
      }],
    }
  } catch (err) {
    console.error('Dashboard load error:', err)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <div class="page-header">
      <h2>Dashboard</h2>
    </div>
    <div class="page-body">
      <!-- Summary Stats -->
      <div class="stats-grid">
        <div class="stat-card info">
          <div class="stat-label">Toplam Model</div>
          <div class="stat-value">{{ summary.models?.total || 0 }}</div>
          <div class="stat-detail">{{ summary.models?.active || 0 }} aktif</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">İnceleme Bekleyen</div>
          <div class="stat-value">{{ summary.models?.under_review || 0 }}</div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">Aktif Projeler</div>
          <div class="stat-value">{{ summary.development?.active_projects || 0 }}</div>
          <div class="stat-detail">{{ summary.development?.completed_projects || 0 }} tamamlanan</div>
        </div>
        <div class="stat-card danger">
          <div class="stat-label">Geciken Aşamalar</div>
          <div class="stat-value">{{ summary.development?.overdue_stages || 0 }}</div>
        </div>
      </div>

      <!-- Charts -->
      <div class="charts-grid">
        <div class="card">
          <div class="card-header">
            <h3>Gini Değerleri Karşılaştırması</h3>
          </div>
          <div class="card-body" style="height: 300px;">
            <Bar
              v-if="giniData.length > 0"
              :data="giniChartData"
              :options="chartOptions"
            />
            <div v-else class="empty-state">
              <i class="pi pi-chart-bar"></i>
              <p>Henüz model verisi bulunmuyor</p>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h3>Model Türü Dağılımı</h3>
          </div>
          <div class="card-body" style="height: 300px;">
            <Doughnut
              v-if="modelTypesData.length > 0"
              :data="typeChartData"
              :options="chartOptions"
            />
            <div v-else class="empty-state">
              <i class="pi pi-chart-pie"></i>
              <p>Henüz model verisi bulunmuyor</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Development Progress -->
      <div class="card">
        <div class="card-header">
          <h3>Geliştirme İlerleme Durumu</h3>
        </div>
        <div class="card-body">
          <div v-if="progressData.length > 0">
            <div
              v-for="project in progressData"
              :key="project.project_name"
              style="margin-bottom: 16px;"
            >
              <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="font-weight: 600; font-size: 0.85rem;">{{ project.project_name }}</span>
                <span style="font-size: 0.8rem; color: #64748b;">
                  {{ project.owner }} · {{ project.progress }}%
                </span>
              </div>
              <div class="progress-bar-container">
                <div class="progress-bar-fill" :style="{ width: project.progress + '%' }"></div>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <i class="pi pi-briefcase"></i>
            <p>Henüz aktif geliştirme projesi bulunmuyor</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
