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
const loading = ref(true)

// Technical Guide
const showTechDialog = ref(false)
const techForm = ref({ section_title: '', section_type: null, content: '', query_code: '', order_index: 0 })
const techSectionTypes = ['query', 'variable_calc', 'methodology', 'note']

// Validation Reports
const showValDialog = ref(false)
const valForm = ref({ report_name: '', report_type: null, file_path: '', report_date: null, notes: '' })
const reportTypes = ['incoming', 'outgoing']

// Gini History
const showGiniDialog = ref(false)
const giniForm = ref({ period: '', gini_value: null, sample_size: null, notes: '' })

const giniChartData = computed(() => {
  if (!model.value?.gini_history?.length) return null
  const sorted = [...model.value.gini_history].sort((a, b) => a.period.localeCompare(b.period))
  return {
    labels: sorted.map(g => g.period),
    datasets: [{
      label: 'Gini Değeri',
      data: sorted.map(g => g.gini_value),
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      fill: true,
      tension: 0.3,
    }],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    y: { min: 0, max: 1, ticks: { callback: v => (v * 100).toFixed(0) + '%' } },
  },
}

async function loadModel() {
  loading.value = true
  try {
    const res = await modelsApi.get(modelId.value)
    model.value = res.data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', detail: 'Model yüklenemedi', life: 3000 })
    router.push('/models')
  } finally {
    loading.value = false
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
async function saveValidation() {
  try {
    const data = {
      ...valForm.value,
      report_date: valForm.value.report_date
        ? new Date(valForm.value.report_date).toISOString().split('T')[0] : null,
    }
    await modelsApi.createValidation(modelId.value, data)
    showValDialog.value = false
    toast.add({ severity: 'success', summary: 'Eklendi', life: 3000 })
    await loadModel()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', life: 3000 })
  }
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

// Gini History CRUD
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

async function deleteGini(recordId) {
  if (!confirm('Bu kaydı silmek istediğinize emin misiniz?')) return
  try {
    await modelsApi.deleteGiniRecord(modelId.value, recordId)
    await loadModel()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', life: 3000 })
  }
}

const statusLabel = { active: 'Aktif', retired: 'Emekli', under_review: 'İnceleniyor' }
const sectionTypeLabel = { query: 'Sorgu', variable_calc: 'Değişken Hesaplama', methodology: 'Metodoloji', note: 'Not' }
const reportTypeLabel = { incoming: 'Gelen', outgoing: 'Giden' }

onMounted(loadModel)
</script>

<template>
  <div v-if="!loading && model">
    <div class="page-header">
      <div>
        <button class="btn btn-secondary btn-sm" @click="router.push('/models')" style="margin-bottom: 8px;">
          <i class="pi pi-arrow-left"></i> Geri
        </button>
        <h2>{{ model.model_name }}</h2>
      </div>
      <span class="status-badge" :class="model.status">{{ statusLabel[model.status] || model.status }}</span>
    </div>

    <div class="page-body">
      <!-- Model Summary -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">Model Türü</div>
          <div class="stat-value" style="font-size: 1.4rem;">{{ model.model_type }}</div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">Gini (Geliştirme)</div>
          <div class="stat-value">{{ model.gini_development != null ? (model.gini_development * 100).toFixed(1) + '%' : '-' }}</div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">Gini (Validasyon)</div>
          <div class="stat-value">{{ model.gini_validation != null ? (model.gini_validation * 100).toFixed(1) + '%' : '-' }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">Gini (Güncel)</div>
          <div class="stat-value">{{ model.gini_current != null ? (model.gini_current * 100).toFixed(1) + '%' : '-' }}</div>
        </div>
      </div>

      <!-- Info Card -->
      <div class="card" style="margin-bottom: 24px;">
        <div class="card-body">
          <div class="form-grid">
            <div class="form-group"><label>Segment</label><span>{{ model.segment || '-' }}</span></div>
            <div class="form-group"><label>Owner</label><span>{{ model.owner || '-' }}</span></div>
            <div class="form-group"><label>Target Değişken</label><span>{{ model.target_variable || '-' }}</span></div>
            <div class="form-group"><label>Geliştirme Tablosu</label><span>{{ model.development_table || '-' }}</span></div>
            <div class="form-group"><label>Geliştirme Dönemi</label>
              <span>{{ model.development_period_start || '?' }} — {{ model.development_period_end || '?' }}</span>
            </div>
            <div class="form-group"><label>Final Skoru</label><span>{{ model.final_score ?? '-' }}</span></div>
            <div class="form-group full-width" v-if="model.description">
              <label>Açıklama</label><span>{{ model.description }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <TabView>
        <!-- Technical Guide Tab -->
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

        <!-- Validation Reports Tab -->
        <TabPanel header="Validasyon Raporları">
          <div style="margin-bottom: 12px; text-align: right;">
            <button class="btn btn-primary btn-sm" @click="valForm = { report_name: '', report_type: null, file_path: '', report_date: null, notes: '' }; showValDialog = true">
              <i class="pi pi-plus"></i> Rapor Ekle
            </button>
          </div>
          <DataTable v-if="model.validation_reports?.length" :value="model.validation_reports" stripedRows>
            <Column field="report_name" header="Rapor Adı" />
            <Column field="report_type" header="Tür">
              <template #body="{ data }">
                <span class="status-badge" :class="data.report_type === 'incoming' ? 'active' : 'info'">
                  {{ reportTypeLabel[data.report_type] }}
                </span>
              </template>
            </Column>
            <Column field="report_date" header="Tarih" />
            <Column field="file_path" header="Dosya Yolu" />
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

        <!-- Gini History Tab -->
        <TabPanel header="Gini Geçmişi">
          <div style="margin-bottom: 12px; text-align: right;">
            <button class="btn btn-primary btn-sm" @click="giniForm = { period: '', gini_value: null, sample_size: null, notes: '' }; showGiniDialog = true">
              <i class="pi pi-plus"></i> Kayıt Ekle
            </button>
          </div>
          <div v-if="giniChartData" class="card" style="margin-bottom: 16px;">
            <div class="card-header"><h3>Gini Trend</h3></div>
            <div class="card-body" style="height: 250px;">
              <Line :data="giniChartData" :options="chartOptions" />
            </div>
          </div>
          <DataTable v-if="model.gini_history?.length" :value="model.gini_history" stripedRows>
            <Column field="period" header="Dönem" sortable />
            <Column field="gini_value" header="Gini" sortable>
              <template #body="{ data }">{{ (data.gini_value * 100).toFixed(1) }}%</template>
            </Column>
            <Column field="sample_size" header="Örnek Boyutu" />
            <Column field="notes" header="Notlar" />
            <Column header="" style="width: 60px;">
              <template #body="{ data }">
                <button class="btn btn-danger btn-sm btn-icon" @click="deleteGini(data.id)">
                  <i class="pi pi-trash"></i>
                </button>
              </template>
            </Column>
          </DataTable>
          <div v-else-if="!giniChartData" class="empty-state">
            <i class="pi pi-chart-line"></i>
            <p>Gini geçmişi bulunmuyor</p>
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
          <Select v-model="techForm.section_type" :options="techSectionTypes" placeholder="Seçiniz" />
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

    <!-- Validation Report Dialog -->
    <Dialog v-model:visible="showValDialog" header="Validasyon Raporu Ekle" modal :style="{ width: '500px' }">
      <div class="form-grid" style="padding: 12px 0;">
        <div class="form-group">
          <label>Rapor Adı *</label>
          <InputText v-model="valForm.report_name" />
        </div>
        <div class="form-group">
          <label>Tür *</label>
          <Select v-model="valForm.report_type" :options="reportTypes" placeholder="Seçiniz" />
        </div>
        <div class="form-group">
          <label>Dosya Yolu</label>
          <InputText v-model="valForm.file_path" />
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
    <Dialog v-model:visible="showGiniDialog" header="Gini Kaydı Ekle" modal :style="{ width: '450px' }">
      <div class="form-grid" style="padding: 12px 0;">
        <div class="form-group">
          <label>Dönem * (örn: 2025-Q1)</label>
          <InputText v-model="giniForm.period" />
        </div>
        <div class="form-group">
          <label>Gini Değeri *</label>
          <InputNumber v-model="giniForm.gini_value" :minFractionDigits="2" :maxFractionDigits="4" :min="0" :max="1" />
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
  </div>
  <div v-else class="page-body">
    <div class="empty-state">
      <i class="pi pi-spin pi-spinner" style="font-size: 2rem;"></i>
      <p>Yükleniyor...</p>
    </div>
  </div>
</template>
