<template>
  <div class="file-upload-container">
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        File Attachments
      </label>
      
      <!-- Upload Button -->
      <div class="flex items-center space-x-4">
        <input
          ref="fileInput"
          type="file"
          multiple
          @change="handleFileSelect"
          class="hidden"
        />
        <button
          type="button"
          @click="$refs.fileInput.click()"
          :disabled="uploading"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="uploading">Uploading...</span>
          <span v-else>📁 Choose Files</span>
        </button>
        
        <span class="text-sm text-gray-500">
          Max file size: 50MB
        </span>
      </div>
    </div>

    <!-- Uploaded Files List -->
    <div v-if="uploadedFiles.length > 0 && !directAttach" class="space-y-2">
      <h4 class="text-sm font-medium text-gray-700">Uploaded Files:</h4>
      <div class="border border-gray-200 rounded-md divide-y divide-gray-200">
        <div
          v-for="file in uploadedFiles"
          :key="file.id"
          class="p-3 flex items-center justify-between hover:bg-gray-50"
        >
          <div class="flex-1">
            <div class="flex items-center space-x-3">
              <input
                type="checkbox"
                :checked="selectedFileIds.includes(file.id)"
                @change="toggleFileSelection(file.id)"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="text-sm font-medium text-gray-900">{{ file.filename }}</span>
              <span class="text-xs text-gray-500">({{ formatFileSize(file.file_size) }})</span>
            </div>
            
            <!-- Comment Input -->
            <div class="mt-2 flex items-center space-x-2">
              <input
                v-model="file.comment"
                @blur="updateFileComment(file)"
                type="text"
                placeholder="Add comment..."
                class="flex-1 text-sm px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
              <button
                type="button"
                @click="updateFileComment(file)"
                class="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
              >
                Save
              </button>
            </div>
          </div>
          
          <!-- File Actions -->
          <div class="flex items-center space-x-2 ml-4">
            <button
              type="button"
              @click="downloadFile(file)"
              class="text-blue-600 hover:text-blue-800 text-sm"
            >
              Download
            </button>
            <button
              type="button"
              @click="deleteFile(file)"
              class="text-red-600 hover:text-red-800 text-sm"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
      
      <!-- Action Buttons -->
      <div class="mt-3 flex items-center space-x-3">
        <button
          type="button"
          v-if="selectedFileIds.length > 0"
          @click="addSelectedFilesToTask"
          :disabled="linkingToTask"
          class="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-50"
        >
          {{ linkingToTask ? 'Adding...' : `Add ${selectedFileIds.length} file(s) to task` }}
        </button>
        
        <button
          type="button"
          @click="selectAllFiles"
          class="text-sm text-blue-600 hover:text-blue-800"
        >
          Select All
        </button>
        
        <button
          type="button"
          @click="clearSelection"
          class="text-sm text-gray-600 hover:text-gray-800"
        >
          Clear Selection
        </button>
      </div>
    </div>

    <!-- Direct Task Attachments -->
    <div v-if="directAttach" class="space-y-2">
      <h4 class="text-sm font-medium text-gray-700">Task Attachments:</h4>
      <div class="border border-gray-200 rounded-md divide-y divide-gray-200">
        <div
          v-for="taskFile in taskFiles"
          :key="taskFile.id"
          class="p-3 flex items-center justify-between hover:bg-gray-50"
        >
          <div class="flex-1">
            <div class="flex items-center space-x-3">
              <input
                type="checkbox"
                :checked="selectedFileIds.includes(taskFile.file.id)"
                @change="toggleFileSelection(taskFile.file.id)"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="text-sm font-medium text-gray-900">{{ taskFile.file.filename }}</span>
              <span class="text-xs text-gray-500">({{ formatFileSize(taskFile.file.file_size) }})</span>
            </div>
            
            <!-- Comment Input -->
            <div class="mt-2 flex items-center space-x-2">
              <input
                v-model="taskFile.file.comment"
                @blur="updateFileComment(taskFile.file)"
                type="text"
                placeholder="Add comment for this file..."
                class="flex-1 text-sm px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
              <button
                type="button"
                @click="updateFileComment(taskFile.file)"
                class="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
              >
                Save
              </button>
            </div>
          </div>
          
          <!-- File Actions -->
          <div class="flex items-center space-x-2 ml-4">
            <button
              type="button"
              @click="downloadFile(taskFile.file)"
              class="text-blue-600 hover:text-blue-800 text-sm"
            >
              Download
            </button>
            <button
              type="button"
              @click="deleteFile(taskFile.file)"
              class="text-red-600 hover:text-red-800 text-sm"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
      
      <!-- Action Buttons -->
      <div class="mt-3 flex items-center space-x-3">
        <button
          type="button"
          v-if="selectedFileIds.length > 0"
          @click="removeSelectedFiles"
          :disabled="removingFiles"
          class="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 disabled:opacity-50"
        >
          {{ removingFiles ? 'Removing...' : `Remove ${selectedFileIds.length} file(s)` }}
        </button>
        
        <button
          type="button"
          @click="selectAllFiles"
          class="text-sm text-blue-600 hover:text-blue-800"
        >
          Select All
        </button>
        
        <button
          type="button"
          @click="clearSelection"
          class="text-sm text-gray-600 hover:text-gray-800"
        >
          Clear Selection
        </button>
      </div>
    </div>

    <!-- Task Files (when taskId is provided and not in direct attach mode) -->
     
    <div v-if="taskId && taskFiles.length > 0 && !directAttach" class="mt-6">
      <h4 class="text-sm font-medium text-gray-700 mb-3">Files attached to this task:</h4>
      <div class="border border-gray-200 rounded-md divide-y divide-gray-200">
        <div
          v-for="taskFile in taskFiles"
          :key="taskFile.id"
          class="p-3 flex items-center justify-between hover:bg-gray-50"
        >
          <div class="flex-1">
            <div class="flex items-center space-x-3">
              <span class="text-sm font-medium text-gray-900">{{ taskFile.file.filename }}</span>
              <span class="text-xs text-gray-500">({{ formatFileSize(taskFile.file.file_size) }})</span>
              <span v-if="taskFile.file.comment" class="text-xs text-gray-600 italic">"{{ taskFile.file.comment }}"</span>
            </div>
          </div>
          
          <!-- File Actions -->
          <div class="flex items-center space-x-2 ml-4">
            <button
              type="button"
              @click="downloadFile(taskFile.file)"
              class="text-blue-600 hover:text-blue-800 text-sm"
            >
              Download
            </button>
            <button
              type="button"
              @click="removeFileFromTask(taskFile)"
              class="text-red-600 hover:text-red-800 text-sm"
            >
              Remove from Task
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Upload Progress -->
    <div v-if="uploading" class="mt-2">
      <div class="flex items-center space-x-2">
        <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
        <span class="text-sm text-gray-600">Uploading files...</span>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="mt-2 bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-md text-sm">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { uploadsApi, taskFilesApi } from '@/lib/api'

