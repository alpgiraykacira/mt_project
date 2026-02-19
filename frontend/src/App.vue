<script setup>
import { ref } from 'vue'
import Toast from 'primevue/toast'

const navItems = [
  { path: '/', label: 'Dashboard', icon: 'pi pi-home' },
  { path: '/models', label: 'Mevcut Skorkartlar', icon: 'pi pi-list' },
  { path: '/development', label: 'Geliştirilen Skorkartlar', icon: 'pi pi-cog' },
]

const sidebarOpen = ref(false)
</script>

<template>
  <Toast />
  <div class="app-layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ open: sidebarOpen }">
      <div class="sidebar-header">
        <h1>MT Dashboard</h1>
        <p>Skorkart Yönetim Platformu</p>
      </div>
      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          @click="sidebarOpen = false"
          exact-active-class="active"
        >
          <i :class="item.icon"></i>
          {{ item.label }}
        </router-link>
      </nav>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>
