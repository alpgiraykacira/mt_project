<script setup>
import { ref } from 'vue'
import Toast from 'primevue/toast'

const navItems = [
  { path: '/', label: 'Dashboard', icon: 'pi pi-home' },
  { path: '/models', label: 'Mevcut Skorkartlar', icon: 'pi pi-list' },
  { path: '/development', label: 'Geliştirilen Skorkartlar', icon: 'pi pi-cog' },
]

const sidebarOpen = ref(false)
const sidebarCollapsed = ref(false)
</script>

<template>
  <Toast />
  <div class="app-layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ open: sidebarOpen, collapsed: sidebarCollapsed }">
      <button
        class="sidebar-collapse-btn"
        @click="sidebarCollapsed = !sidebarCollapsed"
        :title="sidebarCollapsed ? 'Kenar çubuğunu aç' : 'Kenar çubuğunu kapat'"
      >
        <i :class="sidebarCollapsed ? 'pi pi-angle-right' : 'pi pi-angle-left'" />
      </button>
      <div class="sidebar-header">
        <h1 v-show="!sidebarCollapsed">MT Dashboard</h1>
        <p v-show="!sidebarCollapsed">Skorkart Yönetim Platformu</p>
      </div>
      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          @click="sidebarOpen = false"
          active-class=""
          :class="{ active: $route.path === item.path || (item.path !== '/' && $route.path.startsWith(item.path)) }"
          :title="sidebarCollapsed ? item.label : ''"
        >
          <i :class="item.icon"></i>
          <span v-show="!sidebarCollapsed">{{ item.label }}</span>
        </router-link>
      </nav>
    </aside>

    <!-- Main Content -->
    <main class="main-content" :class="{ 'sidebar-is-collapsed': sidebarCollapsed }">
      <router-view />
    </main>
  </div>
</template>
