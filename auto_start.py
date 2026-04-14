import sys
import os
from pathlib import Path
import json

try:
    import winreg
    HAS_WINREG = True
except ImportError:
    HAS_WINREG = False


class AutoStartManager:
    
    APP_NAME = "AutoBrightnessControl"
    
    def __init__(self):
        self.is_windows = sys.platform == 'win32'
        self._get_paths()
    
    def _get_paths(self):
        if getattr(sys, 'frozen', False):
            base_path = sys.executable
        else:
            script_dir = Path(__file__).parent.absolute()
            base_path = str(script_dir / 'main_app.py')
        
        self.app_path = base_path
        
        if self.is_windows:
            self.auto_start_dir = Path(os.path.expandvars('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'))
        else:
            self.auto_start_dir = Path.home() / '.config/autostart'
    
    def enable(self):
        try:
            if self.is_windows and HAS_WINREG:
                self._enable_windows_registry()
            else:
                self._enable_linux_mac()
            return True
        except Exception as e:
            print(f"error in autoboot: {e}")
            return False
    
    def disable(self):
        try:
            if self.is_windows and HAS_WINREG:
                self._disable_windows_registry()
            else:
                self._disable_linux_mac()
            return True
        except Exception as e:
            print(f"Error in disabe aoutoboot: {e}")
            return False
    
    def is_enabled(self):
        try:
            if self.is_windows and HAS_WINREG:
                return self._check_windows_registry()
            else:
                return self._check_linux_mac()
        except:
            return False
    
    # Windows методы
    
    def _enable_windows_registry(self):
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, self.APP_NAME, 0, winreg.REG_SZ, self.app_path)
        winreg.CloseKey(key)
    
    def _disable_windows_registry(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.DeleteValue(key, self.APP_NAME)
            winreg.CloseKey(key)
        except FileNotFoundError:
            pass  # Ключа уже нет
    
    def _check_windows_registry(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            value, _ = winreg.QueryValueEx(key, self.APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
    
    # Linux/Mac методы
    
    def _enable_linux_mac(self):
        self.auto_start_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_file = self.auto_start_dir / f"{self.APP_NAME}.desktop"
        
        content = f"[Desktop Entry]\nType=Application\nName={self.APP_NAME}\nExec={sys.executable} {self.app_path}\nHidden=false\nNoDisplay=false\nX-GNOME-Autostart-enabled=true\n"
        
        with open(desktop_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _disable_linux_mac(self):
        desktop_file = self.auto_start_dir / f"{self.APP_NAME}.desktop"
        if desktop_file.exists():
            desktop_file.unlink()
    
    def _check_linux_mac(self):
        desktop_file = self.auto_start_dir / f"{self.APP_NAME}.desktop"
        return desktop_file.exists()
