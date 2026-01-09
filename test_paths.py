import os
import sys

# Add current directory to path to import your module
sys.path.append('.')

from reset_machine_manual import get_workbench_cursor_path

print("=== TESTING get_workbench_cursor_path() ===")

try:
    # Create a simple translator object for testing
    class SimpleTranslator:
        def get(self, key, **kwargs):
            return key
    
    translator = SimpleTranslator()
    path = get_workbench_cursor_path(translator)
    print(f"Function returned: {path}")
    print(f"Path exists: {os.path.exists(path)}")
    
    # Check what's actually at that path
    if os.path.exists(path):
        print(f"✓ File exists at returned path")
    else:
        print(f"✗ File NOT found at returned path")
        
        # Check correct path
        correct_path = r"C:\Program Files\cursor\resources\app\out\vs\workbench\workbench.desktop.main.js"
        print(f"\nChecking correct path: {correct_path}")
        print(f"Correct path exists: {os.path.exists(correct_path)}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== END TEST ===")
