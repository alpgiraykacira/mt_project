<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'
import DatePicker from 'primevue/datepicker'
import Checkbox from 'primevue/checkbox'
import { developmentApi } from '../api'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const projectId = computed(() => Number(route.params.id))
const project = ref(null)
const initialLoading = ref(true)

// Stage dialog
const showStageDialog = ref(false)
const stageForm = ref({ stage_name: '', stage_code: '', description: '', deadline: null, notes: '', parent_id: null })

// Task dialog
const showTaskDialog = ref(false)
const taskStageId = ref(null)
const taskForm = ref({ task_description: '' })

// Edit project dialog
const showEditDialog = ref(false)
const editForm = ref({})

const statusOptions = ['in_progress', 'completed', 'on_hold', 'cancelled']
const stageStatusOptions = ['pending', 'in_progress', 'completed', 'blocked']
const priorityOptions = ['low', 'medium', 'high', 'critical']
const scorecardCategories = ['Başvuru', 'Davranış']
const productTypes = ['KMH', 'Konut', 'Kredi Kartı', 'Oto', 'Tüketici']

// Flatten hierarchical stages into a list with depth info
const flatStages = computed(() => {
  if (!project.value?.stages) return []
  const result = []
  function walk(stages, depth) {
    for (const stage of stages) {
      result.push({ ...stage, depth })
      if (stage.children?.length) {
        walk(stage.children, depth + 1)
      }
    }
  }
  walk(project.value.stages, 0)
  return result
})

async function loadProject() {
  try {
    const res = await developmentApi.getProject(projectId.value)
    project.value = res.data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', detail: 'Proje yüklenemedi', life: 3000 })
    router.push('/development')
  } finally {
    initialLoading.value = false
  }
}

// Project edit
function openEdit() {
  editForm.value = {
    ...project.value,
    start_date: project.value.start_date ? new Date(project.value.start_date) : null,
    target_end_date: project.value.target_end_date ? new Date(project.value.target_end_date) : null,
  }
  showEditDialog.value = true
}

async function saveProject() {
  try {
    const data = {
      ...editForm.value,
      start_date: editForm.value.start_date
        ? editForm.value.start_date.toISOString().split('T')[0] : null,
      target_end_date: editForm.value.target_end_date
        ? editForm.value.target_end_date.toISOString().split('T')[0] : null,
    }
    await developmentApi.updateProject(projectId.value, data)
    showEditDialog.value = false
    toast.add({ severity: 'success', summary: 'Güncellendi', life: 3000 })
    await loadProject()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', life: 3000 })
  }
}

// Stage CRUD
function openStageDialog(parentId = null) {
  stageForm.value = { stage_name: '', stage_code: '', description: '', deadline: null, notes: '', parent_id: parentId }
  showStageDialog.value = true
}

async function saveStage() {
  try {
    const data = {
      ...stageForm.value,
      deadline: stageForm.value.deadline
        ? stageForm.value.deadline.toISOString().split('T')[0] : null,
      order_index: (() => {
        const parentId = stageForm.value.parent_id
        if (parentId) {
          const parent = flatStages.value.find(s => s.id === parentId)
          return parent?.children?.length || 0
        }
        return project.value.stages?.length || 0
      })(),
    }
    await developmentApi.createStage(projectId.value, data)
    showStageDialog.value = false
    toast.add({ severity: 'success', summary: 'Aşama eklendi', life: 3000 })
    await loadProject()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', life: 3000 })
  }
}

async function updateStageStatus(stage, newStatus) {
  try {
    await developmentApi.updateStage(projectId.value, stage.id, { status: newStatus })
    await loadProject()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', life: 3000 })
  }
}

async function deleteStage(stage) {
  if (!confirm(`"${stage.stage_name}" aşamasını silmek istediğinize emin misiniz?`)) return
  try {
    await developmentApi.deleteStage(projectId.value, stage.id)
    await loadProject()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', life: 3000 })
  }
}

// Task CRUD
function openTaskDialog(stageId) {
  taskStageId.value = stageId
  taskForm.value = { task_description: '' }
  showTaskDialog.value = true
}

const savingTask = ref(false)

async function saveTask() {
  if (savingTask.value) return
  savingTask.value = true
  try {
    await developmentApi.createTask(taskStageId.value, taskForm.value)
    showTaskDialog.value = false
    await loadProject()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', life: 3000 })
  } finally {
    savingTask.value = false
  }
}

async function toggleTask(task, stageId) {
  // Optimistic update - toggle immediately for snappy UI
  task.is_completed = !task.is_completed
  try {
    await developmentApi.updateTask(stageId, task.id, { is_completed: task.is_completed })
  } catch (err) {
    // Revert on failure
    task.is_completed = !task.is_completed
    toast.add({ severity: 'error', summary: 'Hata', life: 3000 })
  }
}

async function deleteTask(task, stageId) {
  try {
    await developmentApi.deleteTask(stageId, task.id)
    await loadProject()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', life: 3000 })
  }
}

const statusLabel = {
  in_progress: 'Devam Ediyor', completed: 'Tamamlandı',
  on_hold: 'Beklemede', cancelled: 'İptal',
  pending: 'Bekliyor', blocked: 'Engelli',
}

