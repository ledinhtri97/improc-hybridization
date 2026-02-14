<template>
  <div class="pipeline-canvas">
    <h3>Pipeline</h3>
    
    <div class="pipeline-content">
      <div v-if="pipelineBlocks.length === 0" class="empty-state">
        Click blocks on the left to add them to the pipeline
      </div>
      
      <draggable 
        v-else
        v-model="localBlocks" 
        item-key="id"
        handle=".drag-handle"
        ghost-class="ghost"
        @end="onReorder"
      >
        <template #item="{ element, index }">
          <div class="pipeline-block">
            <div class="drag-handle">⋮⋮</div>
            <div class="block-content">
              <div class="block-header">
                <span class="block-index">{{ index + 1 }}</span>
                <span class="block-name">{{ element.name }}</span>
                <button class="remove-btn" @click="removeBlock(index)">×</button>
              </div>
              
              <!-- Parameters -->
              <div v-if="element.params && Object.keys(element.params).length > 0" class="block-params">
                <div 
                  v-for="(value, key) in element.params" 
                  :key="key" 
                  class="param-row"
                >
                  <label :for="`${element.id}-${key}`">{{ key }}:</label>
                  <input
                    v-if="getParamType(element.id, key) === 'array'"
                    :id="`${element.id}-${key}`"
                    type="text"
                    :value="element.params[key].join(',')"
                    @change="handleArrayParam(index, key, $event.target.value)"
                    placeholder="e.g. 0,1,2"
                  />
                  <input
                    v-else-if="getParamType(element.id, key) === 'string'"
                    :id="`${element.id}-${key}`"
                    type="text"
                    v-model="element.params[key]"
                    @change="updateParam(index, key, element.params[key])"
                  />
                  <input
                    v-else-if="getParamType(element.id, key) === 'number'"
                    :id="`${element.id}-${key}`"
                    type="number"
                    step="any"
                    v-model.number="element.params[key]"
                    @change="updateParam(index, key, element.params[key])"
                  />
                  <input
                    v-else
                    :id="`${element.id}-${key}`"
                    type="text"
                    v-model="element.params[key]"
                    @change="updateParam(index, key, element.params[key])"
                  />
                </div>
              </div>
            </div>
          </div>
        </template>
      </draggable>
    </div>
    
    <!-- Execute Button -->
    <div class="pipeline-actions">
      <button 
        class="execute-btn" 
        @click="execute"
        :disabled="isLoading || pipelineBlocks.length === 0"
      >
        {{ isLoading ? 'Running...' : '▶ Execute Pipeline' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import draggable from 'vuedraggable'
import { usePipeline } from '../composables/usePipeline'

const { 
  pipelineBlocks, 
  executePipeline, 
  removeBlockFromPipeline, 
  updateBlockParam,
  reorderBlocks,
  isLoading,
  result,
  getBlockSchema
} = usePipeline()

const localBlocks = ref([])

// Sync local blocks with pipeline
watch(pipelineBlocks, (newVal) => {
  localBlocks.value = [...newVal]
}, { deep: true, immediate: true })

function removeBlock(index) {
  removeBlockFromPipeline(index)
}

function updateParam(index, paramName, value) {
  updateBlockParam(index, paramName, value)
}

function handleArrayParam(index, paramName, value) {
  // Parse comma-separated values into array of integers
  const arr = value.split(',')
    .map(s => parseInt(s.trim(), 10))
    .filter(n => !isNaN(n))
  updateBlockParam(index, paramName, arr)
}

function onReorder() {
  reorderBlocks(localBlocks.value)
}

function getParamType(blockId, paramName) {
  // Find parameter type from block schema
  const schema = getBlockSchema(blockId)
  if (!schema) return 'text'
  
  const param = schema.parameters.find(p => p.name === paramName)
  return param ? param.type : 'text'
}

async function execute() {
  await executePipeline()
}
</script>

<style scoped>
.pipeline-canvas {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
  background: #fff;
  overflow: hidden;
}

h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #333;
}

.pipeline-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
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

.pipeline-block {
  display: flex;
  align-items: flex-start;
  margin-bottom: 12px;
  background: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.drag-handle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  background: #e9ecef;
  color: #666;
  cursor: grab;
  font-size: 14px;
  user-select: none;
}

.drag-handle:active {
  cursor: grabbing;
}

.block-content {
  flex: 1;
  padding: 12px;
}

.block-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.block-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #4a90d9;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: bold;
}

.block-name {
  font-weight: 600;
  font-size: 14px;
  color: #333;
  flex: 1;
}

.remove-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: #999;
  font-size: 18px;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-btn:hover {
  background: #ff4757;
  color: white;
}

.block-params {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #eee;
}

.param-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.param-row label {
  font-size: 12px;
  color: #666;
  min-width: 80px;
}

.param-row input {
  flex: 1;
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 12px;
}

.param-row input:focus {
  outline: none;
  border-color: #4a90d9;
}

.ghost {
  opacity: 0.5;
  background: #c8ebfb;
}

.pipeline-actions {
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.execute-btn {
  width: 100%;
  padding: 12px 24px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.execute-btn:hover:not(:disabled) {
  background: #218838;
}

.execute-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
