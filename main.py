import cv2
import screen_brightness_control as sbc
import json
import time
from pathlib import Path


class BrightnessController:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.running = False
        self.config = self.load_config()
        self.cap = None
        
    def load_config(self):
        default_config = {
            "auto_start": False,
            "thresholds": [
                {"min": 90, "max": 100, "output": 100},
                {"min": 80, "max": 90, "output": 80},
                {"min": 70, "max": 80, "output": 60},
                {"min": 50, "max": 70, "output": 40},
                {"min": 0, "max": 50, "output": 30}
            ],
            "update_interval": 1.0,
            "camera_index": 0
        }
        
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
                    return default_config
        except (json.JSONDecodeError, IOError) as e:
            print(f"[ERROR] Config error: {e}. Using defaults.")
        
        return default_config
    
    def save_config(self, new_config=None):
        if new_config:
            self.config.update(new_config)
            
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)
    
    def calculate_camera_brightness(self, frame):
        """Calculate brightness from camera frame (0-255 scale)"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = int(gray.mean())
        return brightness
    
    def find_matching_threshold(self, camera_brightness):
        """Find output brightness based on camera brightness (0-255 scale)"""
        # Direct threshold matching - proven to work
        if camera_brightness > 90:
            return 100
        elif 80 <= camera_brightness <= 90:
            return 80
        elif 70 <= camera_brightness <= 80:
            return 60
        elif 50 <= camera_brightness <= 70:
            return 40
        else:
            return 30
    
    def adjust_brightness(self):
        """Capture frame and adjust brightness"""
        if not self.cap or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.config["camera_index"])
            
        if not self.cap.isOpened():
            print("[ERROR] Cannot open camera!")
            return
        
        ret, frame = self.cap.read()
        
        if not ret:
            print("[ERROR] Cannot read frame")
            return
        
        # Get brightness from camera (0-255 scale)
        camera_brightness = self.calculate_camera_brightness(frame)
        
        # Find matching output brightness
        output_brightness = self.find_matching_threshold(camera_brightness)
        
        # Set monitor brightness
        try:
            sbc.set_brightness(output_brightness)
            current = sbc.get_brightness(display=0)[0]
            print(f"[BRIGHTNESS] Camera: {camera_brightness} -> Monitor: {current}%")
        except Exception as e:
            print(f"[ERROR] Cannot set brightness: {e}")
    
    def start_continuous_adjustment(self):
        """Main loop - continuously adjust brightness"""
        self.running = True
        print(f"[OK] Starting brightness control...")
        print(f"[INFO] Update interval: {self.config['update_interval']} sec")
        print(f"[INFO] Camera index: {self.config['camera_index']}")
        print(f"[INFO] Press Ctrl+C to stop")
        
        interval = self.config["update_interval"]
        
        while self.running:
            try:
                self.adjust_brightness()
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n[INFO] Stopped by user")
                break
            except Exception as e:
                print(f"[ERROR] {e}")
                time.sleep(interval)
        
        self.stop()
    
    def stop(self):
        """Stop brightness control"""
        self.running = False
        if self.cap:
            self.cap.release()
        print("[OK] Controller stopped")
    
    def update_thresholds(self, thresholds):
        """Update threshold values from GUI"""
        self.config["thresholds"] = thresholds
        self.save_config()
    
    def update_settings(self, settings):
        """Update general settings"""
        self.config.update(settings)
        self.save_config()
    
    def get_thresholds(self):
        """Get current threshold values"""
        return self.config.get("thresholds", [])
