<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'
import DatePicker from 'primevue/datepicker'
import ToggleSwitch from 'primevue/toggleswitch'
import { developmentApi } from '../api'

const router = useRouter()
const toast = useToast()

const projects = ref([])
const initialLoading = ref(true)
const showDialog = ref(false)

const filterOwner = ref(null)
const filterStatus = ref(null)
const filterCategory = ref(null)
const owners = ref([])

const statusOptions = ['in_progress', 'completed', 'on_hold', 'cancelled']
const priorityOptions = ['low', 'medium', 'high', 'critical']
const scorecardCategories = ['Başvuru', 'Davranış']
const productTypes = ['KMH', 'Konut', 'Kredi Kartı', 'Oto', 'Tüketici']

const form = ref(getEmptyForm())

function getEmptyForm() {
  return {
    project_name: '',
    scorecard_category: null,
    product_type: null,
    owner: '',
    priority: 'medium',
    start_date: null,
    target_end_date: null,
    description: '',
    use_default_stages: true,
  }
}

async function loadProjects() {
  try {
    const params = {}
    if (filterOwner.value) params.owner = filterOwner.value
    if (filterStatus.value) params.status = filterStatus.value
    if (filterCategory.value) params.scorecard_category = filterCategory.value
    const [projectsRes, ownersRes] = await Promise.all([
      developmentApi.listProjects(params),
      developmentApi.listOwners(),
    ])
    const data = Array.isArray(projectsRes.data) ? projectsRes.data : projectsRes.data.items || []
    projects.value = data
    owners.value = ownersRes.data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', detail: 'Projeler yüklenemedi', life: 3000 })
  } finally {
    initialLoading.value = false
  }
}

function openNew() {
  form.value = getEmptyForm()
  showDialog.value = true
}

async function saveProject() {
  try {
    const data = {
      ...form.value,
      start_date: form.value.start_date
        ? form.value.start_date.toISOString().split('T')[0] : null,
      target_end_date: form.value.target_end_date
        ? form.value.target_end_date.toISOString().split('T')[0] : null,
    }
    await developmentApi.createProject(data)
    showDialog.value = false
    toast.add({ severity: 'success', summary: 'Başarılı', detail: 'Proje oluşturuldu', life: 3000 })
    await loadProjects()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', detail: 'Proje oluşturulamadı', life: 3000 })
  }
}

async function deleteProject(project) {
  if (!confirm(`"${project.project_name}" projesini silmek istediğinize emin misiniz?`)) return
  try {
    await developmentApi.deleteProject(project.id)
    toast.add({ severity: 'success', summary: 'Silindi', life: 3000 })
    await loadProjects()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', life: 3000 })
  }
}

function viewDetail(project) {
  router.push(`/development/${project.id}`)
}

const statusLabel = {
  in_progress: 'Devam Ediyor',
  completed: 'Tamamlandı',
  on_hold: 'Beklemede',
  cancelled: 'İptal',
}

const priorityLabel = {
  critical: 'Kritik',
  high: 'Yüksek',
  medium: 'Orta',
  low: 'Düşük',
}

function isOverdue(project) {
  if (!project.target_end_date || project.status === 'completed') return false
  return new Date(project.target_end_date) < new Date()
}

watch([filterOwner, filterStatus, filterCategory], () => {
  initialLoading.value = true
  loadProjects()
})

onMounted(loadProjects)
</script>

