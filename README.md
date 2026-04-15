# Adaptive Display

Webcam-based automatic brightness and colour temperature control for Windows.
Adaptive Display reads ambient light through your existing webcam and continuously
adjusts your monitor's brightness — and optionally its white point — to match
the environment, reducing eye strain without any extra hardware.

---

## Features

- **Auto brightness** — analyses ambient light every N seconds and sets monitor
  brightness accordingly; no dedicated light sensor required.
- **SoftLight** — estimates the colour temperature of the room light and shifts
  the display's white point to match, similar to Apple TrueTone.
- **Perceptual algorithm** — exponential smoothing (EMA), gamma correction, and
  a hysteresis deadband work together to eliminate flickering and sudden jumps.
- **Peripheral ROI sensing** — only the top strip and side edges of the camera
  frame are sampled, so foreground objects (faces, screens) don't skew the reading.
- **System tray** — runs silently in the background; close the window to minimise
  to tray, click Exit to quit completely.
- **Start with Windows** — optional registry autostart entry written with one click.
- **Configurable interval** — update frequency adjustable from 0.5 s to 10 s via slider.
- **Standalone executable** — ships as a single `.exe`; no Python installation needed.

---

## How It Works

### Brightness pipeline

```
Camera frame
  └─ Peripheral ROI (top 20 %, left/right 17 %)
       └─ Greyscale mean  →  raw brightness (0–255)
            └─ EMA filter  →  smoothed value
                 └─ Gamma curve (x^0.5) + linear scale  →  target %
                      └─ Hysteresis gate (±3 %)
                           └─ screen_brightness_control.set_brightness()
```

### SoftLight pipeline

```
Same peripheral pixels (R, G, B channels separate)
  └─ sRGB → XYZ → CIE xy chromaticity
       └─ McCamy (1992) formula  →  CCT in Kelvin
            └─ EMA filter (slower α = 0.1)
                 └─ Blend toward neutral 6 500 K by (1 − strength)
                      └─ Hysteresis gate (±50 K)
                           └─ Tanner Helland algorithm  →  R/G/B multipliers
                                └─ SetDeviceGammaRamp (Windows GDI32)
```

> **Note on camera white balance.**
> Consumer webcams apply Auto White Balance (AWB) to their output, which
> partially counteracts the colour shift you are trying to measure.
> Adaptive Display attempts to disable AWB via `cv2.CAP_PROP_AUTO_WB`; whether
> this succeeds depends on the camera driver. Even with AWB active, the
> *relative* changes in ambient colour are usually large enough to produce a
> useful and perceptible SoftLight effect.

---

## Screenshot

> *(Add screenshot here)*

---

## Installation

### Option A — Pre-built executable (recommended)

1. Download `AutoBrightness.exe` from the [Releases](../../releases) page.
2. Place it in any folder alongside `config.json`.
3. Run `AutoBrightness.exe`.

### Option B — Run from source

**Requirements:** Python 3.9+

```bash
git clone https://github.com/your-username/adaptive-display.git
cd adaptive-display
pip install -r requirements.txt
python main_app.py
```

### Option C — Build the executable yourself

```bash
pip install -r requirements.txt
pip install pyinstaller
python build_exe.py
# Output: dist/AutoBrightness.exe
```

---

## Configuration

All settings are stored in `config.json` next to the executable.
Most of them can also be changed through the GUI.

| Key | Default | Description |
|-----|---------|-------------|
| `update_interval` | `1.0` | Seconds between brightness checks (0.5 – 10) |
| `camera_index` | `0` | OpenCV camera index (0 = default webcam) |
| `min_brightness` | `20` | Minimum screen brightness in % |
| `max_brightness` | `100` | Maximum screen brightness in % |
| `smoothing_alpha` | `0.2` | EMA factor for brightness (0.1 = slow, 0.4 = fast) |
| `gamma` | `0.5` | Perceptual curve exponent (lower = brighter in dim light) |
| `hysteresis_deadband` | `3` | Min brightness change in % before updating the monitor |
| `softlight_enabled` | `false` | Enable SoftLight colour temperature adaptation |
| `softlight_strength` | `0.7` | Intensity of the colour shift (0.0 – 1.0) |
| `softlight_alpha` | `0.1` | EMA factor for colour temperature (slower than brightness) |
| `auto_start` | `false` | Managed by the *Start with Windows* checkbox |

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| opencv-python | 4.9.0.80 | Camera capture and image processing |
| screen-brightness-control | 0.27.1 | DDC-CI monitor brightness control |
| customtkinter | 5.2.0 | Modern GUI framework |
| pystray | 0.19.5 | System tray integration |
| pillow | ≥ 9.0.0 | Tray icon rendering |
| numpy | < 2 | Array operations |

---

## Compatibility

| | Supported |
|--|--|
| OS | Windows 10 / 11 |
| Monitor interface | DDC-CI (most external monitors), laptop panels |
| Camera | Any OpenCV-compatible webcam |
| SoftLight gamma ramp | Most monitors and GPU drivers |

> **Laptop brightness** is controlled through WMI; **external monitor** brightness
> requires DDC-CI support. If `screen_brightness_control` cannot find a display,
> check that DDC-CI is enabled in your monitor's OSD settings.

---

## License

MIT
