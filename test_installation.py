#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dependency installation checker
"""
import sys

def test_imports():
    """Check if all required modules are installed"""
    
    modules = [
        ('cv2', 'opencv-python'),
        ('customtkinter', 'customtkinter'),
        ('pystray', 'pystray'),
        ('PIL', 'pillow'),
        ('screen_brightness_control', 'screen-brightness-control'),
    ]
    
    print("\n[CHECKING] Dependencies check...\n")
    
    all_ok = True
    for module_name, package_name in modules:
        try:
            __import__(module_name)
            print(f"[OK] {module_name:<30} installed")
        except ImportError:
            print(f"[FAIL] {module_name:<30} NOT installed")
            print(f"       Install: pip install {package_name}")
            all_ok = False
    
    print()
    
    if all_ok:
        print("[OK] All dependencies are installed correctly!")
        print("\nYou can run the application with:")
        print("    python main_app.py")
        return 0
    else:
        print("[FAIL] Some dependencies are missing.")
        print("\nInstall them with:")
        print("    pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(test_imports())
