import customtkinter as ctk
from threading import Thread
import main
import pystray
from PIL import Image, ImageDraw
import math
import sys
import os
from auto_start import AutoStartManager

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Color palette
_ACCENT      = "#3b82f6"
_ACCENT_HOV  = "#2563eb"
_BTN_MUTED   = "#252525"
_BTN_MUT_HOV = "#2e2e2e"
_SEP         = "#2a2a2a"
_TEXT_MUTED  = "#6b7280"
_GREEN       = "#10b981"
_AMBER       = "#f59e0b"
_RED         = "#ef4444"

class BrightnessGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.controller = main.BrightnessController()
        self.auto_start_manager = AutoStartManager()
        self.running = False
        self.working_thread = None
        self.tray_icon = None
        self.tray_thread = None
        self.should_exit = False

        self.title("Auto Brightness")
        self.geometry("400x280")
        self.resizable(False, False)

        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.setup_ui()
        self.load_settings()

        self.after(500, self.start_tray_thread)

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=24, pady=20)

        # ── Header ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(main_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(
            header,
            text="Auto Brightness",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left")

        self.status_dot = ctk.CTkLabel(
            header, text="●",
            font=ctk.CTkFont(size=10),
            text_color=_GREEN, width=14
        )
        self.status_dot.pack(side="right", padx=(4, 0))

        self.status_label = ctk.CTkLabel(
            header,
            text="Idle",
            font=ctk.CTkFont(size=11),
            text_color=_TEXT_MUTED
        )
        self.status_label.pack(side="right")

        # ── Separator ─────────────────────────────────────────────────────────
        ctk.CTkFrame(main_frame, height=1, fg_color=_SEP).pack(fill="x", pady=(8, 14))

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 14))

        self.start_button = ctk.CTkButton(
            btn_frame, text="Start",
            command=self.start_controller,
            height=34, corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=_ACCENT, hover_color=_ACCENT_HOV
        )
        self.start_button.pack(side="left", fill="both", expand=True, padx=(0, 6))

        self.stop_button = ctk.CTkButton(
            btn_frame, text="Stop",
            command=self.stop_controller,
            height=34, corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            state="disabled",
            fg_color=_BTN_MUTED, hover_color=_BTN_MUT_HOV,
            text_color=_TEXT_MUTED
        )
        self.stop_button.pack(side="left", fill="both", expand=True)

        # ── Separator ─────────────────────────────────────────────────────────
        ctk.CTkFrame(main_frame, height=1, fg_color=_SEP).pack(fill="x", pady=(0, 12))

        # ── Interval slider ───────────────────────────────────────────────────
        interval_row = ctk.CTkFrame(main_frame, fg_color="transparent")
        interval_row.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(
            interval_row, text="Update interval",
            font=ctk.CTkFont(size=11), text_color=_TEXT_MUTED
        ).pack(side="left")

        self.interval_label = ctk.CTkLabel(
            interval_row, text="1.0s",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#ffffff"
        )
        self.interval_label.pack(side="right")

        self.interval_slider = ctk.CTkSlider(
            main_frame,
            from_=0.5, to=10, number_of_steps=95,
            command=self.on_interval_change,
            height=14,
            button_color=_ACCENT, button_hover_color=_ACCENT_HOV,
            progress_color=_ACCENT
        )
        self.interval_slider.pack(fill="x", pady=(0, 14))

        # ── Autostart checkbox ────────────────────────────────────────────────
        self.autostart_checkbox = ctk.CTkCheckBox(
            main_frame, text="Start with Windows",
            command=self.on_autostart_change,
            font=ctk.CTkFont(size=11),
            text_color=_TEXT_MUTED,
            fg_color=_ACCENT, hover_color=_ACCENT_HOV,
            checkmark_color="#ffffff",
            border_color="#3d3d3d",
            corner_radius=4
        )
        self.autostart_checkbox.pack(anchor="w")

    # ── Tray icon image ────────────────────────────────────────────────────────
    def create_icon_image(self):
        img = Image.new('RGB', (64, 64), color='#1a1a1a')
        draw = ImageDraw.Draw(img)
        center, radius = 32, 20
        draw.ellipse(
            [center-radius, center-radius, center+radius, center+radius],
            fill='#FFD700', outline='#FFA500', width=2
        )
        for i in range(8):
            angle = (i * 45) * math.pi / 180
            x1 = center + int((radius - 3) * math.cos(angle))
            y1 = center + int((radius - 3) * math.sin(angle))
            x2 = center + int((radius + 8) * math.cos(angle))
            y2 = center + int((radius + 8) * math.sin(angle))
            draw.line([(x1, y1), (x2, y2)], fill='#FFA500', width=2)
        return img

    # ── Tray ──────────────────────────────────────────────────────────────────
    def start_tray_thread(self):
        self.tray_thread = Thread(target=self.setup_tray, daemon=False)
        self.tray_thread.start()

    def setup_tray(self):
        try:
            print("[INFO] Creating tray icon...")
            menu = pystray.Menu(
                pystray.MenuItem('Show', self.show_window),
                pystray.MenuItem('Hide', self.hide_window),
                pystray.MenuItem('Exit', self.exit_app)
            )
            self.tray_icon = pystray.Icon(
                "AutoBrightness", self.create_icon_image(),
                "Auto Brightness", menu=menu
            )
            print("[OK] Tray icon ready")
            self.tray_icon.run()
        except Exception as e:
            print(f"[ERROR] Tray error: {e}")
        finally:
            print("[INFO] Tray thread ended")

    def show_window(self, icon=None, item=None):
        self.deiconify()
        self.lift()
        self.focus()

    def hide_window(self, icon=None, item=None):
        self.withdraw()

    def exit_app(self, icon=None, item=None):
        """Called from pystray thread — hand off to main thread to avoid deadlock."""
        self.should_exit = True
        self.after(0, self._do_exit)

    def _do_exit(self):
        """Shutdown on the Tkinter main thread."""
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass

        if self.running:
            self.running = False
            self.controller.stop()
            if self.working_thread and self.working_thread.is_alive():
                self.working_thread.join(timeout=2)

        os._exit(0)

    def minimize_to_tray(self):
        self.hide_window()

    # ── Settings ──────────────────────────────────────────────────────────────
    def load_settings(self):
        try:
            interval = self.controller.config.get('update_interval', 1.0)
            self.interval_slider.set(interval)
            self.interval_label.configure(text=f"{interval:.1f}s")
        except Exception as e:
            print(f"Error loading interval: {e}")

        try:
            if self.auto_start_manager.is_enabled():
                self.autostart_checkbox.select()
            else:
                self.autostart_checkbox.deselect()
        except Exception as e:
            print(f"Error loading autostart state: {e}")

    def on_interval_change(self, val):
        interval = float(val)
        self.interval_label.configure(text=f"{interval:.1f}s")
        self.controller.config['update_interval'] = interval
        self.controller.save_config()

    def on_autostart_change(self):
        if self.autostart_checkbox.get():
            success = self.auto_start_manager.enable()
            if not success:
                print("[WARN] Failed to enable autostart")
                self.autostart_checkbox.deselect()
        else:
            self.auto_start_manager.disable()

    # ── Controller ────────────────────────────────────────────────────────────
    def start_controller(self):
        if self.running:
            return
        try:
            self.running = True
            self.start_button.configure(state="disabled", fg_color=_BTN_MUTED, text_color=_TEXT_MUTED)
            self.stop_button.configure(state="normal", fg_color=_RED, hover_color="#dc2626", text_color="#ffffff")
            self.status_label.configure(text="Running", text_color=_AMBER)
            self.status_dot.configure(text_color=_AMBER)
            self.interval_slider.configure(state="disabled")

            self.working_thread = Thread(
                target=self._run_controller_thread, daemon=True
            )
            self.working_thread.start()
            print("[OK] Brightness control started")
        except Exception as e:
            print(f"[ERROR] {e}")
            self.running = False
            self.start_button.configure(state="normal", fg_color=_ACCENT, text_color="#ffffff")
            self.stop_button.configure(state="disabled", fg_color=_BTN_MUTED, text_color=_TEXT_MUTED)
            self.status_label.configure(text="Error", text_color=_RED)
            self.status_dot.configure(text_color=_RED)

    def _run_controller_thread(self):
        try:
            self.controller.start_continuous_adjustment()
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            self.running = False

    def stop_controller(self):
        if not self.running:
            return

        self.running = False
        self.controller.stop()

        if self.working_thread and self.working_thread.is_alive():
            self.working_thread.join(timeout=2)

        self.start_button.configure(state="normal", fg_color=_ACCENT, text_color="#ffffff")
        self.stop_button.configure(state="disabled", fg_color=_BTN_MUTED, text_color=_TEXT_MUTED)
        self.status_label.configure(text="Idle", text_color=_TEXT_MUTED)
        self.status_dot.configure(text_color=_GREEN)
        self.interval_slider.configure(state="normal")
        print("[OK] Brightness control stopped")


if __name__ == '__main__':
    app = BrightnessGUI()
    app.mainloop()
