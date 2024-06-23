import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
import time
import screen_brightness_control as sbc
import threading


class BrightnessControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Brightness Control")
        self.root.geometry("400x400")

        self.sliders = []
        self.values = []
        self.labels = []

        for i in range(5):
            frame = ttk.Frame(root)
            frame.pack(fill='x', pady=5)

            label = ttk.Label(frame, text=f'brightness {i + 1} value:')
            label.pack(side='left')

            value_label = ttk.Label(frame, text='0')
            value_label.pack(side='left', padx=10)
            self.labels.append(value_label)

            slider = ttk.Scale(frame, from_=0, to=100, orient='horizontal',
                               command=lambda val, index=i: self.update_label(val, index))
            slider.set((i + 1) * 20)
            slider.pack(fill='x', padx=10)

            self.sliders.append(slider)
            self.values.append(slider.get())

        self.apply_button = ttk.Button(root, text="Apply", command=self.apply_values)
        self.apply_button.pack(pady=10)

        self.running = False

    def update_label(self, value, index):
        self.labels[index].config(text=str(int(float(value))))

    def apply_values(self):
        self.values = [slider.get() for slider in self.sliders]
        if not self.running:
            self.running = True
            threading.Thread(target=self.update_brightness).start()

    def get_camera_brightness(self):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return None

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        brightness = hsv[:, :, 2].mean()
        return brightness

    def update_brightness(self):
        while self.running:
            brightness = self.get_camera_brightness()
            if brightness is not None:

                env_brightness = np.clip((brightness / 255) * 100, 0, 100)

                monitor_brightness = np.interp(env_brightness, [0, 25, 50, 75, 100], self.values)
                sbc.set_brightness(int(monitor_brightness))
            time.sleep(3)

    def stop(self):
        self.running = False


if __name__ == "__main__":
    root = tk.Tk()
    app = BrightnessControlApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop)
    root.mainloop()
