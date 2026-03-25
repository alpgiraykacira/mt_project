<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import InputNumber from 'primevue/inputnumber'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import DatePicker from 'primevue/datepicker'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement,
  LineElement, Title, Tooltip, Legend
} from 'chart.js'
import { modelsApi } from '../api'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

const route = useRoute()
const router = useRouter()
const toast = useToast()

const modelId = computed(() => Number(route.params.id))
const model = ref(null)
const initialLoading = ref(true)

// Technical Guide
const showTechDialog = ref(false)
const techForm = ref({ section_title: '', section_type: null, content: '', query_code: '', order_index: 0 })
const techSectionTypes = [
  { label: 'Sorgu', value: 'query' },
  { label: 'Değişken Hesaplama', value: 'variable_calc' },
  { label: 'Metodoloji', value: 'methodology' },
  { label: 'Backscoring', value: 'backscoring' },
  { label: 'Strateji Tablosu', value: 'strategy' },
  { label: 'Log', value: 'log' },
  { label: 'Bizu Tablosu', value: 'bizu' },
  { label: 'Not', value: 'note' },
]
const sectionTypeLabel = Object.fromEntries(techSectionTypes.map(t => [t.value, t.label]))

// Validation Reports
const showValDialog = ref(false)
const valForm = ref({ report_name: '', report_type: null, report_date: null, notes: '' })
const valFileInput = ref(null)
const valUploadFile = ref(null)
const reportTypes = [
  { label: 'Gelen (Incoming)', value: 'incoming' },
  { label: 'Giden (Outgoing)', value: 'outgoing' },
  { label: 'Wiseminer', value: 'wiseminer' },
]
const reportTypeLabel = { incoming: 'Gelen', outgoing: 'Giden', wiseminer: 'Wiseminer' }

// Gini History
const showGiniDialog = ref(false)
const giniForm = ref({ period: '', gini_value: null, target_ratio: null, sample_size: null, notes: '' })
const giniPeriodFrom = ref('')
const giniPeriodTo = ref('')
const giniViewMode = ref('monthly')  // 'monthly' | 'quarterly'

const MONTHLY_RE   = /^\d{4}-\d{2}$/
const QUARTERLY_RE = /^\d{4}-Q\d$/

const lastCompletedMonth = computed(() => {
  const now = new Date()
  const y = now.getFullYear()
  const m = now.getMonth()  // 0=Jan
  const prevMonth = m === 0 ? 12 : m
  const prevYear  = m === 0 ? y - 1 : y
  return `${prevYear}-${String(prevMonth).padStart(2, '0')}`
})

const lastCompletedQuarter = computed(() => {
  const now = new Date()
  const y = now.getFullYear()
  const q = Math.floor(now.getMonth() / 3)  // 0-indexed current quarter
  if (q === 0) return `${y - 1}-Q4`
  return `${y}-Q${q}`
})

// Rollout (İmplementasyon Kademeleri)
const showRolloutDialog = ref(false)
const rolloutForm = ref({ rollout_percentage: null, rollout_date: null, notes: '' })
const rolloutPercentages = [10, 25, 50, 75, 100]

// Model Variables (Feature Importance)
const showVarDialog = ref(false)
const varForm = ref({ variable_name: '', variable_description: '', iv_value: null, importance_rank: null, median_train: null, coefficient: null, woe_bin_count: null, notes: '' })

// Gini alert hesapla (kategori eşiği ile)
const redevelopmentAlert = computed(() => {
  if (!model.value?.gini_history?.length || model.value.gini_development == null) return null
  const monthly = [...model.value.gini_history]
    .filter(g => MONTHLY_RE.test(g.period))
    .sort((a, b) => b.period.localeCompare(a.period))
  if (monthly.length < 3) return null
  const last3 = monthly.slice(0, 3)
  const diffs = last3.map(g => model.value.gini_development - g.gini_value)
  if (!diffs.every(d => Math.abs(d) >= 0.05)) return null
  return {
    direction: diffs[0] > 0 ? 'drop' : 'rise',
    maxDiff: Math.max(...diffs.map(Math.abs)),
  }
})

