# Enhanced File Upload System Guide

## Overview
This enhanced file upload system provides comprehensive file management with task integration, replacing the basic URL input approach with a modern file upload interface.

## New Features

### 1. Task-File Correlation
- **New Table**: `task_files` links tasks to uploaded files
- **Many-to-Many**: Tasks can have multiple files, files can be linked to multiple tasks
- **Automatic Linking**: Files are automatically linked when creating tasks

### 2. Enhanced File Management UI
- **File Selection**: Checkbox selection for bulk operations
- **Task Integration**: Add selected files to tasks with one click
- **File Preview**: Download/view files directly from interface
- **Comment Management**: Add/edit comments for each file
- **Bulk Operations**: Select all, clear selection, bulk add to task

### 3. Task File Display
- **Attached Files**: Shows files already attached to current task
- **Download Links**: Direct download links for task files
- **Remove from Task**: Remove files from specific tasks without deleting them

## Database Schema

### task_files Table
```sql
CREATE TABLE task_files (
    id VARCHAR PRIMARY KEY,
    task_id VARCHAR NOT NULL REFERENCES tasks(id),
    file_id VARCHAR NOT NULL REFERENCES uploaded_files(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### Relationships
- **Task** ↔ **TaskFile** ↔ **UploadedFile**
- **User** ↔ **UploadedFile** (one-to-many)
- **Task** ↔ **TaskFile** (one-to-many)

## API Endpoints

### File Upload (Existing)
- `POST /api/v1/uploads/upload` - Upload file
- `GET /api/v1/uploads/` - Get user's files
- `PUT /api/v1/uploads/{file_id}` - Update file comment
- `DELETE /api/v1/uploads/{file_id}` - Delete file

### Task Files (New)
- `POST /api/v1/task-files/` - Add file to task
- `GET /api/v1/task-files/task/{task_id}` - Get task files
- `GET /api/v1/task-files/file/{file_id}/tasks` - Get file's tasks
- `DELETE /api/v1/task-files/{task_file_id}` - Remove file from task
- `DELETE /api/v1/task-files/task/{task_id}/file/{file_id}` - Remove by IDs

## Frontend Components

### FileUpload Component (Enhanced)
**Props**:
- `taskId` (optional): Show task files when provided

**Events**:
- `@files-updated`: Emitted when file list changes
- `@files-added-to-task`: Emitted when files added to task

**Features**:
- File upload with progress indication
- Checkbox selection for bulk operations
- Comment editing for each file
- File deletion
- Task file management (when taskId provided)

### TaskCreateView (Updated)
**Changes**:
- Uses enhanced FileUpload component
- Handles file selection and task creation
- Maintains backward compatibility

## Usage Examples

### 1. Creating a Task with Files
```vue
<template>
  <FileUpload 
    @files-updated="handleFilesUpdated"
    ref="fileUploadComponent"
  />
</template>

<script setup>
const handleFilesUpdated = (fileUrls) => {
  // fileUrls contains URLs of uploaded files
  // These will be automatically linked to task on creation
  taskForm.attachments = fileUrls
}
</script>
```

### 2. Managing Files for Existing Task
```vue
<template>
  <FileUpload 
    :task-id="currentTaskId"
    @files-added-to-task="handleFilesAdded"
  />
</template>

<script setup>
const handleFilesAdded = (fileIds) => {
  console.log('Files added to task:', fileIds)
}
</script>
```

## Backend Integration

### Automatic File Linking
When creating a task with attachment URLs, the system automatically:
1. Creates the task
2. Parses attachment URLs
3. Finds matching uploaded files
4. Creates task-file links
5. Maintains backward compatibility

### Task Response Enhancement
Task detail responses now include:
```json
{
  "id": "task-id",
  "title": "Task title",
  // ... other task fields
  "attachments": ["url1", "url2"], // Backward compatibility
  "task_files": [
    {
      "id": "task-file-id",
      "task_id": "task-id",
      "file_id": "file-id",
      "created_at": "2024-01-01T00:00:00Z",
      "file": {
        "id": "file-id",
        "filename": "document.pdf",
        "file_url": "/uploads/uuid.pdf",
        "file_size": "1024000",
        "mime_type": "application/pdf",
        "comment": "Important document",
        "uploaded_by": "user-id",
        "created_at": "2024-01-01T00:00:00Z"
      }
    }
  ]
}
```

## File Management Workflow

### 1. Upload Files
1. User clicks "Choose Files" button
2. Files are uploaded to server
3. Files appear in "Uploaded Files" list
4. User can add comments to files

### 2. Create Task with Files
1. User fills task details
2. User selects files using checkboxes
3. User clicks "Add X file(s) to task"
4. Files are linked to task
5. Task is created with automatic file links

### 3. Manage Task Files
1. View task details
2. See "Files attached to this task" section
3. Download files or remove from task
4. Files remain in user's file library

## Benefits

### For Users
- **Better UX**: Drag-and-drop file upload vs manual URL input
- **File Library**: Reuse files across multiple tasks
- **Comments**: Add context to files
- **Bulk Operations**: Select and manage multiple files

### For Developers
- **Structured Data**: Proper database relationships
- **Scalable**: Easy to extend with more features
- **Backward Compatible**: Existing tasks continue to work
- **RESTful APIs**: Clean separation of concerns

## Testing

Run the test script to verify implementation:
```bash
cd /home/jamesbrown/Desktop/works/openmule_to_openclaw_adaptor
python test_enhanced_file_system.py
```

## Migration Path

### Phase 1: Parallel Systems
- Both URL input and file upload available
- Users can choose preferred method
- Data migration not required

### Phase 2: Gradual Transition
- Promote file upload as preferred method
- Add indicators for file-upload-created tasks
- Start deprecating URL input

### Phase 3: Full Migration
- Remove URL input option
- All tasks use file upload system
- Clean up legacy attachment handling

## Security Considerations

- **File Access**: Users can only access their own files
- **Task Access**: Only task owners can modify file attachments
- **File Validation**: Size limits and MIME type checking
- **URL Security**: Generated URLs use UUIDs to prevent guessing

## Performance Considerations

- **Lazy Loading**: Task files loaded only when needed
- **Efficient Queries**: Use joins to minimize database calls
- **File Storage**: Static file serving for downloads
- **Caching**: File metadata can be cached

## Future Enhancements

1. **File Versioning**: Keep multiple versions of files
2. **File Sharing**: Share files between users
3. **File Categories**: Organize files with tags/categories
4. **Bulk Upload**: Drag-and-drop multiple files
5. **File Preview**: Generate thumbnails for images/documents
6. **File Expiry**: Automatically delete old unused files
