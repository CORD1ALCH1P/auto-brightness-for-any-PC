import cv2
import numpy as np
import screen_brightness_control as sbc
import json
import math
import ctypes
import time
from pathlib import Path


class BrightnessController:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.running = False
        self.config = self.load_config()
        self.cap = None

        # Brightness pipeline state
        self.smoothed_brightness = None
        self.current_screen_brightness = None

        # SoftLight pipeline state
        self.smoothed_cct = None
        self.current_cct_applied = None

    # ── Config ────────────────────────────────────────────────────────────────

    def load_config(self):
        default_config = {
            "auto_start": False,
            "update_interval": 1.0,
            "camera_index": 0,
            # Brightness
            "min_brightness": 20,
            "max_brightness": 100,
            "smoothing_alpha": 0.2,
            "gamma": 0.5,
            "hysteresis_deadband": 3,
            # SoftLight
            "softlight_enabled": False,
            "softlight_strength": 0.7,   # 0.0 – no shift, 1.0 – full shift
            "softlight_alpha": 0.1,      # EMA for CCT (slower than brightness)
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

    # ── Sensing ───────────────────────────────────────────────────────────────

    def _try_disable_awb(self):
        """
        Try to turn off the camera's Auto White Balance so that R/G/B channel
        ratios reflect the actual ambient light color rather than the camera's
        own correction.  Many cameras silently ignore this; we try anyway.
        """
        try:
            self.cap.set(cv2.CAP_PROP_AUTO_WB, 0)
        except Exception:
            pass

    def _measure_ambient(self, frame):
        """
        Estimate ambient light from peripheral frame regions (BGR frame).

        Using top strip + left/right edges reduces the influence of
        foreground objects and captures background / ceiling light instead.

        Returns (brightness, r_mean, g_mean, b_mean) all in [0, 255].
        """
        h, w = frame.shape[:2]

        top   = frame[:h // 5,  :]
        left  = frame[:,         :w // 6]
        right = frame[:, -w // 6:]

        # Stack all peripheral pixels: shape (N, 3), columns = [B, G, R]
        pixels = np.concatenate([
            top.reshape(-1, 3),
            left.reshape(-1, 3),
            right.reshape(-1, 3)
        ])

        b_mean = float(pixels[:, 0].mean())
        g_mean = float(pixels[:, 1].mean())
        r_mean = float(pixels[:, 2].mean())

        brightness = (r_mean + g_mean + b_mean) / 3.0
        return brightness, r_mean, g_mean, b_mean

    # ── Brightness pipeline ───────────────────────────────────────────────────

    def _apply_ema(self, raw_value: float) -> float:
        """EMA smoothing for brightness."""
        alpha = float(self.config.get("smoothing_alpha", 0.2))
        if self.smoothed_brightness is None:
            self.smoothed_brightness = raw_value
        else:
            self.smoothed_brightness = (
                alpha * raw_value + (1.0 - alpha) * self.smoothed_brightness
            )
        return self.smoothed_brightness

    def _map_to_screen(self, camera_value: float) -> int:
        """Gamma + linear mapping: camera (0–255) → screen brightness (%)."""
        min_br = int(self.config.get("min_brightness", 20))
        max_br = int(self.config.get("max_brightness", 100))
        gamma  = float(self.config.get("gamma", 0.5))

        normalized = min(camera_value / 255.0, 1.0)
        perceptual = normalized ** gamma
        return int(round(min_br + perceptual * (max_br - min_br)))

    # ── SoftLight pipeline ────────────────────────────────────────────────────

    def _estimate_cct(self, r: float, g: float, b: float) -> int:
        """
        Estimate Correlated Color Temperature in Kelvin from ambient RGB.

        Pipeline:
          sRGB (0-255) → linear RGB → XYZ (D65) → CIE xy chromaticity
          → McCamy (1992) CCT formula.

        Result is clamped to [1 800 K, 10 000 K].
        """
        r_n, g_n, b_n = r / 255.0, g / 255.0, b / 255.0

        # sRGB → XYZ  (IEC 61966-2-1, D65 white point)
        X = r_n * 0.4124564 + g_n * 0.3575761 + b_n * 0.1804375
        Y = r_n * 0.2126729 + g_n * 0.7151522 + b_n * 0.0721750
        Z = r_n * 0.0193339 + g_n * 0.1191920 + b_n * 0.9503041

        denom = X + Y + Z
        if denom < 1e-10:
            return 5500  # neutral daylight fallback

        x = X / denom
        y = Y / denom

        # McCamy 1992: CCT from chromaticity
        n = (x - 0.3320) / (y - 0.1858 + 1e-10)
        cct = -449.0 * n**3 + 3525.0 * n**2 - 6823.3 * n + 5520.33

        return int(max(1800, min(cct, 10000)))

    def _apply_cct_ema(self, raw_cct: float) -> float:
        """EMA smoothing for color temperature (slower alpha than brightness)."""
        alpha = float(self.config.get("softlight_alpha", 0.1))
        if self.smoothed_cct is None:
            self.smoothed_cct = raw_cct
        else:
            self.smoothed_cct = (
                alpha * raw_cct + (1.0 - alpha) * self.smoothed_cct
            )
        return self.smoothed_cct

    def _kelvin_to_multipliers(self, kelvin: float):
        """
        Convert color temperature (K) to (R, G, B) gain multipliers in [0, 1].

        Implements the Tanner Helland (2012) piecewise algorithm.
        At 6 500 K the output is approximately (1, 1, 1) — neutral.
        Warmer temperatures raise R, cool temperatures raise B.
        """
        t = kelvin / 100.0

        # Red
        r = 1.0 if t <= 66 else max(0.0, min(1.0,
            329.698727446 * (t - 60) ** -0.1332047592 / 255.0))

        # Green
        if t <= 66:
            g = max(0.0, min(1.0,
                (99.4708025861 * math.log(t) - 161.1195681661) / 255.0))
        else:
            g = max(0.0, min(1.0,
                288.1221695283 * (t - 60) ** -0.0755148492 / 255.0))

        # Blue
        if t >= 66:
            b = 1.0
        elif t <= 19:
            b = 0.0
        else:
            b = max(0.0, min(1.0,
                (138.5177312231 * math.log(t - 10) - 305.0447927307) / 255.0))

        return r, g, b

    def _apply_gamma_ramp(self, r_mult: float, g_mult: float, b_mult: float) -> bool:
        """
        Load a per-channel gain into the Windows display gamma ramp via GDI32.

        Builds a 256-entry LUT for each channel (values are 16-bit, 0–65535),
        then calls SetDeviceGammaRamp.  Returns True on success.
        Some monitors/drivers silently ignore this call.
        """
        try:
            hdc = ctypes.windll.user32.GetDC(None)
            ramp = (ctypes.c_uint16 * 768)()
            for i in range(256):
                ramp[i]       = int(min(i * 257 * r_mult, 65535))
                ramp[i + 256] = int(min(i * 257 * g_mult, 65535))
                ramp[i + 512] = int(min(i * 257 * b_mult, 65535))
            result = ctypes.windll.gdi32.SetDeviceGammaRamp(hdc, ramp)
            ctypes.windll.user32.ReleaseDC(None, hdc)
            return bool(result)
        except Exception as e:
            print(f"[SOFTLIGHT] Gamma ramp error: {e}")
            return False

    def _softlight_tick(self, r: float, g: float, b: float):
        """
        One SoftLight iteration:
          1. Estimate CCT from ambient RGB.
          2. EMA-smooth it (slow filter — room lighting changes slowly).
          3. Blend toward neutral by (1 - strength) to keep the effect subtle.
          4. Apply via gamma ramp only when CCT shifts more than 50 K.
        """
        measured_cct = self._estimate_cct(r, g, b)
        smoothed = self._apply_cct_ema(float(measured_cct))

        # Blend: 0 % strength → always 6500 K (neutral), 100 % → full shift
        strength = float(self.config.get("softlight_strength", 0.7))
        neutral  = 6500.0
        effective_cct = neutral + (smoothed - neutral) * strength
        effective_cct = max(1800.0, min(effective_cct, 10000.0))

        # Hysteresis: skip SetDeviceGammaRamp if change is tiny
        if (self.current_cct_applied is None
                or abs(effective_cct - self.current_cct_applied) > 50):
            self.current_cct_applied = effective_cct
            r_m, g_m, b_m = self._kelvin_to_multipliers(effective_cct)
            self._apply_gamma_ramp(r_m, g_m, b_m)
            print(
                f"[SOFTLIGHT] measured={measured_cct}K  "
                f"effective={int(effective_cct)}K  "
                f"R={r_m:.3f} G={g_m:.3f} B={b_m:.3f}"
            )

    def reset_softlight(self):
        """
        Immediately restore a neutral (1, 1, 1) gamma ramp.
        Call this when SoftLight is toggled off or the app exits.
        """
        self._apply_gamma_ramp(1.0, 1.0, 1.0)
        self.smoothed_cct = None
        self.current_cct_applied = None
        print("[SOFTLIGHT] Gamma restored to neutral")

    # ── Main adjustment cycle ─────────────────────────────────────────────────

    def adjust_brightness(self):
        """Capture one frame and run both brightness and SoftLight pipelines."""
        if not self.cap or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.config["camera_index"])
            self._try_disable_awb()

        if not self.cap.isOpened():
            print("[ERROR] Cannot open camera!")
            return

        ret, frame = self.cap.read()
        if not ret:
            print("[ERROR] Cannot read frame")
            return

        # 1. Sense
        raw_brightness, r, g, b = self._measure_ambient(frame)

        # 2. Brightness — EMA → gamma map → hysteresis → sbc
        smoothed = self._apply_ema(raw_brightness)
        target   = self._map_to_screen(smoothed)

        deadband = int(self.config.get("hysteresis_deadband", 3))
        if (self.current_screen_brightness is None
                or abs(target - self.current_screen_brightness) > deadband):
            self.current_screen_brightness = target
            try:
                sbc.set_brightness(target)
                print(
                    f"[BRIGHTNESS] raw={raw_brightness:.1f}  "
                    f"smooth={smoothed:.1f}  screen={target}%"
                )
            except Exception as e:
                print(f"[ERROR] Cannot set brightness: {e}")
        else:
            print(
                f"[BRIGHTNESS] stable  smooth={smoothed:.1f}  "
                f"screen={self.current_screen_brightness}%"
            )

        # 3. SoftLight — CCT estimate → EMA → gamma ramp
        if self.config.get("softlight_enabled", False):
            self._softlight_tick(r, g, b)
        elif self.current_cct_applied is not None:
            # SoftLight was just turned off mid-run — restore neutral
            self.reset_softlight()

    # ── Loop ──────────────────────────────────────────────────────────────────

    def start_continuous_adjustment(self):
        """Main loop — runs in the worker thread."""
        self.running = True
        print("[OK] Starting brightness control...")
        print(f"[INFO] Camera index: {self.config['camera_index']}")

        while self.running:
            try:
                self.adjust_brightness()
                time.sleep(float(self.config["update_interval"]))
            except KeyboardInterrupt:
                print("\n[INFO] Stopped by user")
                break
            except Exception as e:
                print(f"[ERROR] {e}")
                time.sleep(float(self.config.get("update_interval", 1.0)))

        self.stop()

    def stop(self):
        """Stop the loop, release camera, reset all state and gamma ramp."""
        self.running = False

        if self.cap:
            self.cap.release()
            self.cap = None

        # Restore display if SoftLight left a gamma ramp applied
        if self.current_cct_applied is not None:
            self._apply_gamma_ramp(1.0, 1.0, 1.0)
            print("[SOFTLIGHT] Gamma restored to neutral on stop")

        self.smoothed_brightness    = None
        self.current_screen_brightness = None
        self.smoothed_cct           = None
        self.current_cct_applied    = None

        print("[OK] Controller stopped")

    # ── Config helper ─────────────────────────────────────────────────────────

    def update_settings(self, settings):
        self.config.update(settings)
        self.save_config()
