"""
PyTorch & Detection System Troubleshooting Script
Run this to diagnose and fix common issues
"""
import sys
import subprocess


def diagnose_pytorch():
    """Diagnose PyTorch installation"""
    print("=" * 60)
    print("PYTORCH DIAGNOSTICS")
    print("=" * 60)
    
    try:
        import torch
        print(f"✓ PyTorch version: {torch.__version__}")
        print(f"✓ Python version: {sys.version}")
        
        # CUDA check
        print(f"\n📊 CUDA Status:")
        print(f"  Available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"  Device: {torch.cuda.get_device_name(0)}")
            print(f"  Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        else:
            print(f"  Status: Not available (will use CPU)")
        
        return True
    except ImportError:
        print("✗ PyTorch NOT installed")
        return False


def fix_pytorch():
    """Fix PyTorch installation"""
    print("\n" + "=" * 60)
    print("PYTORCH INSTALLATION FIX")
    print("=" * 60)
    
    print("\nOption 1: Fresh Install (Recommended)")
    print("  pip uninstall torch torchvision torchaudio -y")
    print("  pip install torch torchvision torchaudio")
    
    print("\nOption 2: Quick Upgrade")
    print("  pip install --upgrade torch torchvision torchaudio")
    
    print("\nOption 3: Include ultralytics")
    print("  pip install --upgrade ultralytics torch torchvision")
    
    print("\nRunning Option 3 now...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", 
                             "ultralytics", "torch", "torchvision"])
        print("\n✓ Installation complete!")
        return True
    except Exception as e:
        print(f"✗ Installation failed: {str(e)}")
        return False


def test_detection():
    """Test if detection works"""
    print("\n" + "=" * 60)
    print("DETECTION TEST")
    print("=" * 60)
    
    try:
        print("Importing modules...")
        from vehicle_detector import VehicleDetector
        import config
        import numpy as np
        import cv2
        
        print("✓ Imports successful")
        
        print("Initializing detector...")
        detector = VehicleDetector("yolov8n.pt", 0.5)  # Use nano model for testing
        print("✓ Detector initialized")
        
        print("Creating test frame...")
        # Create a dummy frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.rectangle(test_frame, (100, 100), (300, 300), (0, 255, 0), 2)
        
        print("Running detection...")
        results = detector.detect_objects(test_frame)
        print("✓ Detection successful")
        
        return True
    
    except Exception as e:
        print(f"✗ Detection failed: {str(e)}")
        return False


def fix_ultralytics():
    """Fix ultralytics/YOLOv8"""
    print("\n" + "=" * 60)
    print("ULTRALYTICS/YOLOV8 FIX")
    print("=" * 60)
    
    print("Running fix...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", 
                             "ultralytics", "--force-reinstall"])
        print("✓ Ultralytics reinstalled")
        return True
    except Exception as e:
        print(f"✗ Fix failed: {str(e)}")
        return False


def main():
    """Main troubleshooting flow"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "VEHICLE DETECTION - TROUBLESHOOTING" + " " * 14 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # Step 1: Diagnose
    pytorch_ok = diagnose_pytorch()
    
    # Step 2: Fix if needed
    if not pytorch_ok:
        print("\n⚠️  PyTorch issues detected!")
        if fix_pytorch():
            print("\n✓ PyTorch fixed!")
        else:
            print("\n✗ Failed to fix PyTorch")
            return 1
    
    # Step 3: Fix ultralytics
    print("\nFixing YOLOv8...")
    if fix_ultralytics():
        print("✓ YOLOv8 fixed!")
    
    # Step 4: Test
    print("\nTesting detection...")
    if test_detection():
        print("\n" + "=" * 60)
        print("✓✓✓ ALL SYSTEMS GO! ✓✓✓")
        print("=" * 60)
        print("\nYou can now run:")
        print("  python gui.py")
        return 0
    else:
        print("\n" + "=" * 60)
        print("⚠️  Detection test failed")
        print("=" * 60)
        print("\nManual fixes to try:")
        print("1. pip uninstall torch torchvision -y && pip install torch torchvision")
        print("2. pip install --upgrade ultralytics")
        print("3. Restart your Command Prompt")
        print("4. Try again")
        return 1


if __name__ == "__main__":
    sys.exit(main())
