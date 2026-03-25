<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { dashboardApi } from '../api'

const router = useRouter()

const summary  = ref({ models: {}, development: {} })
const giniData = ref({ basvuru: [], davranis: [] })
const progressData = ref([])
const giniAlerts   = ref([])
const initialLoading = ref(true)

// ── Alert lookup: model_id → alert entry ──
const alertByModelId = computed(() => {
  const map = {}
  for (const a of giniAlerts.value) map[a.model_id] = a
  return map
})

// ── Discriminatory Power severity ──
const dpSeverity = computed(() => {
  if (giniAlerts.value.some(a => a.gini_alert)) return 'critical'
  if (giniAlerts.value.some(a => a.psi_flag))   return 'warning'
  return 'ok'
})

// ── Calibration severity (from summary counts) ──
const calSeverity = computed(() => {
  if (summary.value.models?.cal_critical > 0) return 'critical'
  if (summary.value.models?.cal_warning  > 0) return 'warning'
  return 'ok'
})

// severity → card style mapping
function severityCard(sev) {
  if (sev === 'critical') return { border: '1.5px solid #fca5a5', background: '#fff1f2' }
  if (sev === 'warning')  return { border: '1.5px solid #fde68a', background: '#fffbeb' }
  return { border: '1.5px solid #bbf7d0', background: '#f0fdf4' }
}
function severityIcon(sev) {
  if (sev === 'critical') return { icon: 'pi pi-times-circle', color: '#ef4444' }
  if (sev === 'warning')  return { icon: 'pi pi-exclamation-triangle', color: '#f59e0b' }
  return { icon: 'pi pi-check-circle', color: '#10b981' }
}
function severityLabel(sev) {
  if (sev === 'critical') return 'Aksiyon Alınmalı'
  if (sev === 'warning')  return 'Takip Edilmeli'
  return 'Sorun Yok'
}
function severityTextColor(sev) {
  if (sev === 'critical') return '#b91c1c'
  if (sev === 'warning')  return '#92400e'
  return '#166534'
}

// giniAlerts model'leri (yalnızca gini_alert olanlar)
const giniAlertList = computed(() => giniAlerts.value.filter(a => a.gini_alert))

const redFlags = computed(() => giniAlerts.value.filter(a => a.gini_alert).length)
const yellowFlags = computed(() => giniAlerts.value.filter(a => !a.gini_alert && a.psi_flag).length)
const greenFlags = computed(() => (summary.value.models?.active || 0) - redFlags.value - yellowFlags.value)

// Gini segment helpers
function modelAlert(modelId) { return alertByModelId.value[modelId] || null }

function giniDiff(m) {
  if (m.gini_development == null || m.gini_current == null) return null
  return m.gini_current - m.gini_development
}

onMounted(async () => {
  try {
    const [summaryRes, giniRes, progressRes, alertsRes] = await Promise.all([
      dashboardApi.getSummary(),
      dashboardApi.getGiniOverview(),
      dashboardApi.getDevelopmentProgress(),
      dashboardApi.getGiniAlerts(),
    ])
    summary.value      = summaryRes.data
    giniData.value     = giniRes.data
    progressData.value = progressRes.data
    giniAlerts.value   = alertsRes.data
  } catch (err) {
    console.error('Dashboard load error:', err)
  } finally {
    initialLoading.value = false
  }
})
</script>

