import { ref } from 'vue'
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

// Shared state
const blocks = ref([])
const pipelineBlocks = ref([])
const uploadedImageId = ref(null)
const result = ref(null)
const isLoading = ref(false)
const error = ref(null)

// Fetch available blocks from API
async function fetchBlocks() {
  try {
    const response = await axios.get(`${API_BASE}/blocks`)
    blocks.value = response.data
  } catch (e) {
    error.value = e.message
    console.error('Failed to fetch blocks:', e)
  }
}

// Upload image
async function uploadImage(file) {
  try {
    isLoading.value = true
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await axios.post(`${API_BASE}/pipeline/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    uploadedImageId.value = response.data.image_id
    return response.data.image_id
  } catch (e) {
    error.value = e.message
    console.error('Failed to upload image:', e)
    throw e
  } finally {
    isLoading.value = false
  }
}

// Execute pipeline
async function executePipeline() {
  if (!uploadedImageId.value) {
    error.value = 'Please upload an image first'
    return
  }
  
  if (pipelineBlocks.value.length === 0) {
    error.value = 'Please add at least one block to the pipeline'
    return
  }
  
  try {
    isLoading.value = true
    error.value = null
    
    const request = {
      blocks: pipelineBlocks.value.map(block => ({
        id: block.id,
        params: block.params
      })),
      image_id: uploadedImageId.value
    }
    
    const response = await axios.post(`${API_BASE}/pipeline/run`, request)
    result.value = response.data
    return response.data
  } catch (e) {
    error.value = e.message
    console.error('Pipeline execution failed:', e)
    throw e
  } finally {
    isLoading.value = false
  }
}

// Add block to pipeline
function addBlockToPipeline(block) {
  // Clone block with default params
  const newBlock = {
    id: block.id,
    name: block.name,
    params: {}
  }
  
  // Set default values from schema
  block.parameters.forEach(param => {
    if (param.default !== undefined) {
      newBlock.params[param.name] = param.default
    }
  })
  
  pipelineBlocks.value.push(newBlock)
}

// Remove block from pipeline
function removeBlockFromPipeline(index) {
  pipelineBlocks.value.splice(index, 1)
}

// Update block parameter
function updateBlockParam(blockIndex, paramName, value) {
  pipelineBlocks.value[blockIndex].params[paramName] = value
}

// Reorder pipeline blocks
function reorderBlocks(newOrder) {
  pipelineBlocks.value = newOrder
}

// Clear pipeline
function clearPipeline() {
  pipelineBlocks.value = []
  result.value = null
  error.value = null
}

// Reset all
function resetAll() {
  blocks.value = []
  pipelineBlocks.value = []
  uploadedImageId.value = null
  result.value = null
  isLoading.value = false
  error.value = null
}

export function usePipeline() {
  return {
    // State
    blocks,
    pipelineBlocks,
    uploadedImageId,
    result,
    isLoading,
    error,
    
    // Actions
    fetchBlocks,
    uploadImage,
    executePipeline,
    addBlockToPipeline,
    removeBlockFromPipeline,
    updateBlockParam,
    reorderBlocks,
    clearPipeline,
    resetAll
  }
}
