<template>
  <el-config-provider :locale="zhCn">
    <ChatView />
  </el-config-provider>
</template>

<script setup lang="ts">
import ChatView from './views/ChatView.vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
</script>

<style>
body { margin: 0; padding: 0; height: 100vh; }
#app { height: 100vh; }
</style>