<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'
import InputNumber from 'primevue/inputnumber'
import DatePicker from 'primevue/datepicker'
import { modelsApi } from '../api'

const router = useRouter()
const toast = useToast()

const models = ref([])
const loading = ref(true)
const showDialog = ref(false)
const editMode = ref(false)

const filterType = ref(null)
const filterStatus = ref(null)
const searchText = ref('')

const modelTypes = ['PD', 'LGD', 'EAD', 'Behavioural', 'Application', 'Other']
const statusOptions = ['active', 'retired', 'under_review']

const form = ref(getEmptyForm())

function getEmptyForm() {
  return {
    model_name: '',
    model_type: null,
    segment: '',
    development_period_start: null,
    development_period_end: null,
    development_table: '',
    target_variable: '',
    gini_development: null,
    gini_validation: null,
    gini_current: null,
    final_score: null,
    status: 'active',
    owner: '',
    description: '',
  }
}

const filteredModels = computed(() => {
  return models.value.filter(m => {
    if (filterType.value && m.model_type !== filterType.value) return false
    if (filterStatus.value && m.status !== filterStatus.value) return false
    if (searchText.value && !m.model_name.toLowerCase().includes(searchText.value.toLowerCase())) return false
    return true
  })
})

async function loadModels() {
  loading.value = true
  try {
    const res = await modelsApi.list()
    models.value = res.data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', detail: 'Modeller yüklenemedi', life: 3000 })
  } finally {
    loading.value = false
  }
}

function openNew() {
  form.value = getEmptyForm()
  editMode.value = false
  showDialog.value = true
}

function openEdit(model) {
  form.value = {
    ...model,
    development_period_start: model.development_period_start ? new Date(model.development_period_start) : null,
    development_period_end: model.development_period_end ? new Date(model.development_period_end) : null,
  }
  editMode.value = true
  showDialog.value = true
}

async function saveModel() {
  try {
    const data = {
      ...form.value,
      development_period_start: form.value.development_period_start
        ? form.value.development_period_start.toISOString().split('T')[0] : null,
      development_period_end: form.value.development_period_end
        ? form.value.development_period_end.toISOString().split('T')[0] : null,
    }

    if (editMode.value) {
      await modelsApi.update(form.value.id, data)
      toast.add({ severity: 'success', summary: 'Başarılı', detail: 'Model güncellendi', life: 3000 })
    } else {
      await modelsApi.create(data)
      toast.add({ severity: 'success', summary: 'Başarılı', detail: 'Model oluşturuldu', life: 3000 })
    }
    showDialog.value = false
    await loadModels()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', detail: 'İşlem başarısız', life: 3000 })
  }
}

async function deleteModel(model) {
  if (!confirm(`"${model.model_name}" modelini silmek istediğinize emin misiniz?`)) return
  try {
    await modelsApi.delete(model.id)
    toast.add({ severity: 'success', summary: 'Silindi', detail: 'Model silindi', life: 3000 })
    await loadModels()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', detail: 'Silme başarısız', life: 3000 })
  }
}

function viewDetail(model) {
  router.push(`/models/${model.id}`)
}

const statusLabel = {
  active: 'Aktif',
  retired: 'Emekli',
  under_review: 'İnceleniyor',
}

onMounted(loadModels)
</script>