const filteredGiniHistory = computed(() => {
  if (!model.value?.gini_history) return []
  const maxPeriod = giniViewMode.value === 'monthly'
    ? lastCompletedMonth.value
    : lastCompletedQuarter.value
  let records = [...model.value.gini_history].filter(g => {
    if (giniViewMode.value === 'monthly')   return MONTHLY_RE.test(g.period)
    if (giniViewMode.value === 'quarterly') return QUARTERLY_RE.test(g.period)
    return true
  }).filter(g => g.period <= maxPeriod)
  if (giniPeriodFrom.value) records = records.filter(g => g.period >= giniPeriodFrom.value)
  if (giniPeriodTo.value)   records = records.filter(g => g.period <= giniPeriodTo.value)
  return records.sort((a, b) => b.period.localeCompare(a.period))
})

const giniChartData = computed(() => {
  if (!model.value?.gini_history?.length) return null
  const maxPeriod = giniViewMode.value === 'monthly'
    ? lastCompletedMonth.value
    : lastCompletedQuarter.value
  const sorted = [...model.value.gini_history]
    .filter(g => {
      if (giniViewMode.value === 'monthly')   return MONTHLY_RE.test(g.period)
      if (giniViewMode.value === 'quarterly') return QUARTERLY_RE.test(g.period)
      return true
    })
    .filter(g => g.period <= maxPeriod)
    .sort((a, b) => a.period.localeCompare(b.period))
  if (!sorted.length) return null
  const datasets = [
    {
      label: 'Gini Değeri',
      data: sorted.map(g => g.gini_value),
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      fill: true,
      tension: 0.3,
      pointRadius: 3,
    },
  ]
  if (model.value.gini_development != null) {
    datasets.push({
      label: 'Geliştirme Ginisi',
      data: sorted.map(() => model.value.gini_development),
      borderColor: 'rgba(239, 68, 68, 0.7)',
      borderDash: [6, 3],
      borderWidth: 1.5,
      pointRadius: 0,
      fill: false,
      tension: 0,
    })
  }
  return { labels: sorted.map(g => g.period), datasets }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: true, position: 'bottom' } },
  scales: {
    y: { min: 0, max: 1, ticks: { callback: v => Math.round(v * 100) } },
  },
}

async function loadModel() {
  try {
    const res = await modelsApi.get(modelId.value)
    model.value = res.data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', detail: 'Model yüklenemedi', life: 3000 })
    router.push('/models')
  } finally {
    initialLoading.value = false
  }
}

// Technical Guide CRUD
async function saveTechnical() {
  try {
    await modelsApi.createTechnical(modelId.value, techForm.value)
    showTechDialog.value = false
    toast.add({ severity: 'success', summary: 'Eklendi', life: 3000 })
    await loadModel()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', life: 3000 })
  }
}

async function deleteTechnical(guideId) {
  if (!confirm('Bu bölümü silmek istediğinize emin misiniz?')) return
  try {
    await modelsApi.deleteTechnical(modelId.value, guideId)
    await loadModel()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', life: 3000 })
  }
}

// Validation CRUD
function onFileChange(e) {
  valUploadFile.value = e.target.files[0] || null
}

async function saveValidation() {
  try {
    if (valUploadFile.value) {
      // File upload path
      const fd = new FormData()
      fd.append('report_name', valForm.value.report_name)
      fd.append('report_type', valForm.value.report_type)
      if (valForm.value.report_date) {
        const d = new Date(valForm.value.report_date)
        fd.append('report_date', d.toISOString().split('T')[0])
      }
      if (valForm.value.notes) fd.append('notes', valForm.value.notes)
      fd.append('file', valUploadFile.value)
      await modelsApi.uploadValidation(modelId.value, fd)
    } else {
      const data = {
        ...valForm.value,
        report_date: valForm.value.report_date
          ? new Date(valForm.value.report_date).toISOString().split('T')[0] : null,
      }
      await modelsApi.createValidation(modelId.value, data)
    }
    showValDialog.value = false
    valUploadFile.value = null
    toast.add({ severity: 'success', summary: 'Eklendi', life: 3000 })
    await loadModel()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', life: 3000 })
  }
}

function downloadReport(report) {
  const url = modelsApi.downloadValidation(modelId.value, report.id)
  window.open(url, '_blank')
}

async function deleteValidation(reportId) {
  if (!confirm('Bu raporu silmek istediğinize emin misiniz?')) return
  try {
    await modelsApi.deleteValidation(modelId.value, reportId)
    await loadModel()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', life: 3000 })
  }
}

