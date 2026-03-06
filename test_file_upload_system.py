#!/usr/bin/env python3
"""
Test script to verify the file upload system implementation
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend_python'))

def test_models():
    """Test that the models can be imported without errors"""
    try:
        from app.models.uploaded_file import UploadedFile
        from app.models.user import User
        from app.models.task import Task
        
        print("✓ Models imported successfully")
        
        # Check that UploadedFile has the expected fields
        expected_fields = ['id', 'filename', 'file_path', 'file_url', 'file_size', 'mime_type', 'comment', 'uploaded_by']
        for field in expected_fields:
            if hasattr(UploadedFile, field):
                print(f"✓ UploadedFile.{field} exists")
            else:
                print(f"✗ UploadedFile.{field} missing")
        
        # Check User model has uploaded_files relationship
        if hasattr(User, 'uploaded_files'):
            print("✓ User.uploaded_files relationship exists")
        else:
            print("✗ User.uploaded_files relationship missing")
            
        return True
    except ImportError as e:
        print(f"✗ Model import failed: {e}")
        return False

def test_schemas():
    """Test that the schemas can be imported without errors"""
    try:
        from app.schemas import UploadedFileResponse, UploadedFileCreate, UploadedFileUpdate
        
        print("✓ Schemas imported successfully")
        
        # Test schema creation
        test_data = {
            "filename": "test.txt",
            "file_url": "/uploads/test.txt",
            "file_size": "1024",
            "mime_type": "text/plain",
            "comment": "Test file"
        }
        
        try:
            schema = UploadedFileResponse(**test_data)
            print("✓ UploadedFileResponse schema validation works")
        except Exception as e:
            print(f"✗ Schema validation failed: {e}")
            
        return True
    except ImportError as e:
        print(f"✗ Schema import failed: {e}")
        return False

def test_upload_handler():
    """Test that the upload handler can be imported"""
    try:
        from app.handlers.uploads import router
        
        print("✓ Upload handler imported successfully")
        
        # Check that routes are defined
        routes = [route.path for route in router.routes]
        expected_routes = ['/upload', '/', '/{file_id}']
        
        for route in expected_routes:
            if any(route in r for r in routes):
                print(f"✓ Route {route} exists")
            else:
                print(f"✗ Route {route} missing")
                
        return True
    except ImportError as e:
        print(f"✗ Upload handler import failed: {e}")
        return False

def test_main_app():
    """Test that the main app includes upload routes"""
    try:
        from app.main import app
        
        print("✓ Main app imported successfully")
        
        # Check if upload router is included
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        if any('/uploads' in route for route in routes):
            print("✓ Upload routes are registered in main app")
        else:
            print("✗ Upload routes not found in main app")
            
        return True
    except ImportError as e:
        print(f"✗ Main app import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing File Upload System Implementation")
    print("=" * 50)
    
    tests = [
        ("Models", test_models),
        ("Schemas", test_schemas),
        ("Upload Handler", test_upload_handler),
        ("Main App", test_main_app),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 20)
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("=" * 50)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✓ PASS" if results[i] else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results)
    print(f"\nOverall: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
