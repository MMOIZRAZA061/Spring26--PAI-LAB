"""
Test script to validate the Vehicle Detection System installation
Run this to check if everything is properly installed and working
"""
import sys
from pathlib import Path


def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    
    packages = {
        'cv2': 'OpenCV',
        'torch': 'PyTorch',
        'ultralytics': 'YOLOv8',
        'numpy': 'NumPy',
        'PIL': 'Pillow'
    }
    
    failed = []
    
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"  ✓ {name:20} imported successfully")
        except ImportError:
            print(f"  ✗ {name:20} NOT FOUND")
            failed.append(package)
    
    return len(failed) == 0, failed


def test_detector():
    """Test if detector can be initialized"""
    print("\nTesting detector initialization...")
    
    try:
        from vehicle_detector import VehicleDetector
        import config
        
        print(f"  Creating detector with model: {config.MODEL_NAME}")
        print("  This may take a minute on first run (downloading model)...")
        
        detector = VehicleDetector(config.MODEL_NAME, config.CONFIDENCE_THRESHOLD)
        print("  ✓ Detector initialized successfully")
        
        return True, detector
    
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False, None


def test_file_structure():
    """Test if required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        'main.py',
        'gui.py',
        'vehicle_detector.py',
        'config.py',
        'requirements.txt',
        'README.md'
    ]
    
    missing = []
    
    for file in required_files:
        if Path(file).exists():
            print(f"  ✓ {file:25} found")
        else:
            print(f"  ✗ {file:25} NOT FOUND")
            missing.append(file)
    
    return len(missing) == 0, missing


def test_gpu():
    """Test GPU availability"""
    print("\nTesting GPU availability...")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            print(f"  ✓ CUDA is available")
            print(f"    GPU: {torch.cuda.get_device_name(0)}")
            print(f"    Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
            return True
        else:
            print(f"  ℹ CUDA not available - will use CPU (slower)")
            return False
    
    except Exception as e:
        print(f"  ✗ Error checking GPU: {str(e)}")
        return False


def test_create_folders():
    """Create necessary folders"""
    print("\nSetting up folders...")
    
    try:
        Path('inputs').mkdir(exist_ok=True)
        Path('outputs').mkdir(exist_ok=True)
        print("  ✓ Created 'inputs' and 'outputs' folders")
        return True
    except Exception as e:
        print(f"  ✗ Error creating folders: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("VEHICLE DETECTION SYSTEM - INSTALLATION TEST")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Files
    tests_total += 1
    success, missing = test_file_structure()
    if success:
        tests_passed += 1
    else:
        print(f"\n  Missing files: {', '.join(missing)}")
    
    # Test 2: Imports
    tests_total += 1
    success, failed = test_imports()
    if success:
        tests_passed += 1
    else:
        print(f"\n  Failed to import: {', '.join(failed)}")
        print(f"  Run: pip install -r requirements.txt")
    
    # Test 3: GPU
    tests_total += 1
    test_gpu()  # This one is informational
    tests_passed += 1
    
    # Test 4: Folders
    tests_total += 1
    success = test_create_folders()
    if success:
        tests_passed += 1
    
    # Test 5: Detector
    tests_total += 1
    success, detector = test_detector()
    if success:
        tests_passed += 1
    else:
        print(f"\n  First run downloads YOLOv8 model (~100-200MB)")
        print(f"  Check internet connection and disk space")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {tests_passed}/{tests_total} passed")
    print("=" * 60)
    
    if tests_passed == tests_total:
        print("\n✓ All tests passed! System is ready to use.")
        print("\nUsage:")
        print("  GUI:         python gui.py")
        print("  CLI:         python main.py <file>")
        print("  Easy Mode:   Double-click run.bat (Windows)")
        return 0
    else:
        print("\n✗ Some tests failed. Please:")
        print("  1. Check network connection")
        print("  2. Run: pip install -r requirements.txt")
        print("  3. Run this test again")
        return 1


if __name__ == "__main__":
    sys.exit(main())
