"""
Diagnostic script to test best.pt detection
"""
import os
import sys
from pathlib import Path

print("=" * 60)
print("YOLO Model Detection Diagnostic")
print("=" * 60)

# Check current directory
print(f"\n1. Current Working Directory:")
print(f"   {os.getcwd()}")

# Check script location
script_path = Path(__file__).resolve()
print(f"\n2. Script Location:")
print(f"   {script_path}")

# Check parent directory (project root)
root = script_path.parent
print(f"\n3. Project Root:")
print(f"   {root}")

# Check for best.pt in expected locations
print(f"\n4. Checking for best.pt in expected locations:")
candidates = [
    root / "best.pt",
    root / "ai" / "models" / "best.pt",
    root / "models" / "best.pt",
    root / "static" / "models" / "best.pt",
]

for i, path in enumerate(candidates, 1):
    exists = path.exists()
    size = path.stat().st_size if exists else 0
    print(f"   [{i}] {path}")
    print(f"       Exists: {exists}")
    if exists:
        print(f"       Size: {size:,} bytes ({size / (1024*1024):.2f} MB)")

# Check environment variable
env_path = os.getenv("BEST_MODEL_PATH")
print(f"\n5. BEST_MODEL_PATH Environment Variable:")
if env_path:
    print(f"   Set to: {env_path}")
    print(f"   Exists: {os.path.exists(env_path)}")
else:
    print(f"   Not set")

# Try to import ultralytics
print(f"\n6. Checking ultralytics installation:")
try:
    from ultralytics import YOLO
    print(f"   ✅ ultralytics is installed")
    print(f"   Version: {YOLO.__module__}")
except ImportError as e:
    print(f"   ❌ ultralytics is NOT installed")
    print(f"   Error: {e}")
    print(f"\n   To install: pip install ultralytics")

# Try to load the model
print(f"\n7. Attempting to load YOLO model:")
best_pt_path = root / "best.pt"
if best_pt_path.exists():
    try:
        from ultralytics import YOLO
        model = YOLO(str(best_pt_path))
        print(f"   ✅ Model loaded successfully!")
        print(f"   Model type: {type(model)}")
        if hasattr(model, 'names'):
            print(f"   Classes: {model.names}")
    except ImportError:
        print(f"   ❌ Cannot load - ultralytics not installed")
    except Exception as e:
        print(f"   ❌ Failed to load model")
        print(f"   Error: {e}")
else:
    print(f"   ❌ best.pt not found at {best_pt_path}")

# Check ImageIssueClassifier
print(f"\n8. Testing ImageIssueClassifier:")
try:
    sys.path.insert(0, str(root))
    from ai.image_classifier import ImageIssueClassifier
    
    classifier = ImageIssueClassifier()
    print(f"   Model path: {classifier.yolo_model_path}")
    print(f"   Model available: {classifier.is_available()}")
    
    if classifier.is_available():
        info = classifier.get_model_info()
        print(f"   Model info: {info}")
    else:
        print(f"   ❌ Classifier not available")
        
except Exception as e:
    print(f"   ❌ Error initializing classifier")
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Diagnostic Complete")
print("=" * 60)
