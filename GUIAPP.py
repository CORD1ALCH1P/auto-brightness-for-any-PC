import tkinter as tk
from tkinter import ttk
import subprocess


class SliderApp(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Настройка яркости")
        self.geometry("400x300")

        # Создаем слайдеры
        self.max_bright_var = tk.DoubleVar()
        self.pre_max_bright_var = tk.DoubleVar()
        self.half_bright_var = tk.DoubleVar()
        self.low_bright_var = tk.DoubleVar()
        self.min_bright_var = tk.DoubleVar()

        self.max_bright_slider = self.create_slider("Максимальная яркость", self.max_bright_var)
        self.pre_max_bright_slider = self.create_slider("Предварительная максимальная яркость", self.pre_max_bright_var)
        self.half_bright_slider = self.create_slider("Половина яркости", self.half_bright_var)
        self.low_bright_slider = self.create_slider("Низкая яркость", self.low_bright_var)
        self.min_bright_slider = self.create_slider("Минимальная яркость", self.min_bright_var)

        # Создаем кнопку для применения изменений
        self.apply_button = tk.Button(self, text="Применить", command=self.apply_changes)
        self.apply_button.pack()

    def create_slider(self, label_text, variable):
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=5)
        label = ttk.Label(frame, text=label_text)
        label.pack(side="left")
        slider = ttk.Scale(frame, from_=0, to=100, orient="horizontal", variable=variable)
        slider.pack(side="right", fill="x", expand=True)
        return slider

    def apply_changes(self):
        max_bright = self.max_bright_var.get()
        pre_max_bright = self.pre_max_bright_var.get()
        half_bright = self.half_bright_var.get()
        low_bright = self.low_bright_var.get()
        min_bright = self.min_bright_var.get()

        # Передаем новые значения переменных в скрипт main.py
        subprocess.run(["python", "backend_module.py", str(max_bright), str(pre_max_bright), str(half_bright), str(low_bright),
                        str(min_bright)])


if __name__ == "__main__":
    root = tk.Tk()
    app = SliderApp(root)
    app.mainloop()