// Gini History (silme yok)
async function saveGini() {
  try {
    await modelsApi.createGiniRecord(modelId.value, giniForm.value)
    showGiniDialog.value = false
    toast.add({ severity: 'success', summary: 'Eklendi', life: 3000 })
    await loadModel()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', life: 3000 })
  }
}

function exportGiniToExcel() {
  const records = filteredGiniHistory.value
  if (!records.length) return

  const header = ['Dönem', 'Gini', 'Hedef Oranı', 'Örnek Boyutu', 'Notlar']
  const rows = records.map(g => [
    g.period,
    g.gini_value != null ? Math.round(g.gini_value * 100) : '',
    g.target_ratio != null ? (g.target_ratio * 100).toFixed(2) + '%' : '',
    g.sample_size ?? '',
    g.notes ?? '',
  ])

  const csvContent = [header, ...rows].map(r => r.map(v => `"${v}"`).join(',')).join('\n')
  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `gini_gecmisi_${model.value?.model_name?.replace(/\s/g, '_')}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

// Rollout CRUD
async function saveRollout() {
  try {
    const data = {
      ...rolloutForm.value,
      rollout_date: rolloutForm.value.rollout_date
        ? new Date(rolloutForm.value.rollout_date).toISOString().split('T')[0] : null,
    }
    await modelsApi.createRollout(modelId.value, data)
    showRolloutDialog.value = false
    toast.add({ severity: 'success', summary: 'Eklendi', life: 3000 })
    await loadModel()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', life: 3000 })
  }
}

async function deleteRollout(stageId) {
  if (!confirm('Bu kademeyi silmek istediğinize emin misiniz?')) return
  try {
    await modelsApi.deleteRollout(modelId.value, stageId)
    await loadModel()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', life: 3000 })
  }
}

// Model Variables CRUD
async function saveVariable() {
  try {
    await modelsApi.createVariable(modelId.value, varForm.value)
    showVarDialog.value = false
    toast.add({ severity: 'success', summary: 'Eklendi', life: 3000 })
    await loadModel()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', life: 3000 })
  }
}

async function deleteVariable(varId) {
  if (!confirm('Bu değişkeni silmek istediğinize emin misiniz?')) return
  try {
    await modelsApi.deleteVariable(modelId.value, varId)
    await loadModel()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', life: 3000 })
  }
}

const statusLabel = { active: 'Aktif', retired: 'Emekli', under_review: 'İnceleniyor' }

onMounted(loadModel)
</script>

<template>
  <div v-if="!initialLoading && model">
    <div class="page-header">
      <div>
        <button class="btn btn-secondary btn-sm" @click="router.push('/models')" style="margin-bottom: 8px;">
          <i class="pi pi-arrow-left"></i> Geri
        </button>
        <h2>{{ model.model_name }}</h2>
      </div>
      <div style="display: flex; align-items: center; gap: 8px;">
        <span v-if="model.psi_flag" style="background: #fef3c7; color: #92400e; font-size: 0.72rem; padding: 3px 10px; border-radius: 20px; font-weight: 600;">
          <i class="pi pi-flag"></i> PSI Flag
        </span>
        <span class="status-badge" :class="model.status">{{ statusLabel[model.status] || model.status }}</span>
      </div>
    </div>

    <div class="page-body">

      <!-- ── Gini Özet Kartları (train/cv/itt/oot/güncel) ── -->
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; margin-bottom: 20px;">
        <div class="stat-card info">
          <div class="stat-label">Train Gini</div>
          <div class="stat-value" style="font-size: 1.4rem;">
            {{ model.gini_train != null ? Math.round(model.gini_train * 100) : (model.gini_development != null ? Math.round(model.gini_development * 100) : '-') }}
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-label">CV Gini</div>
          <div class="stat-value" style="font-size: 1.4rem;">
            {{ model.gini_cv != null ? Math.round(model.gini_cv * 100) : (model.gini_validation != null ? Math.round(model.gini_validation * 100) : '-') }}
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-label">ITT Gini</div>
          <div class="stat-value" style="font-size: 1.4rem;">
            {{ model.gini_itt != null ? Math.round(model.gini_itt * 100) : '-' }}
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-label">OOT Gini</div>
          <div class="stat-value" style="font-size: 1.4rem;">
            {{ model.gini_oot != null ? Math.round(model.gini_oot * 100) : '-' }}
          </div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">Güncel Gini</div>
          <div class="stat-value" style="font-size: 1.4rem;">
            {{ model.gini_current != null ? Math.round(model.gini_current * 100) : '-' }}
          </div>
        </div>
      </div>

      <!-- ── Bağımlılık Uyarısı ── -->
      <div v-if="model.dependency_warning" style="background: #fff7ed; border: 1px solid #fed7aa; border-radius: 8px; padding: 12px 16px; margin-bottom: 16px; display: flex; gap: 10px; align-items: flex-start;">
        <i class="pi pi-exclamation-circle" style="color: #c2410c; margin-top: 2px;"></i>
        <span style="color: #7c2d12; font-size: 0.85rem;">{{ model.dependency_warning }}</span>
      </div>

      <!-- ── Bağlantılı Süreçler ── -->
      <div v-if="model.connected_processes" style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 12px 16px; margin-bottom: 16px; display: flex; gap: 10px; align-items: flex-start;">
        <i class="pi pi-link" style="color: #1d4ed8; margin-top: 2px;"></i>
        <span style="color: #1e3a8a; font-size: 0.85rem;">{{ model.connected_processes }}</span>
      </div>

      <!-- ── Info Card ── -->
      <div class="card" style="margin-bottom: 24px;">
        <div class="card-body">
          <div class="form-grid">
            <div class="form-group"><label>Kategori</label><span>{{ model.scorecard_category }}</span></div>
            <div class="form-group"><label>Ürün Tipi</label><span>{{ model.product_type || '-' }}</span></div>
            <div class="form-group"><label>Target Değişken</label><span>{{ model.target_variable || '-' }}</span></div>
            <div class="form-group"><label>Geliştirme Tablosu</label><span>{{ model.development_table || '-' }}</span></div>
            <div class="form-group">
              <label>Geliştirme Dönemi</label>
              <span>{{ model.development_period_start || '?' }} — {{ model.development_period_end || '?' }}</span>
            </div>
            <div class="form-group">
              <label>OOT Dönemi</label>
              <span>{{ model.oot_period_start || '?' }} — {{ model.oot_period_end || '?' }}</span>
            </div>
            <div class="form-group">
              <label>Validasyona Gönderilme Tarihi</label>
              <span>{{ model.validation_submission_date || '-' }}</span>
            </div>
            <div class="form-group"><label>Final Skoru</label><span>{{ model.final_score ?? '-' }}</span></div>
            <div class="form-group full-width" v-if="model.description">
              <label>Açıklama</label><span>{{ model.description }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ── İmplementasyon Kademeleri ── -->
      <div class="card" style="margin-bottom: 24px;">
        <div class="card-header">
          <h3>İmplementasyon Kademeleri</h3>
          <button class="btn btn-primary btn-sm" @click="rolloutForm = { rollout_percentage: null, rollout_date: null, notes: '' }; showRolloutDialog = true">
            <i class="pi pi-plus"></i> Kademe Ekle
          </button>
        </div>
        <div class="card-body">
          <div v-if="model.rollout_stages?.length" style="display: flex; gap: 12px; flex-wrap: wrap;">
            <div
              v-for="stage in model.rollout_stages"
              :key="stage.id"
              style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; min-width: 130px; position: relative;"
            >
              <div style="font-size: 1.6rem; font-weight: 700; color: #1e40af;">%{{ stage.rollout_percentage }}</div>
              <div style="font-size: 0.8rem; color: #64748b; margin-top: 2px;">{{ stage.rollout_date }}</div>
              <div v-if="stage.notes" style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">{{ stage.notes }}</div>
              <button
                class="btn btn-danger btn-sm btn-icon"
                style="position: absolute; top: 8px; right: 8px; width: 22px; height: 22px;"
                @click="deleteRollout(stage.id)"
              >
                <i class="pi pi-times" style="font-size: 0.65rem;"></i>
              </button>
            </div>
          </div>
          <div v-else class="empty-state" style="padding: 16px 0;">
            <i class="pi pi-calendar"></i>
            <p>Henüz implementasyon kademesi yok</p>
          </div>
        </div>
      </div>

      <!-- ── Gini Uyarısı ── -->
      <div v-if="redevelopmentAlert" class="gini-redevelopment-alert" style="margin-bottom: 16px;">
        <i class="pi pi-exclamation-triangle"></i>
        <span>
          <strong>Yeni model geliştirme önerilir:</strong>
          Son 3 ay üst üste izleme Gini'si geliştirme Gini'sinden
          {{ redevelopmentAlert.direction === 'drop' ? 'düştü' : 'yükseldi' }}
          (maks. sapma: {{ Math.round(redevelopmentAlert.maxDiff * 100) }} puan).
        </span>
      </div>

      <!-- ── Tabs ── -->
      <TabView>

        <!-- Teknik Kılavuz -->
        <TabPanel header="Teknik Kılavuz">
          <div style="margin-bottom: 12px; text-align: right;">
            <button class="btn btn-primary btn-sm" @click="techForm = { section_title: '', section_type: null, content: '', query_code: '', order_index: 0 }; showTechDialog = true">
              <i class="pi pi-plus"></i> Bölüm Ekle
            </button>
          </div>
          <div v-if="model.technical_details?.length">
            <div v-for="guide in model.technical_details" :key="guide.id" class="card" style="margin-bottom: 12px;">
              <div class="card-header">
                <div>
                  <h3>{{ guide.section_title }}</h3>
                  <span class="status-badge pending" style="margin-top: 4px;">{{ sectionTypeLabel[guide.section_type] || guide.section_type }}</span>
                </div>
                <button class="btn btn-danger btn-sm btn-icon" @click="deleteTechnical(guide.id)">
                  <i class="pi pi-trash"></i>
                </button>
              </div>
              <div class="card-body">
                <p style="white-space: pre-wrap;">{{ guide.content }}</p>
                <pre v-if="guide.query_code" style="background: #f1f5f9; padding: 12px; border-radius: 8px; margin-top: 12px; overflow-x: auto; font-size: 0.85rem;">{{ guide.query_code }}</pre>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <i class="pi pi-file"></i>
            <p>Teknik kılavuz bölümü eklenmemiş</p>
          </div>
        </TabPanel>

        <!-- Model Değişkenleri -->
        <TabPanel header="Model Değişkenleri">
          <div style="margin-bottom: 12px; text-align: right;">
            <button class="btn btn-primary btn-sm" @click="varForm = { variable_name: '', variable_description: '', iv_value: null, importance_rank: null, median_train: null, coefficient: null, woe_bin_count: null, notes: '' }; showVarDialog = true">
              <i class="pi pi-plus"></i> Değişken Ekle
            </button>
          </div>
          <DataTable v-if="model.model_variables?.length" :value="model.model_variables" stripedRows responsiveLayout="scroll">
            <Column field="importance_rank" header="Sıra" style="width: 60px;" sortable />
            <Column field="variable_name" header="Değişken" sortable />
            <Column field="variable_description" header="Açıklama" />
            <Column field="median_train" header="Medyan (Train)" sortable>
              <template #body="{ data }">
                <strong style="color: #1d4ed8;">{{ data.median_train ?? '-' }}</strong>
              </template>
            </Column>
            <Column field="iv_value" header="IV" sortable>
              <template #body="{ data }">{{ data.iv_value != null ? data.iv_value.toFixed(4) : '-' }}</template>
            </Column>
            <Column field="coefficient" header="Katsayı">
              <template #body="{ data }">{{ data.coefficient != null ? data.coefficient.toFixed(4) : '-' }}</template>
            </Column>
            <Column field="woe_bin_count" header="WOE Bin" />
            <Column header="" style="width: 60px;">
              <template #body="{ data }">
                <button class="btn btn-danger btn-sm btn-icon" @click="deleteVariable(data.id)">
                  <i class="pi pi-trash"></i>
                </button>
              </template>
            </Column>
          </DataTable>
          <div v-else class="empty-state">
            <i class="pi pi-list"></i>
            <p>Model değişkeni girilmemiş</p>
          </div>
        </TabPanel>

        <!-- Validasyon Raporları -->
        <TabPanel header="Validasyon Raporları">
          <div style="margin-bottom: 12px; text-align: right;">
            <button class="btn btn-primary btn-sm" @click="valForm = { report_name: '', report_type: null, report_date: null, notes: '' }; valUploadFile = null; showValDialog = true">
              <i class="pi pi-plus"></i> Rapor Ekle
            </button>
          </div>
          <DataTable v-if="model.validation_reports?.length" :value="model.validation_reports" stripedRows>
            <Column field="report_name" header="Rapor Adı" />
            <Column field="report_type" header="Tür">
              <template #body="{ data }">
                <span class="status-badge" :class="data.report_type === 'incoming' ? 'active' : data.report_type === 'wiseminer' ? 'info' : 'pending'">
                  {{ reportTypeLabel[data.report_type] || data.report_type }}
                </span>
              </template>
            </Column>
            <Column field="report_date" header="Tarih" />
            <Column field="file_path" header="Dosya">
              <template #body="{ data }">
                <span v-if="data.has_file">
                  <button class="btn btn-secondary btn-sm" @click="downloadReport(data)" style="font-size: 0.75rem;">
                    <i class="pi pi-download"></i> İndir
                  </button>
                </span>
                <span v-else-if="data.file_path" style="font-size: 0.8rem; color: #64748b;">{{ data.file_path }}</span>
                <span v-else style="color: #94a3b8;">-</span>
              </template>
            </Column>
            <Column field="notes" header="Notlar" />
            <Column header="" style="width: 60px;">
              <template #body="{ data }">
                <button class="btn btn-danger btn-sm btn-icon" @click="deleteValidation(data.id)">
                  <i class="pi pi-trash"></i>
                </button>
              </template>
            </Column>
          </DataTable>
          <div v-else class="empty-state">
            <i class="pi pi-file-pdf"></i>
            <p>Validasyon raporu bulunmuyor</p>
          </div>
        </TabPanel>

        <!-- Gini Geçmişi -->
        <TabPanel header="Gini Geçmişi">
          <!-- Grafik -->
          <div v-if="giniChartData" class="card" style="margin-bottom: 16px;">
            <div class="card-header"><h3>Gini Trend</h3></div>
            <div class="card-body" style="height: 250px;">
              <Line :data="giniChartData" :options="chartOptions" />
            </div>
          </div>

          <!-- Filtreler ve Aksiyon butonları -->
          <div style="display: flex; gap: 12px; flex-wrap: wrap; align-items: center; margin-bottom: 12px;">
            <!-- Aylık / Çeyreklik toggle -->
            <div style="display: flex; border: 1px solid #e2e8f0; border-radius: 6px; overflow: hidden; flex-shrink: 0;">
              <button
                @click="giniViewMode = 'monthly'"
                :style="{
                  padding: '4px 14px', fontSize: '0.82rem', border: 'none', cursor: 'pointer',
                  background: giniViewMode === 'monthly' ? '#3b82f6' : '#f8fafc',
                  color:      giniViewMode === 'monthly' ? '#fff'    : '#64748b',
                }"
              >Aylık</button>
              <button
                @click="giniViewMode = 'quarterly'"
                :style="{
                  padding: '4px 14px', fontSize: '0.82rem', border: 'none', cursor: 'pointer',
                  background: giniViewMode === 'quarterly' ? '#3b82f6' : '#f8fafc',
                  color:      giniViewMode === 'quarterly' ? '#fff'    : '#64748b',
                }"
              >Çeyreklik</button>
            </div>
            <span style="font-size: 0.75rem; color: #94a3b8;">
              max: {{ giniViewMode === 'monthly' ? lastCompletedMonth : lastCompletedQuarter }}
            </span>
            <div style="display: flex; align-items: center; gap: 6px; font-size: 0.85rem;">
              <label>Dönem:</label>
              <input v-model="giniPeriodFrom" type="text" :placeholder="giniViewMode === 'monthly' ? '2024-01' : '2024-Q1'" style="border: 1px solid #e2e8f0; border-radius: 6px; padding: 4px 8px; font-size: 0.82rem; width: 100px;" />
              <span>—</span>
              <input v-model="giniPeriodTo" type="text" :placeholder="giniViewMode === 'monthly' ? '2026-02' : '2025-Q4'" style="border: 1px solid #e2e8f0; border-radius: 6px; padding: 4px 8px; font-size: 0.82rem; width: 100px;" />
            </div>
            <button class="btn btn-secondary btn-sm" @click="exportGiniToExcel" :disabled="!filteredGiniHistory.length">
              <i class="pi pi-file-excel"></i> Excel'e Aktar
            </button>
            <button class="btn btn-primary btn-sm" @click="giniForm = { period: '', gini_value: null, target_ratio: null, sample_size: null, notes: '' }; showGiniDialog = true" style="margin-left: auto;">
              <i class="pi pi-plus"></i> Kayıt Ekle
            </button>
          </div>

          <!-- Kaydırmalı liste -->
          <div style="max-height: 400px; overflow-y: auto;">
            <DataTable
              v-if="filteredGiniHistory.length"
              :value="filteredGiniHistory"
              stripedRows
              scrollable
              scrollHeight="flex"
            >
              <Column field="period" header="Dönem" sortable />
              <Column field="gini_value" header="Gini" sortable>
                <template #body="{ data }">{{ Math.round(data.gini_value * 100) }}</template>
              </Column>
              <Column field="target_ratio" header="Hedef Oranı" sortable>
                <template #body="{ data }">
                  {{ data.target_ratio != null ? (data.target_ratio * 100).toFixed(2) + '%' : '-' }}
                </template>
              </Column>
              <Column field="sample_size" header="Örnek Boyutu" />
              <Column field="notes" header="Notlar" />
            </DataTable>
            <div v-else class="empty-state">
              <i class="pi pi-chart-line"></i>
              <p>Gini geçmişi bulunamadı</p>
            </div>
          </div>
        </TabPanel>

      </TabView>
    </div>

    <!-- Technical Guide Dialog -->
    <Dialog v-model:visible="showTechDialog" header="Teknik Kılavuz Bölümü Ekle" modal :style="{ width: '600px' }">
      <div class="form-grid" style="padding: 12px 0;">
        <div class="form-group">
          <label>Bölüm Başlığı *</label>
          <InputText v-model="techForm.section_title" />
        </div>
        <div class="form-group">
          <label>Tür</label>
          <Select v-model="techForm.section_type" :options="techSectionTypes" optionLabel="label" optionValue="value" placeholder="Seçiniz" />
        </div>
        <div class="form-group full-width">
          <label>İçerik *</label>
          <Textarea v-model="techForm.content" rows="4" />
        </div>
        <div class="form-group full-width">
          <label>Sorgu / Kod</label>
          <Textarea v-model="techForm.query_code" rows="4" style="font-family: monospace;" />
        </div>
      </div>
      <template #footer>
        <button class="btn btn-secondary" @click="showTechDialog = false">İptal</button>
        <button class="btn btn-primary" @click="saveTechnical" style="margin-left: 8px;">Ekle</button>
      </template>
    </Dialog>

    <!-- Model Variable Dialog -->
    <Dialog v-model:visible="showVarDialog" header="Model Değişkeni Ekle" modal :style="{ width: '600px' }">
      <div class="form-grid" style="padding: 12px 0;">
        <div class="form-group">
          <label>Değişken Adı *</label>
          <InputText v-model="varForm.variable_name" />
        </div>
        <div class="form-group">
          <label>Önem Sırası</label>
          <InputNumber v-model="varForm.importance_rank" :min="1" />
        </div>
        <div class="form-group full-width">
          <label>Açıklama</label>
          <InputText v-model="varForm.variable_description" />
        </div>
        <div class="form-group">
          <label>Medyan (Train) *</label>
          <InputNumber v-model="varForm.median_train" :minFractionDigits="2" :maxFractionDigits="6" />
        </div>
        <div class="form-group">
          <label>IV Değeri</label>
          <InputNumber v-model="varForm.iv_value" :minFractionDigits="4" :maxFractionDigits="6" :min="0" />
        </div>
        <div class="form-group">
          <label>Katsayı</label>
          <InputNumber v-model="varForm.coefficient" :minFractionDigits="4" :maxFractionDigits="6" />
        </div>
        <div class="form-group">
          <label>WOE Bin Sayısı</label>
          <InputNumber v-model="varForm.woe_bin_count" :min="1" />
        </div>
        <div class="form-group full-width">
          <label>Notlar</label>
          <Textarea v-model="varForm.notes" rows="2" />
        </div>
      </div>
      <template #footer>
        <button class="btn btn-secondary" @click="showVarDialog = false">İptal</button>
        <button class="btn btn-primary" @click="saveVariable" style="margin-left: 8px;">Ekle</button>
      </template>
    </Dialog>

    <!-- Validation Report Dialog -->
    <Dialog v-model:visible="showValDialog" header="Validasyon Raporu Ekle" modal :style="{ width: '540px' }">
      <div class="form-grid" style="padding: 12px 0;">
        <div class="form-group">
          <label>Rapor Adı *</label>
          <InputText v-model="valForm.report_name" />
        </div>
        <div class="form-group">
          <label>Tür *</label>
          <Select v-model="valForm.report_type" :options="reportTypes" optionLabel="label" optionValue="value" placeholder="Seçiniz" />
        </div>
        <div class="form-group">
          <label>Tarih</label>
          <DatePicker v-model="valForm.report_date" dateFormat="yy-mm-dd" />
        </div>
        <div class="form-group">
          <label>Dosya Yükle</label>
          <input ref="valFileInput" type="file" @change="onFileChange" style="font-size: 0.85rem;" />
          <span v-if="valUploadFile" style="font-size: 0.75rem; color: #10b981; margin-top: 4px;">{{ valUploadFile.name }}</span>
        </div>
        <div class="form-group full-width">
          <label>Notlar</label>
          <Textarea v-model="valForm.notes" rows="2" />
        </div>
      </div>
      <template #footer>
        <button class="btn btn-secondary" @click="showValDialog = false">İptal</button>
        <button class="btn btn-primary" @click="saveValidation" style="margin-left: 8px;">Ekle</button>
      </template>
    </Dialog>

    <!-- Gini History Dialog -->
    <Dialog v-model:visible="showGiniDialog" header="Gini Kaydı Ekle" modal :style="{ width: '480px' }">
      <div class="form-grid" style="padding: 12px 0;">
        <div class="form-group">
          <label>Dönem * (örn: 2025-03 veya 2025-Q1)</label>
          <InputText v-model="giniForm.period" />
        </div>
        <div class="form-group">
          <label>Gini Değeri *</label>
          <InputNumber v-model="giniForm.gini_value" :minFractionDigits="2" :maxFractionDigits="4" :min="0" :max="1" />
        </div>
        <div class="form-group">
          <label>Hedef Oranı</label>
          <InputNumber v-model="giniForm.target_ratio" :minFractionDigits="2" :maxFractionDigits="4" :min="0" :max="1" />
        </div>
        <div class="form-group">
          <label>Örnek Boyutu</label>
          <InputNumber v-model="giniForm.sample_size" :min="0" />
        </div>
        <div class="form-group full-width">
          <label>Notlar</label>
          <Textarea v-model="giniForm.notes" rows="2" />
        </div>
      </div>
      <template #footer>
        <button class="btn btn-secondary" @click="showGiniDialog = false">İptal</button>
        <button class="btn btn-primary" @click="saveGini" style="margin-left: 8px;">Ekle</button>
      </template>
    </Dialog>

    <!-- Rollout Dialog -->
    <Dialog v-model:visible="showRolloutDialog" header="İmplementasyon Kademesi Ekle" modal :style="{ width: '400px' }">
      <div class="form-grid" style="padding: 12px 0;">
        <div class="form-group">
          <label>Kademe (%) *</label>
          <Select v-model="rolloutForm.rollout_percentage" :options="rolloutPercentages" placeholder="Seçiniz" />
        </div>
        <div class="form-group">
          <label>Tarih *</label>
          <DatePicker v-model="rolloutForm.rollout_date" dateFormat="yy-mm-dd" />
        </div>
        <div class="form-group full-width">
          <label>Notlar</label>
          <Textarea v-model="rolloutForm.notes" rows="2" />
        </div>
      </div>
      <template #footer>
        <button class="btn btn-secondary" @click="showRolloutDialog = false">İptal</button>
        <button class="btn btn-primary" @click="saveRollout" style="margin-left: 8px;">Ekle</button>
      </template>
    </Dialog>
  </div>

  <div v-else-if="initialLoading" class="page-body">
    <div class="empty-state">
      <i class="pi pi-spin pi-spinner" style="font-size: 2rem;"></i>
      <p>Yükleniyor...</p>
    </div>
  </div>
</template>
