<template>
  <div class="app">
    <header class="header">
      <h1>🔧 Hybrid Pipeline UI</h1>
      <p class="subtitle">YOLOv8 + OpenCV + SAM</p>
    </header>
    
    <main class="main-content">
      <BlockList />
      <PipelineCanvas />
      <ResultsPanel />
    </main>
  </div>
</template>

<script setup>
import BlockList from './components/BlockList.vue'
import PipelineCanvas from './components/PipelineCanvas.vue'
import ResultsPanel from './components/ResultsPanel.vue'
</script>

<style>
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}

.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 24px;
  background: #2c3e50;
  color: white;
}

.header h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  font-size: 14px;
  opacity: 0.8;
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}
</style>
