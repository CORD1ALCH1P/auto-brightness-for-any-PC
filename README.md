# Auto Brightness Control

Automatic display brightness adjustment based on ambient light detection using your webcam.

## Features

- Real-time brightness monitoring via webcam
- Automatic display brightness adjustment
- Customizable brightness thresholds (5 levels)
- Adjustable update interval (0.5-10 seconds)
- System tray integration
- Settings persistence
- Lightweight and responsive

## Requirements

- Windows 10/11
- Webcam
- Python 3.8+ (for development) or standalone executable
- Monitor with DDC-CI support (for brightness control)

## Installation

### Option 1: Standalone Executable (Recommended)

Download `AutoBrightness.exe` from releases and run it directly. No installation required.

### Option 2: From Source

```bash
# Clone repository
git clone <repository-url>
cd brightness-control

# Install dependencies
pip install -r requirements.txt

# Run application
python main_app.py
```

## Usage

1. Launch the application
2. Click "Start" to enable automatic brightness control
3. Adjust update interval if needed (default: 1.0 second)
4. Close window to minimize to system tray
5. Right-click tray icon for menu options

## Configuration

Brightness thresholds are adjustable via GUI sliders:

- 90-100% ambient light → 100% monitor brightness
- 80-90% → 80%
- 70-80% → 60%
- 50-70% → 40%
- 0-50% → 30%

Custom values are saved automatically and persist between sessions.

## Troubleshooting

### Camera not detected

Edit `config.json` and change `camera_index`:

```json
{
  "camera_index": 0
}
```

Try values 0, 1, 2, etc. until correct camera is found.

### Brightness not changing

1. Verify monitor supports DDC-CI brightness control
2. Check Windows Defender Firewall settings
3. Run application as administrator
4. Update graphics drivers

### Tray icon not appearing

Minimize and restore the window. Right-click desktop to access tray settings.

## Building Executable

To create standalone Windows executable:

```bash
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name AutoBrightness --icon icon.ico main_app.py
```

Executable will be in `dist/AutoBrightness.exe`

## Project Structure

```
.
├── main.py              # Brightness control logic
├── gui.py               # GUI interface (CustomTkinter)
├── main_app.py          # Application entry point
├── config.json          # User settings
├── icon.ico             # Application icon
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Dependencies

- `opencv-python` - Webcam video capture and brightness analysis
- `customtkinter` - Modern GUI framework
- `pystray` - System tray integration
- `screen-brightness-control` - Display brightness control
- `pillow` - Image processing

## Performance

- Memory usage: ~100-200 MB
- CPU usage: 1-5% (depends on update interval)
- Startup time: <5 seconds

## License

MIT License - See LICENSE file for details

## Support

For issues:

1. Check `config.json` for valid settings
2. Run `python test_installation.py` to verify dependencies
3. Review troubleshooting section above
4. Check that camera is accessible to the application

## Version

Version: 1.1.0
Last Updated: 2026
