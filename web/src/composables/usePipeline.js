import { ref } from 'vue'
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

// Shared state
const blocks = ref([])
const pipelineBlocks = ref([])
const uploadedFile = ref(null)  // Store the actual file, not just ID
const uploadedImageUrl = ref(null)  // URL for preview
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

// Upload image - just stores the file locally
function uploadImage(file) {
  uploadedFile.value = file
  // Create a URL for preview
  if (uploadedImageUrl.value) {
    URL.revokeObjectURL(uploadedImageUrl.value)
  }
  uploadedImageUrl.value = URL.createObjectURL(file)
  return file
}

// Execute pipeline - sends image together with blocks
async function executePipeline() {
  if (!uploadedFile.value) {
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
    
    // Prepare blocks as JSON
    const blocksJson = JSON.stringify(
      pipelineBlocks.value.map(block => ({
        id: block.id,
        params: block.params
      }))
    )
    
    // Send as multipart form - image sent together with blocks
    const formData = new FormData()
    formData.append('blocks', blocksJson)
    formData.append('image', uploadedFile.value)
    
    const response = await axios.post(`${API_BASE}/pipeline/run`, formData, {
      headers: { 
        'Content-Type': 'multipart/form-data'
      }
    })
    
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

// Clear uploaded image
function clearImage() {
  uploadedFile.value = null
  result.value = null
}

// Load image from URL (proxied through backend to avoid CORS)
async function loadImageFromUrl(url) {
  try {
    const proxyUrl = `${API_BASE}/pipeline/fetch-image?url=${encodeURIComponent(url)}`
    const response = await fetch(proxyUrl)
    if (!response.ok) {
      const body = await response.json().catch(() => null)
      throw new Error(body?.detail || `Server returned ${response.status}`)
    }
    const blob = await response.blob()
    const filename = url.split('/').pop().split('?')[0] || 'image.jpg'
    const file = new File([blob], filename, { type: blob.type })
    uploadImage(file)
    return file
  } catch (e) {
    error.value = `Failed to load image from URL: ${e.message}`
    throw e
  }
}

// Load default sample pipeline
async function loadDefaultPipeline() {
  const defaultBlockIds = [
    'YOLODetect',
    'ConfidenceFilter',
    'ClassFilter',
    'CropRegions',
    'SAMSegment',
    'VisualizeResults'
  ]
  
  // Clear current pipeline
  pipelineBlocks.value = []
  
  defaultBlockIds.forEach(id => {
    const block = blocks.value.find(b => b.id === id)
    if (block) {
      addBlockToPipeline(block)
    }
  })

  // Auto-load sample image
  const sampleUrl = 'https://media.istockphoto.com/id/1781481227/photo/chicken-happy-and-portrait-of-kid-on-a-farm-learning-about-sustainable-agriculture-in-the.jpg?s=612x612&w=0&k=20&c=94AMjxcf2NB6J6c5qSlTMHpOA3mysOjriLTxrYqCkWs='
  try {
    await loadImageFromUrl(sampleUrl)
  } catch (e) {
    console.warn('Failed to load sample image:', e)
  }
}

// Reset all
function resetAll() {
  blocks.value = []
  pipelineBlocks.value = []
  uploadedFile.value = null
  result.value = null
  isLoading.value = false
  error.value = null
}

export function usePipeline() {
  return {
    // State
    blocks,
    pipelineBlocks,
    uploadedFile,
    uploadedImageUrl,
    result,
    isLoading,
    error,
    
    // Actions
    fetchBlocks,
    uploadImage,
    loadImageFromUrl,
    executePipeline,
    addBlockToPipeline,
    removeBlockFromPipeline,
    updateBlockParam,
    reorderBlocks,
    clearPipeline,
    clearImage,
    resetAll,
    loadDefaultPipeline,
    
    // Helpers
    getBlockSchema
  }
}

// Helper to get block schema by ID
function getBlockSchema(blockId) {
  return blocks.value.find(b => b.id === blockId)
}
