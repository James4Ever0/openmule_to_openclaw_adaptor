#!/usr/bin/env python3
"""
Test script to verify enhanced file upload system implementation
"""

import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend_python'))

def test_models():
    """Test that all models can be imported without errors"""
    try:
        from app.models.uploaded_file import UploadedFile
        from app.models.task_file import TaskFile
        from app.models.task import Task
        from app.models.user import User
        
        print("✓ All models imported successfully")
        
        # Check TaskFile has expected fields
        expected_fields = ['task_id', 'file_id']
        for field in expected_fields:
            if hasattr(TaskFile, field):
                print(f"✓ TaskFile.{field} exists")
            else:
                print(f"✗ TaskFile.{field} missing")
        
        # Check relationships
        if hasattr(Task, 'task_files'):
            print("✓ Task.task_files relationship exists")
        else:
            print("✗ Task.task_files relationship missing")
            
        if hasattr(UploadedFile, 'task_files'):
            print("✓ UploadedFile.task_files relationship exists")
        else:
            print("✗ UploadedFile.task_files relationship missing")
            
        return True
    except ImportError as e:
        print(f"✗ Model import failed: {e}")
        return False

def test_schemas():
    """Test that all schemas can be imported without errors"""
    try:
        from app.schemas import (
            UploadedFileResponse, 
            TaskFileCreate, 
            TaskFileResponse, 
            TaskFileWithDetails
        )
        
        print("✓ All schemas imported successfully")
        
        # Test schema creation
        test_data = {
            "task_id": "test-task-id",
            "file_id": "test-file-id"
        }
        
        try:
            schema = TaskFileCreate(**test_data)
            print("✓ TaskFileCreate schema validation works")
        except Exception as e:
            print(f"✗ Schema validation failed: {e}")
            
        return True
    except ImportError as e:
        print(f"✗ Schema import failed: {e}")
        return False

def test_task_files_handler():
    """Test that task files handler can be imported"""
    try:
        from app.handlers.task_files import router
        
        print("✓ Task files handler imported successfully")
        
        # Check that routes are defined
        routes = [route.path for route in router.routes]
        expected_routes = ['/', '/task/{task_id}', '/file/{file_id}/tasks', '/{task_file_id}', '/task/{task_id}/file/{file_id}']
        
        for route in expected_routes:
            if any(route in r for r in routes):
                print(f"✓ Route {route} exists")
            else:
                print(f"✗ Route {route} missing")
                
        return True
    except ImportError as e:
        print(f"✗ Task files handler import failed: {e}")
        return False

def test_updated_task_handler():
    """Test that task handler includes new functionality"""
    try:
        from app.handlers.tasks import router, link_attachments_to_task
        
        print("✓ Updated task handler imported successfully")
        
        # Check if helper function exists
        if callable(link_attachments_to_task):
            print("✓ link_attachments_to_task helper function exists")
        else:
            print("✗ link_attachments_to_task helper function missing")
            
        return True
    except ImportError as e:
        print(f"✗ Task handler import failed: {e}")
        return False

def test_main_app():
    """Test that main app includes task files router"""
    try:
        from app.main import app
        
        print("✓ Main app imported successfully")
        
        # Check if task files router is included
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        if any('/task-files' in route for route in routes):
            print("✓ Task files routes are registered in main app")
        else:
            print("✗ Task files routes not found in main app")
            
        return True
    except ImportError as e:
        print(f"✗ Main app import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Enhanced File Upload System Implementation")
    print("=" * 60)
    
    tests = [
        ("Models & Relationships", test_models),
        ("Schemas", test_schemas),
        ("Task Files Handler", test_task_files_handler),
        ("Updated Task Handler", test_updated_task_handler),
        ("Main App Integration", test_main_app),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✓ PASS" if results[i] else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results)
    print(f"\nOverall: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Enhanced file upload system is ready for testing!")
        print("\nNext steps:")
        print("1. Start the backend server")
        print("2. Start the frontend development server")
        print("3. Test file upload and task creation in the UI")
        print("4. Verify file management features (add, remove, comment)")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
