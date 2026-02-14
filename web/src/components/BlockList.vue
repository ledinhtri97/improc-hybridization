<template>
  <div class="block-list">
    <h3>Available Blocks</h3>
    
    <div v-if="loading" class="loading">Loading blocks...</div>
    
    <div v-else class="blocks-container">
      <div 
        v-for="category in categories" 
        :key="category.name" 
        class="category-section"
      >
        <h4 class="category-title">{{ category.name }}</h4>
        <div class="category-blocks">
          <BlockItem
            v-for="block in category.blocks"
            :key="block.id"
            :block="block"
            @add="addBlock"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { usePipeline } from '../composables/usePipeline'
import BlockItem from './BlockItem.vue'

const { blocks, fetchBlocks, addBlockToPipeline, isLoading } = usePipeline()

const loading = computed(() => isLoading.value && blocks.value.length === 0)

// Group blocks by category
const categories = computed(() => {
  const grouped = {}
  
  blocks.value.forEach(block => {
    const cat = block.category || 'other'
    if (!grouped[cat]) {
      grouped[cat] = {
        name: cat.charAt(0).toUpperCase() + cat.slice(1),
        blocks: []
      }
    }
    grouped[cat].blocks.push(block)
  })
  
  return Object.values(grouped)
})

function addBlock(block) {
  addBlockToPipeline(block)
}

// Fetch blocks on mount
fetchBlocks()
</script>

<style scoped>
.block-list {
  width: 280px;
  padding: 16px;
  background: #f8f9fa;
  border-right: 1px solid #e0e0e0;
  overflow-y: auto;
  height: 100%;
}

h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #333;
}

.loading {
  color: #666;
  font-style: italic;
}

.category-section {
  margin-bottom: 20px;
}

.category-title {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #555;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.category-blocks {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
