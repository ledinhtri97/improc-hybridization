<template>
  <div class="block-item">
    <div class="block-info">
      <span class="block-name">{{ block.name }}</span>
      <span class="block-desc">{{ block.description }}</span>
    </div>
    <button class="add-btn" @click="$emit('add', block)" title="Add to pipeline">
      +
    </button>
  </div>
</template>

<script setup>
defineProps({
  block: {
    type: Object,
    required: true
  }
})

defineEmits(['add'])
</script>

<style scoped>
.block-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.block-item:hover {
  border-color: #4a90d9;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.block-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.block-name {
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.block-desc {
  font-size: 11px;
  color: #888;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.add-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: #4a90d9;
  color: white;
  border-radius: 4px;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  flex-shrink: 0;
  margin-left: 8px;
}

.add-btn:hover {
  background: #357abd;
}
</style>