const props = defineProps({
  taskId: {
    type: String,
    default: null
  },
  directAttach: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['files-updated', 'files-added-to-task', 'task-files-updated'])

const fileInput = ref(null)
const uploadedFiles = ref([])
const taskFiles = ref([])
const selectedFileIds = ref([])
const uploading = ref(false)
const linkingToTask = ref(false)
const removingFiles = ref(false)
const error = ref('')

// Load existing files on component mount
onMounted(async () => {
  if (props.taskId) {
    await loadTaskFiles()
  }
  if (!props.directAttach) {
    await loadUserFiles()
  }
})

// Watch for taskId changes
watch(() => props.taskId, async (newTaskId) => {
  if (newTaskId) {
    await loadTaskFiles()
  } else {
    taskFiles.value = []
  }
})

// Watch for direct attach mode changes
watch(() => props.directAttach, async (newDirectAttach) => {
  if (newDirectAttach) {
    // In direct attach mode, show task files as uploaded files for selection
    uploadedFiles.value = taskFiles.value.map(tf => tf.file)
  } else {
    // Load user files when not in direct attach mode
    await loadUserFiles()
  }
})

const loadUserFiles = async () => {
  try {
    const response = await uploadsApi.getUserFiles()
    console.log('API response:', response.data) // Debug log
    uploadedFiles.value = response.data.data || response.data || []
    emitFilesUpdated()
  } catch (err) {
    console.error('Failed to load user files:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to load files'
  }
}

const loadTaskFiles = async () => {
  if (!props.taskId) return
  
  try {
    const response = await taskFilesApi.getTaskFiles(props.taskId)
    taskFiles.value = response.data || []
    
    // If in direct attach mode, update uploadedFiles to show task files
    if (props.directAttach) {
      uploadedFiles.value = taskFiles.value.map(tf => tf.file)
    }
  } catch (err) {
    console.error('Failed to load task files:', err)
  }
}

const handleFileSelect = async (event) => {
  const files = Array.from(event.target.files)
  if (files.length === 0) return

  uploading.value = true
  error.value = ''

  try {
    // Upload each file
    for (const file of files) {
      // Check file size (50MB limit)
      if (file.size > 50 * 1024 * 1024) {
        throw new Error(`File "${file.name}" exceeds 50MB limit`)
      }

      const response = await uploadsApi.uploadFile(file, '')
      console.log('Upload response:', response.data) // Debug log
      
      // If direct attach mode and taskId is provided, attach file to task immediately
      if (props.directAttach && props.taskId && response.data.data) {
        await taskFilesApi.addFileToTask(props.taskId, response.data.data.id)
      }
    }

    // Reload files list
    await loadUserFiles()
    if (props.taskId) {
      await loadTaskFiles()
    }
    
    // Clear file input
    event.target.value = ''
    
  } catch (err) {
    console.error('Upload error:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to upload files'
  } finally {
    uploading.value = false
  }
}

const toggleFileSelection = (fileId) => {
  const index = selectedFileIds.value.indexOf(fileId)
  if (index > -1) {
    selectedFileIds.value.splice(index, 1)
  } else {
    selectedFileIds.value.push(fileId)
  }
}

const selectAllFiles = () => {
  if (props.directAttach) {
    selectedFileIds.value = taskFiles.value.map(taskFile => taskFile.file.id)
  } else {
    selectedFileIds.value = uploadedFiles.value.map(file => file.id)
  }
}

const clearSelection = () => {
  selectedFileIds.value = []
}

const removeSelectedFiles = async () => {
  if (selectedFileIds.value.length === 0) return
  
  if (!confirm(`Are you sure you want to remove ${selectedFileIds.value.length} file(s) from this task?`)) {
    return
  }

  removingFiles.value = true
  error.value = ''

  try {
    // Remove each selected file from task
    for (const fileId of selectedFileIds.value) {
      // Find the task file entry for this file
      const taskFile = taskFiles.value.find(tf => tf.file.id === fileId)
      if (taskFile) {
        await taskFilesApi.removeFileFromTask(taskFile.id)
      }
    }

    // Reload task files
    await loadTaskFiles()
    
    // Clear selection
    selectedFileIds.value = []
    
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to remove files from task'
  } finally {
    removingFiles.value = false
  }
}

const removeFileFromTask = async (taskFile) => {
  if (!confirm(`Are you sure you want to remove "${taskFile.file.filename}" from this task?`)) {
    return
  }

  try {
    await taskFilesApi.removeFileFromTask(taskFile.id)
    taskFiles.value = taskFiles.value.filter(tf => tf.id !== taskFile.id)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to remove file from task'
  }
}

const updateFileComment = async (file) => {
  try {
    await uploadsApi.updateFileComment(file.id, file.comment || '')
    console.log(`Comment saved for file "${file.filename}": "${file.comment}"`)
  } catch (err) {
    console.error('Failed to update comment:', err)
  }
}

const deleteFile = async (file) => {
  if (!confirm(`Are you sure you want to delete "${file.filename}"? This will remove it from all tasks.`)) {
    return
  }

  try {
    await uploadsApi.deleteFile(file.id)
    
    // Remove from uploadedFiles
    uploadedFiles.value = uploadedFiles.value.filter(f => f.id !== file.id)
    
    // In direct attach mode, also remove from taskFiles and refresh
    if (props.directAttach) {
      taskFiles.value = taskFiles.value.filter(tf => tf.file.id !== file.id)
      // Reload task files to ensure sync with server
      if (props.taskId) {
        await loadTaskFiles()
      }
    }
    
    emitFilesUpdated()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to delete file'
  }
}

const downloadFile = async (file) => {
  try {
    // Use the secure download API instead of direct file URL
    const blob = await uploadsApi.downloadFile(file.id)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = file.filename
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (err) {
    console.error('Download failed:', err)
    error.value = 'Failed to download file'
  }
}

const getFileUrl = (fileUrl) => {
  // Don't convert to absolute URL - keep relative for display purposes
  // The actual download uses the secure API, not this URL
  return fileUrl
}

const formatFileSize = (sizeStr) => {
  const size = parseInt(sizeStr)
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB'
  return (size / (1024 * 1024)).toFixed(1) + ' MB'
}

const emitFilesUpdated = () => {
  const fileUrls = uploadedFiles.value.map(file => getFileUrl(file.file_url))
  emit('files-updated', fileUrls)
}

// Expose methods
defineExpose({
  getFileUrls: () => {
    return uploadedFiles.value.map(file => getFileUrl(file.file_url))
  },
  getSelectedFileIds: () => selectedFileIds.value,
  addSelectedFilesToTask: !props.directAttach ? addSelectedFilesToTask : null,
  removeSelectedFiles: props.directAttach ? removeSelectedFiles : null
})
</script>

