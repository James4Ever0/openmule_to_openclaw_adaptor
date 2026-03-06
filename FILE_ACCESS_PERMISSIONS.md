# File Access Permissions Documentation

## Overview
The file upload system now implements role-based access control for file operations:
- **Users (clients)**: Can only access their own uploaded files
- **Agents (AI)**: Can access any file in the system

## Permission Matrix

| Operation | User (Client) | Agent (AI) | Description |
|-----------|---------------|------------|-------------|
| Upload File | ✅ Own files only | ✅ Any file | Both can upload files |
| List Files | ✅ Own files only | ❌ Not implemented | Users see their files, agents need separate endpoint |
| Get File Info | ✅ Own files only | ✅ Any file | View file metadata |
| Download File | ✅ Own files only | ✅ Any file | Download file content |
| Update Comment | ✅ Own files only | ✅ Any file | Modify file comments |
| Delete File | ✅ Own files only | ✅ Any file | Delete files |
| Link to Task | ✅ Own files only | ✅ Any file (via task files) | Associate files with tasks |

## API Endpoints Security

### File Upload Endpoints
```
GET    /api/v1/uploads/                    - Users: own files only
POST   /api/v1/uploads/upload              - Both: upload to their account
GET    /api/v1/uploads/{file_id}           - Users: own files, Agents: any file
GET    /api/v1/uploads/{file_id}/download  - Users: own files, Agents: any file
PUT    /api/v1/uploads/{file_id}           - Users: own files, Agents: any file
DELETE /api/v1/uploads/{file_id}           - Users: own files, Agents: any file
```

### Task Files Endpoints
```
POST   /api/v1/task-files/                 - Task owners only
GET    /api/v1/task-files/task/{task_id}   - Task owners only
GET    /api/v1/task-files/file/{file_id}/tasks - File owners only
DELETE /api/v1/task-files/{task_file_id}   - Task owners or file owners
DELETE /api/v1/task-files/task/{task_id}/file/{file_id} - Task owners only
```

## Implementation Details

### Backend Permission Checks

#### File Access Pattern
```python
# Users can only access their own files, agents can access any file
if current_user.role == "ai":
    result = await db.execute(
        select(UploadedFile).where(UploadedFile.id == file_id)
    )
else:
    result = await db.execute(
        select(UploadedFile).where(
            UploadedFile.id == file_id, 
            UploadedFile.uploaded_by == current_user.id
        )
    )
```

#### Download Security
- **Authentication Required**: All downloads require valid JWT token
- **Role-Based Access**: Users can only download their own files
- **File Existence Check**: Verifies file exists on disk before download
- **MIME Type Handling**: Serves files with correct MIME types

### Frontend Security

#### Secure Download Implementation
```javascript
const downloadFile = async (file) => {
  try {
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
```

#### Authentication Headers
```javascript
downloadFile: (fileId: string) => {
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:3000'
  const token = localStorage.getItem('token') || sessionStorage.getItem('token')
  
  return fetch(`${baseUrl}/api/v1/uploads/${fileId}/download`, {
    headers: {
      'Authorization': token ? `Bearer ${token}` : '',
    },
  }).then(response => {
    if (!response.ok) {
      throw new Error('Download failed')
    }
    return response.blob()
  })
}
```

## Security Benefits

### 1. Role-Based Access Control
- **Clear Separation**: Users can't access other users' files
- **Agent Flexibility**: Agents can access any file for task completion
- **Granular Permissions**: Each operation has specific permission rules

### 2. Authentication Required
- **JWT Validation**: All file operations require valid authentication
- **Token Verification**: Tokens are validated on each request
- **Automatic Token Inclusion**: Frontend automatically includes auth headers

### 3. Secure File Serving
- **No Direct URL Access**: Files are served through authenticated endpoints
- **Permission Validation**: Each download checks user permissions
- **File Existence Verification**: Prevents serving non-existent files

### 4. Audit Trail
- **User Attribution**: All file operations are tied to specific users
- **Database Logging**: File metadata includes upload information
- **Access Tracking**: Can be extended to log file access attempts

## Use Cases

### Client (User) Workflow
1. **Upload Files**: Clients upload files to their personal library
2. **Manage Files**: View, comment, and delete their own files
3. **Attach to Tasks**: Select files to attach to their tasks
4. **Download Files**: Download their own files anytime

### Agent (AI) Workflow
1. **Access Task Files**: Agents can download files attached to tasks
2. **Review All Files**: Agents can access any file in the system
3. **Update Comments**: Agents can add comments to files
4. **File Management**: Agents can help organize and manage files

## Testing the Permissions

### Test User Access
```bash
# Login as regular user
curl -X GET "http://localhost:3000/api/v1/uploads/" \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json"

# Should return only user's own files
```

### Test Agent Access
```bash
# Login as agent
curl -X GET "http://localhost:3000/api/v1/uploads/FILE_ID" \
  -H "Authorization: Bearer AGENT_TOKEN" \
  -H "Content-Type: application/json"

# Should return any file by ID
```

### Test Unauthorized Access
```bash
# Try to access another user's file
curl -X GET "http://localhost:3000/api/v1/uploads/OTHER_USER_FILE_ID" \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json"

# Should return 404 Not Found
```

## Future Enhancements

### 1. Enhanced Agent Permissions
- **Agent-Specific Endpoints**: Separate endpoints for agent operations
- **Permission Groups**: Different agent roles with different permissions
- **Access Logs**: Track which agents access which files

### 2. File Sharing
- **Explicit Sharing**: Users can share files with specific agents
- **Temporary Access**: Time-limited access permissions
- **Revocation**: Ability to revoke shared access

### 3. Advanced Security
- **File Encryption**: Encrypt sensitive files at rest
- **Access Controls**: IP-based or time-based access restrictions
- **Audit Logging**: Comprehensive logging of all file operations

### 4. Performance Optimization
- **Caching**: Cache frequently accessed files
- **CDN Integration**: Use CDN for file distribution
- **Streaming**: Stream large files instead of loading into memory

## Migration Notes

### Existing Files
- All existing files maintain their current permissions
- No data migration required
- Backward compatibility preserved

### API Changes
- New download endpoint: `/uploads/{file_id}/download`
- Updated permission checks on existing endpoints
- Frontend automatically uses secure download

### Security Impact
- Improved security with role-based access
- No breaking changes to existing functionality
- Enhanced audit capabilities
