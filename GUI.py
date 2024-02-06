from tkinter import *
from tkinter import ttk

root = Tk()  # создаем корневой объект - окно
root.title("Приложение на Tkinter")  # устанавливаем заголовок окна
root.geometry("400x550+600+100")  # устанавливаем размеры окна
root.resizable(False, False)    # фиксированый размер окна

# Настройки оформления загаловка
root.title("Auto Brightness settings")   # Загаловок окна
# root.iconbitmap(default="favicon.ico")   # Для иконки отображаемой в загаловке

# Содержимое
label = Label(text="GUI AUTO BRIGHTNESS")  # создаем текстовую метку
label.pack()  # размещаем метку в окне

btn = ttk.Button(text="Click") # создаем кнопку из пакета ttk
btn.pack()    # размещаем кнопку в окне

root.mainloop()