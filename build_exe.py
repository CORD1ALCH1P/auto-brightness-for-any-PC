#!/usr/bin/env python3
"""
Build Windows executable using PyInstaller
"""

import os
import subprocess
import sys
from pathlib import Path

print("[INFO] Building Windows executable...")
print("[INFO] Creating AutoBrightness.exe\n")

# Check if PyInstaller is installed
try:
    import PyInstaller
    print("[OK] PyInstaller found")
except ImportError:
    print("[ERROR] PyInstaller not found!")
    print("[INFO] Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("[OK] PyInstaller installed")

print("[INFO] Building executable...\n")

# Use Python module syntax for cross-platform compatibility
cmd = [
    sys.executable,
    "-m",
    "PyInstaller",
    "--onefile",
    "--windowed",
    "--name", "AutoBrightness",
    "--icon", "icon.ico",
    "-p", ".",
    "main_app.py"
]

print(f"[INFO] Command: {' '.join(cmd)}\n")

try:
    result = subprocess.run(cmd, check=True)
    print("\n[OK] Build complete!")
    
    exe_path = Path("dist/AutoBrightness.exe")
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024*1024)
        print(f"[OK] Executable: {exe_path}")
        print(f"[OK] Size: {size_mb:.1f} MB")
        print("\n[SUCCESS] Application ready for distribution!")
        print("[INFO] No Python required - users can run directly")
    else:
        print("[WARNING] Build completed but executable not found")
        print("[INFO] Check the dist/ folder")
        
except subprocess.CalledProcessError as e:
    print(f"\n[ERROR] Build failed!")
    print(f"Error code: {e.returncode}")
    print("\n[TROUBLESHOOTING]")
    print("1. Verify files exist: main_app.py, config.json, icon.ico")
    print("2. Upgrade PyInstaller: pip install --upgrade pyinstaller")
    print("3. Ensure all modules installed: pip install -r requirements.txt")
    print("\n[MANUAL BUILD]")
    print("Try this command:")
    print(f"  {sys.executable} -m PyInstaller --onefile --windowed --name AutoBrightness main_app.py")
    sys.exit(1)
except Exception as e:
    print(f"\n[ERROR] {e}")
    sys.exit(1)
