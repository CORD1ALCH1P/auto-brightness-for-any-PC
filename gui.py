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
        self.geometry("400x330")
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
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(
            main_frame,
            text="Auto Brightness",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(0, 15))

        status_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            status_frame,
            text="Status:",
            font=ctk.CTkFont(size=12)
        ).pack(side="left")

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Idle",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#90EE90"
        )
        self.status_label.pack(side="left", padx=(10, 0))

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 20))

        self.start_button = ctk.CTkButton(
            button_frame,
            text="Start",
            command=self.start_controller,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.start_button.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.stop_button = ctk.CTkButton(
            button_frame,
            text="Stop",
            command=self.stop_controller,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            state="disabled",
            fg_color="#444444"
        )
        self.stop_button.pack(side="left", fill="both", expand=True)

        interval_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        interval_frame.pack(fill="x")

        ctk.CTkLabel(
            interval_frame,
            text="Update interval:",
            font=ctk.CTkFont(size=11)
        ).pack(anchor="w")

        slider_frame = ctk.CTkFrame(interval_frame, fg_color="transparent")
        slider_frame.pack(fill="x", pady=(5, 0))

        self.interval_slider = ctk.CTkSlider(
            slider_frame,
            from_=0.5,
            to=10,
            number_of_steps=95,
            command=self.on_interval_change,
            height=20
        )
        self.interval_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.interval_label = ctk.CTkLabel(
            slider_frame,
            text="1.0s",
            font=ctk.CTkFont(size=11),
            width=35
        )
        self.interval_label.pack(side="left")

        autostart_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        autostart_frame.pack(fill="x", pady=(18, 0))

        self.autostart_checkbox = ctk.CTkCheckBox(
            autostart_frame,
            text="Start with Windows",
            command=self.on_autostart_change,
            font=ctk.CTkFont(size=11)
        )
        self.autostart_checkbox.pack(anchor="w")

    def create_icon_image(self):
        img = Image.new('RGB', (64, 64), color='#1f6aa5')
        draw = ImageDraw.Draw(img)

        center = 32
        radius = 20
        draw.ellipse([center-radius, center-radius, center+radius, center+radius],
                     fill='#FFD700', outline='#FFA500', width=2)

        for i in range(8):
            angle = (i * 45) * math.pi / 180
            x1 = center + int((radius-3) * math.cos(angle))
            y1 = center + int((radius-3) * math.sin(angle))
            x2 = center + int((radius+8) * math.cos(angle))
            y2 = center + int((radius+8) * math.sin(angle))
            draw.line([(x1, y1), (x2, y2)], fill='#FFA500', width=2)

        return img

    def start_tray_thread(self):
        """Start tray in separate thread"""
        self.tray_thread = Thread(target=self.setup_tray, daemon=False)
        self.tray_thread.start()

    def setup_tray(self):
        """Setup tray icon"""
        try:
            print("[INFO] Creating tray icon...")
            icon = self.create_icon_image()

            menu = pystray.Menu(
                pystray.MenuItem('Show', self.show_window),
                pystray.MenuItem('Hide', self.hide_window),
                pystray.MenuItem('Exit', self.exit_app)
            )

            self.tray_icon = pystray.Icon(
                "AutoBrightness",
                icon,
                "Auto Brightness",
                menu=menu
            )

            print("[OK] Tray icon ready")
            self.tray_icon.run()

        except Exception as e:
            print(f"[ERROR] Tray error: {e}")
        finally:
            print("[INFO] Tray thread ended")

    def show_window(self, icon=None, item=None):
        """Show window from tray"""
        self.deiconify()
        self.lift()
        self.focus()
        print("[OK] Window shown")

    def hide_window(self, icon=None, item=None):
        """Hide to tray"""
        self.withdraw()
        print("[OK] Hidden to tray")

    def exit_app(self, icon=None, item=None):
        """Called from pystray thread — schedule shutdown on main thread to avoid deadlock"""
        print("[INFO] Exit requested from tray menu")
        self.should_exit = True
        # Schedule the actual exit on the Tkinter main thread.
        # Calling tray_icon.stop() from within a pystray callback deadlocks,
        # so we hand off to the main thread and return immediately.
        self.after(0, self._do_exit)

    def _do_exit(self):
        """Perform complete shutdown on the main Tkinter thread"""
        print("[INFO] Performing exit...")

        # Stop tray icon — safe to call from main thread
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception as e:
                print(f"[WARN] Tray stop error: {e}")

        # Stop brightness controller directly (skip GUI updates, we're quitting)
        if self.running:
            self.running = False
            self.controller.stop()
            if self.working_thread and self.working_thread.is_alive():
                self.working_thread.join(timeout=2)

        print("[OK] Exiting process")
        os._exit(0)

    def minimize_to_tray(self):
        """Minimize on close button"""
        self.hide_window()

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

    def start_controller(self):
        try:
            if self.running:
                return

            self.running = True
            self.start_button.configure(state="disabled", fg_color="#444444")
            self.stop_button.configure(state="normal", fg_color="#FF6B6B")
            self.status_label.configure(text="Running", text_color="#FFD700")
            self.interval_slider.configure(state="disabled")

            self.working_thread = Thread(
                target=self._run_controller_thread,
                daemon=True
            )
            self.working_thread.start()
            print("[OK] Brightness control started")
        except Exception as e:
            print(f"[ERROR] {e}")
            self.running = False
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.status_label.configure(text="Error", text_color="#FF6B6B")

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

        self.start_button.configure(state="normal", fg_color="#1f6aa5")
        self.stop_button.configure(state="disabled", fg_color="#444444")
        self.status_label.configure(text="Idle", text_color="#90EE90")
        self.interval_slider.configure(state="normal")
        print("[OK] Brightness control stopped")

if __name__ == '__main__':
    app = BrightnessGUI()
    app.mainloop()
