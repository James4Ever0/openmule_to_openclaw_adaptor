# File Upload Debug Guide

## Issue Fixed
The FileUpload component wasn't showing uploaded files because:

1. **API Response Structure Mismatch**: Backend was returning files directly, frontend expected wrapped response
2. **Double Assignment**: Form attachments were being set twice, causing confusion

## Fixes Applied

### Backend Changes
- ✅ Updated `/uploads/` endpoint to return `{"success": true, "data": files}`
- ✅ Updated `/uploads/upload` endpoint to return `{"success": true, "data": file}`

### Frontend Changes
- ✅ Added debug logging to track API responses
- ✅ Fixed response parsing: `response.data.data || response.data`
- ✅ Removed redundant file URL assignment in handleSubmit
- ✅ Added console logging for form submission

## Testing Steps

1. **Open browser console** (F12 → Console tab)
2. **Upload a file** using the file upload button
3. **Check console logs**:
   ```
   API response: {success: true, data: [{...}]}
   Files updated: ["/uploads/uuid.pdf"]
   ```
4. **Verify file appears** in the "Uploaded Files" list
5. **Create task** and check attachments are included

## Expected Behavior

### After Upload
- File appears in "Uploaded Files" list
- Checkbox available for selection
- Comment field works
- Delete button works

### After Task Creation
- Form contains file URLs in attachments field
- Task created with file links
- Files automatically linked to task

## Debug Console Logs

If files still don't show, check these console logs:

1. **"API response:"** - Should show the backend response
2. **"Files updated:"** - Should show array of file URLs  
3. **"Submitting form with attachments:"** - Should show URLs before task creation

## Common Issues

### 1. Authentication Error
```
Error: Request failed with status code 401
```
**Solution**: Make sure you're logged in

### 2. File Size Error
```
Error: File size exceeds 50MB limit
```
**Solution**: Use smaller files or increase limit

### 3. Server Error
```
Error: Failed to save file: Permission denied
```
**Solution**: Check uploads directory permissions

### 4. CORS Error
```
Error: Network Error
```
**Solution**: Check backend CORS settings

## Quick Test Command

```bash
# Test backend directly
curl -X GET "http://localhost:3000/api/v1/uploads/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

## File Locations

- **Uploads Directory**: `backend_python/uploads/`
- **Static Files**: Served at `/uploads/` route
- **Database**: `uploaded_files` table

## Next Steps

1. **Start Backend**: `cd backend_python && python -m app.main`
2. **Start Frontend**: `cd frontend && npm run dev`
3. **Test Upload**: Upload a file and check console
4. **Create Task**: Verify files are attached to task

The system should now work correctly with proper file display and task integration!
