<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement,
  Title, Tooltip, Legend
} from 'chart.js'
import { dashboardApi } from '../api'

const router = useRouter()

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const summary = ref({ models: {}, development: {} })
const giniData = ref({ basvuru: [], davranis: [] })
const progressData = ref([])
const giniAlerts = ref([])
const initialLoading = ref(true)

const basvuruChartData = computed(() => {
  const data = giniData.value.basvuru || []
  if (!data.length) return null
  return {
    labels: data.map(m => m.model_name),
    datasets: [
      {
        label: 'Geliştirme Gini',
        data: data.map(m => m.gini_development != null ? +(m.gini_development * 100).toFixed(1) : null),
        backgroundColor: 'rgba(59, 130, 246, 0.7)',
      },
      {
        label: 'Güncel Gini',
        data: data.map(m => m.gini_current != null ? +(m.gini_current * 100).toFixed(1) : null),
        backgroundColor: 'rgba(245, 158, 11, 0.7)',
      },
    ],
  }
})

const davranisChartData = computed(() => {
  const data = giniData.value.davranis || []
  if (!data.length) return null
  return {
    labels: data.map(m => m.model_name),
    datasets: [
      {
        label: 'Geliştirme Gini',
        data: data.map(m => m.gini_development != null ? +(m.gini_development * 100).toFixed(1) : null),
        backgroundColor: 'rgba(59, 130, 246, 0.7)',
      },
      {
        label: 'Güncel Gini',
        data: data.map(m => m.gini_current != null ? +(m.gini_current * 100).toFixed(1) : null),
        backgroundColor: 'rgba(245, 158, 11, 0.7)',
      },
    ],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom' } },
  scales: {
    y: {
      min: 0,
      ticks: { callback: v => v + '%' },
    },
  },
}

const giniAlertList = computed(() => giniAlerts.value.filter(a => a.gini_alert))
const psiAlertList = computed(() => giniAlerts.value.filter(a => a.psi_flag && !a.gini_alert))

onMounted(async () => {
  try {
    const [summaryRes, giniRes, progressRes, alertsRes] = await Promise.all([
      dashboardApi.getSummary(),
      dashboardApi.getGiniOverview(),
      dashboardApi.getDevelopmentProgress(),
      dashboardApi.getGiniAlerts(),
    ])

    summary.value = summaryRes.data
    giniData.value = giniRes.data
    progressData.value = progressRes.data
    giniAlerts.value = alertsRes.data
  } catch (err) {
    console.error('Dashboard load error:', err)
  } finally {
    initialLoading.value = false
  }
})
</script>

<template>
  <div>
    <div class="page-header">
      <h2>Dashboard</h2>
    </div>
    <div class="page-body">

      <!-- ── Özet Kartlar ── -->
      <div style="margin-bottom: 8px; font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; letter-spacing: 0.05em;">
        Mevcut Skorkartlar
      </div>
      <div class="stats-grid" style="margin-bottom: 24px;">
        <div class="stat-card info">
          <div class="stat-label">Toplam Aktif Model</div>
          <div class="stat-value">{{ summary.models?.active || 0 }}</div>
          <div class="stat-detail">
            <span style="color: #3b82f6;">{{ summary.models?.basvuru || 0 }} Başvuru</span>
            &nbsp;·&nbsp;
            <span style="color: #10b981;">{{ summary.models?.davranis || 0 }} Davranış</span>
          </div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">İnceleme Bekleyen</div>
          <div class="stat-value">{{ summary.models?.under_review || 0 }}</div>
        </div>
        <div class="stat-card danger">
          <div class="stat-label">Gini Uyarısı</div>
          <div class="stat-value">{{ giniAlertList.length }}</div>
          <div class="stat-detail" v-if="summary.models?.psi_flag_count">
            {{ summary.models.psi_flag_count }} PSI flag
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-label">PSI Flag</div>
          <div class="stat-value" :style="{ color: summary.models?.psi_flag_count ? '#f59e0b' : '#64748b' }">
            {{ summary.models?.psi_flag_count || 0 }}
          </div>
        </div>
      </div>

      <div style="margin-bottom: 8px; font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; letter-spacing: 0.05em;">
        Geliştirilen Skorkartlar
      </div>
      <div class="stats-grid" style="margin-bottom: 32px;">
        <div class="stat-card success">
          <div class="stat-label">Aktif Projeler</div>
          <div class="stat-value">{{ summary.development?.active_projects || 0 }}</div>
          <div class="stat-detail">
            <span style="color: #3b82f6;">{{ summary.development?.dev_basvuru || 0 }} Başvuru</span>
            &nbsp;·&nbsp;
            <span style="color: #10b981;">{{ summary.development?.dev_davranis || 0 }} Davranış</span>
          </div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">Tamamlanan</div>
          <div class="stat-value">{{ summary.development?.completed_projects || 0 }}</div>
        </div>
        <div class="stat-card danger">
          <div class="stat-label">Geciken Aşamalar</div>
          <div class="stat-value">{{ summary.development?.overdue_stages || 0 }}</div>
        </div>
      </div>

      <!-- ── Alert Mekanizması ── -->
      <div class="card" :style="giniAlertList.length > 0 ? 'border: 1.5px solid #fca5a5; margin-bottom: 24px;' : 'margin-bottom: 24px;'">
        <div class="card-header">
          <div style="display: flex; align-items: center; gap: 8px;">
            <i
              :class="giniAlertList.length > 0 ? 'pi pi-exclamation-triangle' : 'pi pi-check-circle'"
              :style="{ color: giniAlertList.length > 0 ? '#ef4444' : '#10b981', fontSize: '1.1rem' }"
            ></i>
            <h3 style="margin: 0;">Gini Uyarıları</h3>
          </div>
          <span style="font-size: 0.78rem; color: #64748b;">
            Başvuru &lt; 50% · Davranış &lt; 70% · Son 3 ayda ≥5pp ardışık sapma
          </span>
        </div>
        <div class="card-body">
          <div v-if="giniAlertList.length > 0">
            <div
              v-for="alert in giniAlertList"
              :key="alert.model_id"
              class="gini-alert-row"
              @click="router.push(`/models/${alert.model_id}`)"
            >
              <div class="gini-alert-header">
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                  <span class="gini-alert-name">{{ alert.model_name }}</span>
                  <span class="status-badge" :class="alert.status">
                    {{ alert.status === 'active' ? 'Aktif' : 'İnceleniyor' }}
                  </span>
                  <!-- Üstüne çalışma başladı mı? -->
                  <span
                    v-if="alert.alert_work_started"
                    style="background: #dbeafe; color: #1d4ed8; font-size: 0.7rem; padding: 2px 8px; border-radius: 20px; font-weight: 600;"
                  >
                    <i class="pi pi-wrench" style="font-size: 0.65rem;"></i> Çalışma Başladı
                  </span>
                  <!-- Alert sebepleri -->
                  <span
                    v-if="alert.alert_reason.includes('threshold_breach')"
                    style="background: #fee2e2; color: #dc2626; font-size: 0.7rem; padding: 2px 8px; border-radius: 20px;"
                  >
                    Eşik Altı ({{ alert.scorecard_category === 'Başvuru' ? '&lt;50%' : '&lt;70%' }})
                  </span>
                  <span
                    v-if="alert.alert_reason.includes('consecutive_deviation')"
                    style="background: #fff7ed; color: #c2410c; font-size: 0.7rem; padding: 2px 8px; border-radius: 20px;"
                  >
                    Ardışık Sapma
                  </span>
                </div>
                <span
                  v-if="alert.direction"
                  class="gini-alert-direction"
                  :class="alert.direction === 'drop' ? 'drop' : 'rise'"
                >
                  <i :class="alert.direction === 'drop' ? 'pi pi-arrow-down' : 'pi pi-arrow-up'"></i>
                  {{ alert.direction === 'drop' ? 'Düşüş' : 'Artış' }}
                </span>
              </div>
              <div class="gini-alert-body">
                <div class="gini-alert-ref">
                  Geliştirme: <strong>{{ alert.gini_development != null ? (alert.gini_development * 100).toFixed(1) + '%' : '-' }}</strong>
                  &nbsp;·&nbsp;
                  Güncel: <strong :style="{ color: alert.gini_current < alert.gini_threshold ? '#ef4444' : '#374151' }">
                    {{ alert.gini_current != null ? (alert.gini_current * 100).toFixed(1) + '%' : '-' }}
                  </strong>
                  &nbsp;·&nbsp;
                  Eşik: <strong>{{ (alert.gini_threshold * 100).toFixed(0) }}%</strong>
                  &nbsp;·&nbsp; {{ alert.scorecard_category }}
                </div>
                <div v-if="alert.last3_periods.length" class="gini-alert-months">
                  <div
                    v-for="(period, i) in alert.last3_periods"
                    :key="period"
                    class="gini-alert-month"
                  >
                    <span class="gini-month-label">{{ period }}</span>
                    <span class="gini-month-value">{{ (alert.last3_values[i] * 100).toFixed(1) }}%</span>
                    <span class="gini-month-diff" :class="alert.direction">
                      {{ alert.direction === 'drop' ? '-' : '+' }}{{ (Math.abs(alert.last3_diffs[i]) * 100).toFixed(1) }}pp
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="empty-state" style="padding: 24px 0;">
            <i class="pi pi-check-circle" style="color: #10b981;"></i>
            <p style="color: #10b981;">Gini uyarısı yok</p>
          </div>
        </div>
      </div>

      <!-- ── PSI Flag Listesi (bağımsız) ── -->
      <div v-if="psiAlertList.length > 0" class="card" style="border: 1.5px solid #fde68a; margin-bottom: 24px;">
        <div class="card-header">
          <div style="display: flex; align-items: center; gap: 8px;">
            <i class="pi pi-flag" style="color: #f59e0b; font-size: 1.1rem;"></i>
            <h3 style="margin: 0;">PSI Uyarısı</h3>
          </div>
          <span style="font-size: 0.78rem; color: #64748b;">Sadece PSI flag olan modeller (Gini alertten bağımsız)</span>
        </div>
        <div class="card-body">
          <div
            v-for="alert in psiAlertList"
            :key="'psi-' + alert.model_id"
            class="gini-alert-row"
            @click="router.push(`/models/${alert.model_id}`)"
          >
            <div class="gini-alert-header">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span class="gini-alert-name">{{ alert.model_name }}</span>
                <span style="background: #fef3c7; color: #92400e; font-size: 0.7rem; padding: 2px 8px; border-radius: 20px; font-weight: 600;">
                  PSI Flag
                </span>
                <span v-if="alert.alert_work_started" style="background: #dbeafe; color: #1d4ed8; font-size: 0.7rem; padding: 2px 8px; border-radius: 20px; font-weight: 600;">
                  <i class="pi pi-wrench" style="font-size: 0.65rem;"></i> Çalışma Başladı
                </span>
              </div>
              <span style="font-size: 0.8rem; color: #64748b;">{{ alert.scorecard_category }} · {{ alert.product_type }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Gini Karşılaştırma: Başvuru ── -->
      <div class="card" style="margin-bottom: 24px;">
        <div class="card-header">
          <h3>Başvuru Modelleri — Geliştirme vs Güncel Gini</h3>
        </div>
        <div class="card-body" style="height: 280px;">
          <Bar
            v-if="basvuruChartData"
            :data="basvuruChartData"
            :options="chartOptions"
          />
          <div v-else class="empty-state">
            <i class="pi pi-chart-bar"></i>
            <p>Başvuru modeli verisi yok</p>
          </div>
        </div>
      </div>

      <!-- ── Gini Karşılaştırma: Davranış ── -->
      <div class="card" style="margin-bottom: 24px;">
        <div class="card-header">
          <h3>Davranış Modelleri — Geliştirme vs Güncel Gini</h3>
        </div>
        <div class="card-body" style="height: 280px;">
          <Bar
            v-if="davranisChartData"
            :data="davranisChartData"
            :options="chartOptions"
          />
          <div v-else class="empty-state">
            <i class="pi pi-chart-bar"></i>
            <p>Davranış modeli verisi yok</p>
          </div>
        </div>
      </div>

      <!-- ── Geliştirme İlerleme Durumu (en altta) ── -->
      <div class="card">
        <div class="card-header">
          <h3>Geliştirme İlerleme Durumu</h3>
        </div>
        <div class="card-body">
          <div v-if="progressData.length > 0">
            <div
              v-for="project in progressData"
              :key="project.project_name"
              style="margin-bottom: 16px; cursor: pointer;"
              @click="router.push(`/development/${project.project_id}`)"
            >
              <div style="display: flex; justify-content: space-between; margin-bottom: 4px; align-items: center;">
                <div>
                  <span style="font-weight: 600; font-size: 0.85rem;">{{ project.project_name }}</span>
                  <span v-if="project.scorecard_category" style="margin-left: 8px; font-size: 0.75rem; color: #64748b;">
                    {{ project.scorecard_category }}
                  </span>
                </div>
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
