#!/usr/bin/env python3
"""
Main application entry point
"""
import sys
import os

def main_entry():
    """Application entry point"""
    # Add current directory to path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    try:
        # Import and run GUI
        from gui import BrightnessGUI
        
        # Create and start application
        app = BrightnessGUI()
        app.mainloop()
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        print("[INFO] Install dependencies: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Application error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main_entry()