const statusIcon = {
  pending: 'pi pi-clock',
  in_progress: 'pi pi-spin pi-spinner',
  completed: 'pi pi-check-circle',
  blocked: 'pi pi-exclamation-triangle',
}

const statusColor = {
  completed: '#10b981',
  in_progress: '#3b82f6',
  blocked: '#ef4444',
  pending: '#94a3b8',
}

function isOverdue(deadline) {
  if (!deadline) return false
  return new Date(deadline) < new Date()
}

onMounted(loadProject)
</script>

<template>
  <div v-if="!initialLoading && project">
    <div class="page-header">
      <div>
        <button class="btn btn-secondary btn-sm" @click="router.push('/development')" style="margin-bottom: 8px;">
          <i class="pi pi-arrow-left"></i> Geri
        </button>
        <h2>{{ project.project_name }}</h2>
      </div>
      <div style="display: flex; gap: 8px;">
        <span class="status-badge" :class="project.status">{{ statusLabel[project.status] }}</span>
        <button class="btn btn-secondary btn-sm" @click="openEdit">
          <i class="pi pi-pencil"></i> Düzenle
        </button>
      </div>
    </div>

    <div class="page-body">
      <!-- Project Summary -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">Owner</div>
          <div class="stat-value" style="font-size: 1.2rem;">{{ project.owner }}</div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">İlerleme</div>
          <div class="stat-value">{{ project.progress }}%</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Hedef Tarih</div>
          <div class="stat-value" style="font-size: 1.2rem;" :style="{ color: project.target_end_date && isOverdue(project.target_end_date) && project.status !== 'completed' ? '#ef4444' : '#1e293b' }">
            {{ project.target_end_date || '-' }}
          </div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">Kategori / Ürün</div>
          <div class="stat-value" style="font-size: 1.1rem;">
            {{ project.scorecard_category || '-' }} · {{ project.product_type || '-' }}
          </div>
        </div>
      </div>

      <!-- Progress Bar -->
      <div class="card" style="margin-bottom: 24px;">
        <div class="card-body">
          <div class="progress-bar-container" style="height: 12px;">
            <div class="progress-bar-fill" :style="{ width: project.progress + '%' }"></div>
          </div>
        </div>
      </div>

      <!-- Stages (hierarchical, flat-rendered with indentation) -->
      <div class="card">
        <div class="card-header">
          <h3>Geliştirme Aşamaları</h3>
          <button class="btn btn-primary btn-sm" @click="openStageDialog(null)">
            <i class="pi pi-plus"></i> Aşama Ekle
          </button>
        </div>
        <div class="card-body">
          <div v-if="flatStages.length">
            <div
              v-for="stage in flatStages"
              :key="stage.id"
              :style="{
                marginLeft: (stage.depth * 28) + 'px',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                padding: stage.depth === 0 ? '16px' : '10px 14px',
                marginBottom: '8px',
                borderLeftColor: statusColor[stage.status] || '#e2e8f0',
                borderLeftWidth: '4px',
                background: stage.depth > 0 ? '#fafbfc' : 'white',
              }"
            >
              <!-- Stage Header -->
              <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="flex: 1;">
                  <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                    <i :class="statusIcon[stage.status]" :style="{ color: statusColor[stage.status] || '#94a3b8' }"></i>
                    <span style="font-size: 0.8rem; color: #64748b; font-weight: 600; min-width: 36px;" v-if="stage.stage_code">{{ stage.stage_code }}</span>
                    <strong :style="{ fontSize: stage.depth === 0 ? '0.95rem' : '0.88rem' }">{{ stage.stage_name }}</strong>
                    <span class="status-badge" :class="stage.status" style="font-size: 0.7rem;">{{ statusLabel[stage.status] }}</span>
                  </div>
                  <p v-if="stage.description" style="font-size: 0.8rem; color: #64748b; margin-top: 4px; margin-left: 28px;">
                    {{ stage.description }}
                  </p>
                </div>
                <div style="display: flex; gap: 4px; align-items: center; flex-shrink: 0;">
                  <span v-if="stage.deadline" style="font-size: 0.75rem; margin-right: 8px;"
                    :style="{ color: isOverdue(stage.deadline) && stage.status !== 'completed' ? '#ef4444' : '#94a3b8' }">
                    <i class="pi pi-calendar"></i> {{ stage.deadline }}
                  </span>
                  <Select
                    :modelValue="stage.status"
                    @update:modelValue="(val) => updateStageStatus(stage, val)"
                    :options="stageStatusOptions"
                    style="width: 140px; font-size: 0.8rem;"
                  />
                  <button class="btn btn-sm btn-icon" style="background: none; color: #3b82f6; padding: 4px;" @click="openStageDialog(stage.id)" title="Alt aşama ekle">
                    <i class="pi pi-plus" style="font-size: 0.7rem;"></i>
                  </button>
                  <button class="btn btn-danger btn-sm btn-icon" @click="deleteStage(stage)">
                    <i class="pi pi-trash"></i>
                  </button>
                </div>
              </div>

              <!-- Notes -->
              <div v-if="stage.notes" style="margin-top: 8px; margin-left: 28px; padding: 8px 12px; background: #f8fafc; border-radius: 6px; font-size: 0.85rem;">
                {{ stage.notes }}
              </div>

              <!-- Tasks -->
              <div v-if="stage.tasks?.length || stage.depth <= 1" style="margin-top: 8px; margin-left: 28px;">
                <div v-for="task in stage.tasks" :key="task.id" style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                  <Checkbox :modelValue="task.is_completed" :binary="true" @update:modelValue="toggleTask(task, stage.id)" />
                  <span :style="{ textDecoration: task.is_completed ? 'line-through' : 'none', color: task.is_completed ? '#94a3b8' : '#1e293b', fontSize: '0.85rem' }">
                    {{ task.task_description }}
                  </span>
                  <button class="btn btn-sm btn-icon" style="background: none; color: #94a3b8; padding: 2px 4px;" @click="deleteTask(task, stage.id)">
                    <i class="pi pi-times" style="font-size: 0.7rem;"></i>
                  </button>
                </div>
                <button class="btn btn-sm" style="background: none; color: #3b82f6; padding: 4px 0; font-size: 0.8rem;" @click="openTaskDialog(stage.id)">
                  <i class="pi pi-plus" style="font-size: 0.7rem;"></i> Görev ekle
                </button>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <i class="pi pi-list"></i>
            <p>Henüz aşama eklenmemiş</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Stage Dialog -->
    <Dialog v-model:visible="showStageDialog" header="Yeni Aşama Ekle" modal :style="{ width: '500px' }">
      <div class="form-grid" style="padding: 12px 0;">
        <div class="form-group">
          <label>Aşama Kodu</label>
          <InputText v-model="stageForm.stage_code" placeholder="örn: 3.1.2" />
        </div>
        <div class="form-group">
          <label>Aşama Adı *</label>
          <InputText v-model="stageForm.stage_name" />
        </div>
        <div class="form-group full-width">
          <label>Açıklama</label>
          <Textarea v-model="stageForm.description" rows="2" />
        </div>
        <div class="form-group">
          <label>Deadline</label>
          <DatePicker v-model="stageForm.deadline" dateFormat="yy-mm-dd" />
        </div>
        <div class="form-group full-width">
          <label>Notlar (yapılanlar/yapılacaklar)</label>
          <Textarea v-model="stageForm.notes" rows="3" />
        </div>
      </div>
      <template #footer>
        <button class="btn btn-secondary" @click="showStageDialog = false">İptal</button>
        <button class="btn btn-primary" @click="saveStage" style="margin-left: 8px;">Ekle</button>
      </template>
    </Dialog>

    <!-- Add Task Dialog -->
    <Dialog v-model:visible="showTaskDialog" header="Görev Ekle" modal :style="{ width: '400px' }">
      <div style="padding: 12px 0;">
        <div class="form-group">
          <label>Görev Açıklaması *</label>
          <InputText v-model="taskForm.task_description" style="width: 100%;" />
        </div>
      </div>
      <template #footer>
        <button class="btn btn-secondary" @click="showTaskDialog = false">İptal</button>
        <button class="btn btn-primary" @click="saveTask" :disabled="savingTask" style="margin-left: 8px;">Ekle</button>
      </template>
    </Dialog>

    <!-- Edit Project Dialog -->
    <Dialog v-model:visible="showEditDialog" header="Proje Düzenle" modal :style="{ width: '600px' }">
      <div class="form-grid" style="padding: 12px 0;">
        <div class="form-group">
          <label>Proje Adı</label>
          <InputText v-model="editForm.project_name" />
        </div>
        <div class="form-group">
          <label>Owner</label>
          <InputText v-model="editForm.owner" />
        </div>
        <div class="form-group">
          <label>Kategori</label>
          <Select v-model="editForm.scorecard_category" :options="scorecardCategories" placeholder="Seçiniz" />
        </div>
        <div class="form-group">
          <label>Ürün Tipi</label>
          <Select v-model="editForm.product_type" :options="productTypes" placeholder="Seçiniz" />
        </div>
        <div class="form-group">
          <label>Durum</label>
          <Select v-model="editForm.status" :options="statusOptions" />
        </div>
        <div class="form-group">
          <label>Öncelik</label>
          <Select v-model="editForm.priority" :options="priorityOptions" />
        </div>
        <div class="form-group">
          <label>Başlangıç Tarihi</label>
          <DatePicker v-model="editForm.start_date" dateFormat="yy-mm-dd" />
        </div>
        <div class="form-group">
          <label>Hedef Bitiş</label>
          <DatePicker v-model="editForm.target_end_date" dateFormat="yy-mm-dd" />
        </div>
        <div class="form-group full-width">
          <label>Açıklama</label>
          <Textarea v-model="editForm.description" rows="3" />
        </div>
      </div>
      <template #footer>
        <button class="btn btn-secondary" @click="showEditDialog = false">İptal</button>
        <button class="btn btn-primary" @click="saveProject" style="margin-left: 8px;">Güncelle</button>
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
