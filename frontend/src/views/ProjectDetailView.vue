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
const loading = ref(true)

// Stage dialog
const showStageDialog = ref(false)
const stageForm = ref({ stage_name: '', description: '', deadline: null, notes: '' })

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

async function loadProject() {
  loading.value = true
  try {
    const res = await developmentApi.getProject(projectId.value)
    project.value = res.data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', detail: 'Proje yüklenemedi', life: 3000 })
    router.push('/development')
  } finally {
    loading.value = false
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
async function saveStage() {
  try {
    const data = {
      ...stageForm.value,
      deadline: stageForm.value.deadline
        ? stageForm.value.deadline.toISOString().split('T')[0] : null,
      order_index: project.value.stages?.length || 0,
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

async function saveTask() {
  try {
    await developmentApi.createTask(taskStageId.value, taskForm.value)
    showTaskDialog.value = false
    await loadProject()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Hata', life: 3000 })
  }
}

async function toggleTask(task, stageId) {
  try {
    await developmentApi.updateTask(stageId, task.id, { is_completed: !task.is_completed })
    await loadProject()
  } catch (err) {
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

function isOverdue(deadline) {
  if (!deadline) return false
  return new Date(deadline) < new Date()
}

onMounted(loadProject)
</script>

<template>
  <div v-if="!loading && project">
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
          <div class="stat-label">Aşama Durumu</div>
          <div class="stat-value" style="font-size: 1.2rem;">
            {{ project.stages?.filter(s => s.status === 'completed').length || 0 }} / {{ project.stages?.length || 0 }}
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

      <!-- Stages -->
      <div class="card">
        <div class="card-header">
          <h3>Geliştirme Aşamaları</h3>
          <button class="btn btn-primary btn-sm" @click="stageForm = { stage_name: '', description: '', deadline: null, notes: '' }; showStageDialog = true">
            <i class="pi pi-plus"></i> Aşama Ekle
          </button>
        </div>
        <div class="card-body">
          <div v-if="project.stages?.length">
            <div
              v-for="(stage, index) in project.stages"
              :key="stage.id"
              style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 12px;"
              :style="{ borderLeftColor: stage.status === 'completed' ? '#10b981' : stage.status === 'in_progress' ? '#3b82f6' : stage.status === 'blocked' ? '#ef4444' : '#e2e8f0', borderLeftWidth: '4px' }"
            >
              <!-- Stage Header -->
              <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <i :class="statusIcon[stage.status]" :style="{ color: stage.status === 'completed' ? '#10b981' : stage.status === 'blocked' ? '#ef4444' : '#3b82f6' }"></i>
                    <strong style="font-size: 0.95rem;">{{ index + 1 }}. {{ stage.stage_name }}</strong>
                    <span class="status-badge" :class="stage.status">{{ statusLabel[stage.status] }}</span>
                  </div>
                  <p v-if="stage.description" style="font-size: 0.8rem; color: #64748b; margin-top: 4px; margin-left: 28px;">
                    {{ stage.description }}
                  </p>
                </div>
                <div style="display: flex; gap: 4px; align-items: center;">
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
              <div style="margin-top: 12px; margin-left: 28px;">
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
        <div class="form-group full-width">
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
        <button class="btn btn-primary" @click="saveTask" style="margin-left: 8px;">Ekle</button>
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
  <div v-else class="page-body">
    <div class="empty-state">
      <i class="pi pi-spin pi-spinner" style="font-size: 2rem;"></i>
      <p>Yükleniyor...</p>
    </div>
  </div>
</template>
