<template>
  <div class="results-panel">
    <h3>Results</h3>
    
    <!-- Image Upload -->
    <div class="upload-section">
      <input 
        type="file" 
        accept="image/*" 
        @change="onFileChange"
        id="image-upload"
        class="file-input"
      />
      <label for="image-upload" class="file-label">
        📁 {{ uploadedImageId ? 'Change Image' : 'Upload Image' }}
      </label>
      <span v-if="uploadedImageId" class="uploaded-badge">✓ Uploaded</span>
    </div>
    
    <!-- Results -->
    <div v-if="result" class="result-content">
      <div class="result-header">
        <span :class="['status-badge', result.status]">{{ result.status }}</span>
      </div>
      
      <!-- Text Result -->
      <div v-if="result.data?.text" class="text-result">
        <pre>{{ result.data.text }}</pre>
      </div>
      
      <!-- Image Result -->
      <div v-if="result.type === 'image' && result.data?.image_url" class="image-result">
        <img :src="result.data.image_url" alt="Pipeline result" />
      </div>
      
      <!-- Error Message -->
      <div v-if="result.message" class="error-message">
        {{ result.message }}
      </div>
    </div>
    
    <!-- Error State -->
    <div v-if="error" class="error-state">
      {{ error }}
    </div>
    
    <!-- No Results -->
    <div v-if="!result && !error" class="empty-state">
      Execute pipeline to see results
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { usePipeline } from '../composables/usePipeline'

const { 
  result, 
  error, 
  uploadedImageId, 
  uploadImage,
  isLoading 
} = usePipeline()

async function onFileChange(event) {
  const file = event.target.files[0]
  if (file) {
    await uploadImage(file)
  }
}
</script>

<style scoped>
.results-panel {
  width: 320px;
  padding: 16px;
  background: #f8f9fa;
  border-left: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #333;
}

.upload-section {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.file-input {
  display: none;
}

.file-label {
  display: inline-block;
  padding: 8px 16px;
  background: #4a90d9;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.file-label:hover {
  background: #357abd;
}

.uploaded-badge {
  display: inline-block;
  margin-left: 8px;
  color: #28a745;
  font-size: 12px;
}

.result-content {
  flex: 1;
}

.result-header {
  margin-bottom: 12px;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.completed {
  background: #d4edda;
  color: #155724;
}

.status-badge.failed {
  background: #f8d7da;
  color: #721c24;
}

.text-result {
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 12px;
}

.text-result pre {
  margin: 0;
  font-size: 12px;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-word;
}

.image-result {
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 8px;
}

.image-result img {
  width: 100%;
  height: auto;
  border-radius: 4px;
}

.error-message {
  margin-top: 12px;
  padding: 12px;
  background: #f8d7da;
  color: #721c24;
  border-radius: 6px;
  font-size: 13px;
}

.error-state {
  padding: 12px;
  background: #f8d7da;
  color: #721c24;
  border-radius: 6px;
  font-size: 13px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #999;
  font-style: italic;
  border: 2px dashed #ddd;
  border-radius: 8px;
}
</style>