<template>
  <div>
    <div class="page-header"><h2>Dashboard</h2></div>
    <div class="page-body">

      <!-- ══ Mevcut Skorkartlar ══ -->
      <div style="margin-bottom: 8px; font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; letter-spacing: 0.05em;">Mevcut Skorkartlar</div>
      <div class="stats-grid" style="margin-bottom: 32px;">

        <!-- 1. Aktif Model Sayısı -->
        <div class="stat-card info">
          <div class="stat-label">Aktif Model</div>
          <div class="stat-value">{{ summary.models?.active || 0 }}</div>
          <div class="stat-detail">
            <span style="color: #3b82f6;">{{ summary.models?.basvuru || 0 }} Başvuru</span>
            &nbsp;·&nbsp;
            <span style="color: #10b981;">{{ summary.models?.davranis || 0 }} Davranış</span>
          </div>
        </div>

        <!-- 2. Discriminatory Power Alert -->
        <div class="stat-card info">
          <div class="stat-label" style="text-transform: none;">Discriminatory Power Alert</div>
          <div class="stat-detail" style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px;">
            <span style="font-size: 0.75rem; background: #dcfce7; color: #166534; padding: 2px 10px; border-radius: 10px; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;">
              <i class="pi pi-circle-fill" style="font-size: 0.45rem; color: #22c55e;"></i> {{ greenFlags }}
            </span>
            <span style="font-size: 0.75rem; background: #fef3c7; color: #92400e; padding: 2px 10px; border-radius: 10px; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;">
              <i class="pi pi-circle-fill" style="font-size: 0.45rem; color: #f59e0b;"></i> {{ yellowFlags }}
            </span>
            <span style="font-size: 0.75rem; background: #fee2e2; color: #b91c1c; padding: 2px 10px; border-radius: 10px; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;">
              <i class="pi pi-circle-fill" style="font-size: 0.45rem; color: #ef4444;"></i> {{ redFlags }}
            </span>
          </div>
        </div>

        <!-- 3. Calibration Alert -->
        <div class="stat-card" :style="severityCard(calSeverity)">
          <div class="stat-label" style="display: flex; align-items: center; gap: 5px;">
            <i :class="severityIcon(calSeverity).icon" :style="{ color: severityIcon(calSeverity).color, fontSize: '0.85rem' }"></i>
            Calibration Alert
          </div>
          <div class="stat-value" :style="{ color: severityTextColor(calSeverity), fontSize: '1.1rem', fontWeight: 700 }">
            {{ severityLabel(calSeverity) }}
          </div>
          <div class="stat-detail" style="display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px;">
            <span v-if="summary.models?.cal_critical" style="font-size: 0.7rem; background: #fee2e2; color: #b91c1c; padding: 1px 6px; border-radius: 10px;">
              {{ summary.models.cal_critical }} kritik
            </span>
            <span v-if="summary.models?.cal_warning" style="font-size: 0.7rem; background: #fef3c7; color: #92400e; padding: 1px 6px; border-radius: 10px;">
              {{ summary.models.cal_warning }} takip
            </span>
          </div>
        </div>

      </div>

      <!-- ══ Geliştirilen Skorkartlar ══ -->
      <div style="margin-bottom: 8px; font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; letter-spacing: 0.05em;">Geliştirilen Skorkartlar</div>
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
        <div class="stat-card danger">
          <div class="stat-label">Geciken Aşamalar</div>
          <div class="stat-value">{{ summary.development?.overdue_stages || 0 }}</div>
        </div>
      </div>

      <!-- ══ Discriminatory Power İzleme ══ -->
      <div class="card" style="margin-bottom: 24px;">
        <div class="card-header">
          <h3>Model İzleme</h3>
          <span style="font-size: 0.78rem; color: #64748b;">
            Başvuru &lt;50 · Davranış &lt;55 · Ardışık ≥5pp sapma · PSI
          </span>
        </div>
        <div class="card-body" style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; max-height: 420px; overflow-y: auto;">

          <!-- Başvuru segment -->
          <div>
            <div style="font-size: 0.72rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 10px;">
              Başvuru
            </div>
            <div v-if="(giniData.basvuru || []).length" style="display: flex; flex-direction: column; gap: 8px;">
              <div
                v-for="m in giniData.basvuru"
                :key="m.model_id"
                style="background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; cursor: pointer;"
                @click="router.push(`/models/${m.model_id}`)"
              >
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px; flex-wrap: wrap;">
                  <span style="font-size: 0.82rem; font-weight: 600; color: #1e293b;">{{ m.model_name }}</span>
                  <span v-if="m.in_development" style="background: #dbeafe; color: #1d4ed8; font-size: 0.65rem; padding: 1px 7px; border-radius: 10px; font-weight: 600;">
                    <i class="pi pi-sync" style="font-size: 0.55rem;"></i> Yeni Versiyon Geliştiriliyor
                  </span>
                </div>
                <div style="display: flex; gap: 16px;">
                  <div style="text-align: center;">
                    <div style="font-size: 0.65rem; color: #94a3b8; margin-bottom: 2px;">Geliştirme</div>
                    <div style="font-size: 1rem; font-weight: 700; color: #1d4ed8;">
                      {{ m.gini_development != null ? Math.round(m.gini_development * 100) : '-' }}
                    </div>
                  </div>
                  <div style="display: flex; align-items: center; color: #cbd5e1; font-size: 0.9rem;">→</div>
                  <div style="text-align: center;">
                    <div style="font-size: 0.65rem; color: #94a3b8; margin-bottom: 2px;">Güncel</div>
                    <div style="font-size: 1rem; font-weight: 700; color: #374151;">
                      {{ m.gini_current != null ? Math.round(m.gini_current * 100) : '-' }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="empty-state" style="padding: 16px 0;"><p>Veri yok</p></div>
          </div>

          <!-- Davranış segment -->
          <div>
            <div style="font-size: 0.72rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 10px;">
              Davranış
            </div>
            <div v-if="(giniData.davranis || []).length" style="display: flex; flex-direction: column; gap: 8px;">
              <div
                v-for="m in giniData.davranis"
                :key="m.model_id"
                style="background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; cursor: pointer;"
                @click="router.push(`/models/${m.model_id}`)"
              >
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px; flex-wrap: wrap;">
                  <span style="font-size: 0.82rem; font-weight: 600; color: #1e293b;">{{ m.model_name }}</span>
                  <span v-if="m.in_development" style="background: #dbeafe; color: #1d4ed8; font-size: 0.65rem; padding: 1px 7px; border-radius: 10px; font-weight: 600;">
                    <i class="pi pi-sync" style="font-size: 0.55rem;"></i> Yeni Versiyon Geliştiriliyor
                  </span>
                </div>
                <div style="display: flex; gap: 16px;">
                  <div style="text-align: center;">
                    <div style="font-size: 0.65rem; color: #94a3b8; margin-bottom: 2px;">Geliştirme</div>
                    <div style="font-size: 1rem; font-weight: 700; color: #1d4ed8;">
                      {{ m.gini_development != null ? Math.round(m.gini_development * 100) : '-' }}
                    </div>
                  </div>
                  <div style="display: flex; align-items: center; color: #cbd5e1; font-size: 0.9rem;">→</div>
                  <div style="text-align: center;">
                    <div style="font-size: 0.65rem; color: #94a3b8; margin-bottom: 2px;">Güncel</div>
                    <div style="font-size: 1rem; font-weight: 700; color: #374151;">
                      {{ m.gini_current != null ? Math.round(m.gini_current * 100) : '-' }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="empty-state" style="padding: 16px 0;"><p>Veri yok</p></div>
          </div>

        </div>

        <!-- Alert detayları (gini_alert olanlar) -->
        <div v-if="giniAlertList.length" style="border-top: 1px solid #f1f5f9; margin-top: 16px; padding: 16px 20px 20px 20px;">
          <div style="font-size: 0.72rem; text-transform: uppercase; color: #ef4444; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">
            <i class="pi pi-exclamation-triangle"></i> Alert Detayları
          </div>
          <div
            v-for="alert in giniAlertList"
            :key="'det-' + alert.model_id"
            class="gini-alert-row"
            @click="router.push(`/models/${alert.model_id}`)"
          >
            <div class="gini-alert-header">
              <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                <span class="gini-alert-name">{{ alert.model_name }}</span>
                <span v-if="alert.alert_reason.includes('threshold_breach')" style="background: #fee2e2; color: #dc2626; font-size: 0.7rem; padding: 2px 8px; border-radius: 20px;">
                  Eşik Altı ({{ alert.scorecard_category === 'Başvuru' ? '<50' : '<55' }})
                </span>
                <span v-if="alert.alert_reason.includes('consecutive_deviation')" style="background: #fff7ed; color: #c2410c; font-size: 0.7rem; padding: 2px 8px; border-radius: 20px;">Ardışık Sapma</span>
                <span v-if="alert.psi_flag" style="background: #fef3c7; color: #92400e; font-size: 0.7rem; padding: 2px 8px; border-radius: 20px; font-weight: 600;">
                  <i class="pi pi-flag" style="font-size: 0.65rem;"></i> PSI Flag
                </span>
                <span v-if="alert.alert_work_started" style="background: #dbeafe; color: #1d4ed8; font-size: 0.7rem; padding: 2px 8px; border-radius: 20px; font-weight: 600;">
                  <i class="pi pi-wrench" style="font-size: 0.65rem;"></i> Çalışma Başladı
                </span>
              </div>
              <span v-if="alert.direction" class="gini-alert-direction" :class="alert.direction">
                <i :class="alert.direction === 'drop' ? 'pi pi-arrow-down' : 'pi pi-arrow-up'"></i>
                {{ alert.direction === 'drop' ? 'Düşüş' : 'Artış' }}
              </span>
            </div>
            <div class="gini-alert-body">
              <div class="gini-alert-ref">
                Geliştirme: <strong>{{ alert.gini_development != null ? Math.round(alert.gini_development * 100) : '-' }}</strong>
                &nbsp;·&nbsp;
                Güncel: <strong :style="{ color: alert.gini_current < alert.gini_threshold ? '#ef4444' : '#374151' }">
                  {{ alert.gini_current != null ? Math.round(alert.gini_current * 100) : '-' }}
                </strong>
                &nbsp;·&nbsp; Eşik: <strong>{{ Math.round(alert.gini_threshold * 100) }}</strong>
                &nbsp;·&nbsp; {{ alert.scorecard_category }}
              </div>
              <div v-if="alert.last3_periods.length" class="gini-alert-months">
                <div v-for="(period, i) in alert.last3_periods" :key="period" class="gini-alert-month">
                  <span class="gini-month-label">{{ period }}</span>
                  <span class="gini-month-value">{{ Math.round(alert.last3_values[i] * 100) }}</span>
                  <span class="gini-month-diff" :class="alert.direction">
                    {{ alert.direction === 'drop' ? '-' : '+' }}{{ (Math.abs(alert.last3_diffs[i]) * 100).toFixed(1) }}pp
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ══ Geliştirme İlerleme Durumu ══ -->
      <div class="card">
        <div class="card-header"><h3>Geliştirme İlerleme Durumu</h3></div>
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
                  <span v-if="project.scorecard_category" style="margin-left: 8px; font-size: 0.75rem; color: #64748b;">{{ project.scorecard_category }}</span>
                </div>
                <span style="font-size: 0.8rem; color: #64748b;">{{ project.owner }} · {{ project.progress }}%</span>
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