<template>
  <div>
    <div class="page-header">
      <h2>Mevcut Skorkartlar</h2>
      <button class="btn btn-primary" @click="openNew">
        <i class="pi pi-plus"></i> Yeni Model
      </button>
    </div>
    <div class="page-body">
      <!-- Filters -->
      <div class="card">
        <div class="card-body" style="display: flex; gap: 12px; flex-wrap: wrap; align-items: center;">
          <InputText v-model="searchText" placeholder="Model ara..." style="width: 220px;" />
          <Select
            v-model="filterType"
            :options="modelTypes"
            placeholder="Model Türü"
            showClear
            style="width: 160px;"
          />
          <Select
            v-model="filterStatus"
            :options="statusOptions"
            placeholder="Durum"
            showClear
            style="width: 160px;"
          />
        </div>
      </div>

      <!-- Data Table -->
      <div class="card">
        <div class="card-body data-table-wrapper">
          <DataTable
            :value="filteredModels"
            :loading="loading"
            paginator
            :rows="10"
            stripedRows
            removableSort
            :rowHover="true"
            @row-click="(e) => viewDetail(e.data)"
            style="cursor: pointer;"
          >
            <Column field="model_name" header="Model Adı" sortable style="min-width: 200px;" />
            <Column field="model_type" header="Tür" sortable style="width: 100px;" />
            <Column field="segment" header="Segment" sortable style="min-width: 150px;" />
            <Column field="owner" header="Owner" sortable style="min-width: 120px;" />
            <Column field="gini_current" header="Güncel Gini" sortable style="width: 120px;">
              <template #body="{ data }">
                <span v-if="data.gini_current != null" style="font-weight: 600;">
                  {{ (data.gini_current * 100).toFixed(1) }}%
                </span>
                <span v-else style="color: #94a3b8;">-</span>
              </template>
            </Column>
            <Column field="status" header="Durum" sortable style="width: 120px;">
              <template #body="{ data }">
                <span class="status-badge" :class="data.status">
                  {{ statusLabel[data.status] || data.status }}
                </span>
              </template>
            </Column>
            <Column header="İşlem" style="width: 100px;">
              <template #body="{ data }">
                <div style="display: flex; gap: 4px;" @click.stop>
                  <button class="btn btn-secondary btn-sm btn-icon" @click="openEdit(data)" title="Düzenle">
                    <i class="pi pi-pencil"></i>
                  </button>
                  <button class="btn btn-danger btn-sm btn-icon" @click="deleteModel(data)" title="Sil">
                    <i class="pi pi-trash"></i>
                  </button>
                </div>
              </template>
            </Column>
            <template #empty>
              <div class="empty-state">
                <i class="pi pi-inbox"></i>
                <p>Henüz model bulunmuyor</p>
              </div>
            </template>
          </DataTable>
        </div>
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <Dialog
      v-model:visible="showDialog"
      :header="editMode ? 'Model Düzenle' : 'Yeni Model Oluştur'"
      modal
      :style="{ width: '700px' }"
    >
      <div class="form-grid" style="padding: 12px 0;">
        <div class="form-group">
          <label>Model Adı *</label>
          <InputText v-model="form.model_name" />
        </div>
        <div class="form-group">
          <label>Model Türü *</label>
          <Select v-model="form.model_type" :options="modelTypes" placeholder="Seçiniz" />
        </div>
        <div class="form-group">
          <label>Segment</label>
          <InputText v-model="form.segment" />
        </div>
        <div class="form-group">
          <label>Owner</label>
          <InputText v-model="form.owner" />
        </div>
        <div class="form-group">
          <label>Geliştirme Başlangıç</label>
          <DatePicker v-model="form.development_period_start" dateFormat="yy-mm-dd" />
        </div>
        <div class="form-group">
          <label>Geliştirme Bitiş</label>
          <DatePicker v-model="form.development_period_end" dateFormat="yy-mm-dd" />
        </div>
        <div class="form-group">
          <label>Geliştirme Tablosu</label>
          <InputText v-model="form.development_table" />
        </div>
        <div class="form-group">
          <label>Target Değişken</label>
          <InputText v-model="form.target_variable" />
        </div>
        <div class="form-group">
          <label>Gini (Geliştirme)</label>
          <InputNumber v-model="form.gini_development" :minFractionDigits="2" :maxFractionDigits="4" :min="0" :max="1" />
        </div>
        <div class="form-group">
          <label>Gini (Validasyon)</label>
          <InputNumber v-model="form.gini_validation" :minFractionDigits="2" :maxFractionDigits="4" :min="0" :max="1" />
        </div>
        <div class="form-group">
          <label>Gini (Güncel)</label>
          <InputNumber v-model="form.gini_current" :minFractionDigits="2" :maxFractionDigits="4" :min="0" :max="1" />
        </div>
        <div class="form-group">
          <label>Final Skoru</label>
          <InputNumber v-model="form.final_score" :minFractionDigits="2" :maxFractionDigits="4" />
        </div>
        <div class="form-group">
          <label>Durum</label>
          <Select v-model="form.status" :options="statusOptions" />
        </div>
        <div class="form-group full-width">
          <label>Açıklama</label>
          <Textarea v-model="form.description" rows="3" />
        </div>
      </div>

      <template #footer>
        <button class="btn btn-secondary" @click="showDialog = false">İptal</button>
        <button class="btn btn-primary" @click="saveModel" style="margin-left: 8px;">
          {{ editMode ? 'Güncelle' : 'Oluştur' }}
        </button>
      </template>
    </Dialog>
  </div>
</template>