<template>
  <div>
    <div class="page-header">
      <h2>Geliştirilen Skorkartlar</h2>
      <button class="btn btn-primary" @click="openNew">
        <i class="pi pi-plus"></i> Yeni Proje
      </button>
    </div>
    <div class="page-body">
      <!-- Filters -->
      <div class="card">
        <div class="card-body" style="display: flex; gap: 12px; flex-wrap: wrap; align-items: center;">
          <Select
            v-model="filterCategory"
            :options="scorecardCategories"
            placeholder="Kategori"
            showClear
            style="width: 150px;"
          />
          <Select
            v-model="filterOwner"
            :options="owners"
            placeholder="Owner Filtrele"
            showClear
            style="width: 180px;"
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

      <!-- Project Cards -->
      <div v-if="projects.length" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 16px;">
        <div
          v-for="project in projects"
          :key="project.id"
          class="card project-card"
          @click="viewDetail(project)"
        >
          <div class="card-header">
            <div>
              <h3>{{ project.project_name }}</h3>
              <div style="display: flex; gap: 6px; margin-top: 6px;">
                <span class="status-badge" :class="project.status">{{ statusLabel[project.status] }}</span>
                <span class="priority-badge" :class="project.priority">{{ priorityLabel[project.priority] }}</span>
              </div>
            </div>
            <div style="text-align: right;" @click.stop>
              <button class="btn btn-danger btn-sm btn-icon" @click="deleteProject(project)">
                <i class="pi pi-trash"></i>
              </button>
            </div>
          </div>
          <div class="card-body">
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #64748b; margin-bottom: 8px;">
              <span><i class="pi pi-user" style="margin-right: 4px;"></i> {{ project.owner }}</span>
              <span v-if="project.scorecard_category">{{ project.scorecard_category }} · {{ project.product_type }}</span>
            </div>

            <div style="margin-bottom: 8px;">
              <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;">
                <span>İlerleme</span>
                <span style="font-weight: 600;">{{ project.progress }}%</span>
              </div>
              <div class="progress-bar-container">
                <div class="progress-bar-fill" :style="{ width: project.progress + '%' }"></div>
              </div>
            </div>

            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #94a3b8;">
              <span v-if="project.target_end_date" :style="{ color: isOverdue(project) ? '#ef4444' : '#94a3b8', fontWeight: isOverdue(project) ? 600 : 400 }">
                <i class="pi pi-calendar"></i> {{ project.target_end_date }}
                <span v-if="isOverdue(project)"> (Gecikmiş)</span>
              </span>
              <span v-if="project.stages">{{ project.stages.filter(s => s.status === 'completed').length }}/{{ project.stages.length }} aşama</span>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="!initialLoading" class="empty-state" style="margin-top: 48px;">
        <i class="pi pi-briefcase"></i>
        <p>Henüz geliştirme projesi bulunmuyor</p>
        <button class="btn btn-primary" @click="openNew" style="margin-top: 16px;">
          <i class="pi pi-plus"></i> İlk Projeyi Oluştur
        </button>
      </div>
    </div>

    <!-- New Project Dialog -->
    <Dialog v-model:visible="showDialog" header="Yeni Geliştirme Projesi" modal :style="{ width: '600px' }">
      <div class="form-grid" style="padding: 12px 0;">
        <div class="form-group">
          <label>Proje Adı *</label>
          <InputText v-model="form.project_name" />
        </div>
        <div class="form-group">
          <label>Owner *</label>
          <InputText v-model="form.owner" />
        </div>
        <div class="form-group">
          <label>Kategori</label>
          <Select v-model="form.scorecard_category" :options="scorecardCategories" placeholder="Seçiniz" />
        </div>
        <div class="form-group">
          <label>Ürün Tipi</label>
          <Select v-model="form.product_type" :options="productTypes" placeholder="Seçiniz" />
        </div>
        <div class="form-group">
          <label>Öncelik</label>
          <Select v-model="form.priority" :options="priorityOptions" />
        </div>
        <div class="form-group">
          <label>Başlangıç Tarihi</label>
          <DatePicker v-model="form.start_date" dateFormat="yy-mm-dd" />
        </div>
        <div class="form-group">
          <label>Hedef Bitiş Tarihi</label>
          <DatePicker v-model="form.target_end_date" dateFormat="yy-mm-dd" />
        </div>
        <div class="form-group">
          <label>Varsayılan Aşamaları Ekle</label>
          <ToggleSwitch v-model="form.use_default_stages" />
        </div>
        <div class="form-group full-width">
          <label>Açıklama</label>
          <Textarea v-model="form.description" rows="3" />
        </div>
      </div>

      <template #footer>
        <button class="btn btn-secondary" @click="showDialog = false">İptal</button>
        <button class="btn btn-primary" @click="saveProject" style="margin-left: 8px;">Oluştur</button>
      </template>
    </Dialog>
  </div>
</template>
