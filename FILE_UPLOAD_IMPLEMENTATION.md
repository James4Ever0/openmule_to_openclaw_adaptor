# File Upload System Implementation

## Overview
This implementation replaces the URL input textarea with a comprehensive file upload system that manages uploaded files in a separate database table while maintaining compatibility with the existing attachment system.

## Backend Changes

### 1. New Database Model
- **File**: `backend_python/app/models/uploaded_file.py`
- **Table**: `uploaded_files`
- **Fields**:
  - `id`: Primary key (UUID)
  - `filename`: Original filename
  - `file_path`: Storage path on server
  - `file_url`: Public URL for access
  - `file_size`: File size in bytes
  - `mime_type`: MIME type
  - `comment`: Optional comment
  - `uploaded_by`: Foreign key to users.id
  - `created_at`, `updated_at`: Timestamps

### 2. Updated Models
- **File**: `backend_python/app/models/user.py`
- **Added**: `uploaded_files` relationship to User model

### 3. New Schemas
- **File**: `backend_python/app/schemas.py`
- **Added**: `UploadedFileBase`, `UploadedFileCreate`, `UploadedFileResponse`, `UploadedFileUpdate`

### 4. Upload Handler
- **File**: `backend_python/app/handlers/uploads.py`
- **Endpoints**:
  - `POST /api/v1/uploads/upload` - Upload file
  - `GET /api/v1/uploads/` - Get user's files
  - `GET /api/v1/uploads/{file_id}` - Get file info
  - `PUT /api/v1/uploads/{file_id}` - Update file comment
  - `DELETE /api/v1/uploads/{file_id}` - Delete file

### 5. Main App Updates
- **File**: `backend_python/app/main.py`
- **Added**: Upload router registration and static file serving
- **Static Files**: Serves files from `/uploads` directory

## Frontend Changes

### 1. API Integration
- **File**: `frontend/src/lib/api.ts`
- **Added**: `uploadsApi` with methods for all upload operations

### 2. File Upload Component
- **File**: `frontend/src/components/FileUpload.vue`
- **Features**:
  - Multiple file selection
  - Drag & drop support (via file input)
  - File size validation (50MB limit)
  - Comment management for each file
  - File preview/download
  - File deletion
  - Real-time upload progress

### 3. Updated Task Creation
- **File**: `frontend/src/views/TaskCreateView.vue`
- **Replaced**: Textarea for attachment URLs with FileUpload component
- **Maintained**: Compatibility with existing attachment data structure

## Key Features

### File Management
- **Upload**: Users can upload multiple files simultaneously
- **Comments**: Each file can have an optional comment
- **Delete**: Users can delete their uploaded files
- **View**: Files can be viewed/downloaded via public URLs

### Security & Validation
- **Authentication**: All upload operations require authentication
- **File Size**: 50MB limit per file
- **Ownership**: Users can only manage their own files
- **MIME Type**: Automatic MIME type detection

### Storage
- **Location**: Files stored in `uploads/` directory
- **Naming**: Unique UUID-based filenames to prevent collisions
- **URLs**: Public URLs served via `/uploads/{filename}`

## Database Schema

### uploaded_files table
```sql
CREATE TABLE uploaded_files (
    id VARCHAR PRIMARY KEY,
    filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    file_url VARCHAR NOT NULL,
    file_size VARCHAR NOT NULL,
    mime_type VARCHAR NOT NULL,
    comment TEXT,
    uploaded_by VARCHAR NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## API Endpoints

### Upload File
```
POST /api/v1/uploads/upload
Content-Type: multipart/form-data
Body: file (File), comment (optional string)
```

### Get User Files
```
GET /api/v1/uploads/
Authorization: Bearer <token>
```

### Update File Comment
```
PUT /api/v1/uploads/{file_id}
Authorization: Bearer <token>
Body: { "comment": "new comment" }
```

### Delete File
```
DELETE /api/v1/uploads/{file_id}
Authorization: Bearer <token>
```

## Usage Example

### Frontend Component Usage
```vue
<template>
  <FileUpload 
    @files-updated="handleFilesUpdated"
    ref="fileUploadComponent"
  />
</template>

<script setup>
import FileUpload from '@/components/FileUpload.vue'

const handleFilesUpdated = (fileUrls) => {
  // fileUrls contains array of uploaded file URLs
  console.log('Uploaded files:', fileUrls)
}
</script>
```

## Compatibility

### Existing Task System
- **No Changes**: The existing `tasks.attachments` JSON field remains unchanged
- **Backward Compatible**: Tasks created with URL input still work
- **Seamless**: New file upload system populates the same attachment field

### Migration Path
- **Optional**: Existing users can continue using URL input if needed
- **Gradual**: System supports both methods simultaneously
- **Future**: URL input can be deprecated when ready

## Benefits

1. **Better UX**: File upload is more intuitive than manual URL input
2. **File Management**: Users can manage their uploaded files centrally
3. **Comments**: Add context to files with optional comments
4. **Security**: Controlled file access with authentication
5. **Storage**: Efficient file storage with unique naming
6. **Scalability**: Separate table allows for future file management features

## Testing

Run the test script to verify implementation:
```bash
cd /home/jamesbrown/Desktop/works/openmule_to_openclaw_adaptor
python test_file_upload_system.py
```

## Next Steps

1. **Database Migration**: Run the application to create the new table
2. **Testing**: Test file upload functionality in the UI
3. **Documentation**: Update user documentation
4. **Monitoring**: Add file upload monitoring and cleanup if needed
