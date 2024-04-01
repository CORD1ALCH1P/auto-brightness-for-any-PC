import tkinter as tk
from tkinter import ttk


def update_labels(value, label):
    label.config(text=str(int(float(value))))


def apply_values():
    var1 = slider1.get()
    var2 = slider2.get()
    var3 = slider3.get()
    var4 = slider4.get()
    var5: float = slider5.get()

    print("Values applied:")
    print("Variable 1:", var1)
    print("Variable 2:", var2)
    print("Variable 3:", var3)
    print("Variable 4:", var4)
    print("Variable 5:", var5)
    import cv2
    import screen_brightness_control as sbc

    def calculate_brightness(frame):
        # converting frame to gray
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate
        brightness = int(gray.mean())

        return brightness

    def main():

        brightness = sbc.get_brightness()  # get brightness of primary monitor
        global primary_monitor  # bad-coder)
        primary_monitor = sbc.get_brightness(display=0)  # get brightness of primary monitor
        print(primary_monitor)

        # init web-cam
        cap = cv2.VideoCapture(0)

        while True:
            # capture frame from web-camera
            ret, frame = cap.read()

            # get level of AO brightness
            brightness = calculate_brightness(frame)

            # print level AO brightness
            print(f"Brightness: {brightness}")

            # here you can tune your own settings (sry for if logic)
            if brightness > 90:
                sbc.set_brightness(var1)
            elif 80 <= brightness <= 90:
                sbc.set_brightness(var2)
            elif 70 <= brightness <= 80:
                sbc.set_brightness(var3)
            elif 50 <= brightness <= 70:
                sbc.set_brightness(var4)
            else:
                sbc.set_brightness(var5)

            print(sbc.get_brightness(display=0))
            # 'q' for exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # clear resources
        cap.release()
        cv2.destroyAllWindows()

    if __name__ == "__main__":
        main()


root = tk.Tk()
root.title("Slider App")

# Создаем и настраиваем ползунки
slider1 = ttk.Scale(root, from_=0, to=100, length=200, orient="horizontal",
                    command=lambda value: update_labels(value, label1))
slider1.pack()
label1 = ttk.Label(root, text="0")
label1.pack()

slider2 = ttk.Scale(root, from_=0, to=100, length=200, orient="horizontal",
                    command=lambda value: update_labels(value, label2))
slider2.pack()
label2 = ttk.Label(root, text="0")
label2.pack()

slider3 = ttk.Scale(root, from_=0, to=100, length=200, orient="horizontal",
                    command=lambda value: update_labels(value, label3))
slider3.pack()
label3 = ttk.Label(root, text="0")
label3.pack()

slider4 = ttk.Scale(root, from_=0, to=100, length=200, orient="horizontal",
                    command=lambda value: update_labels(value, label4))
slider4.pack()
label4 = ttk.Label(root, text="0")
label4.pack()

slider5 = ttk.Scale(root, from_=0, to=100, length=200, orient="horizontal",
                    command=lambda value: update_labels(value, label5))
slider5.pack()
label5 = ttk.Label(root, text="0")
label5.pack()

# Создаем кнопку "Применить"
apply_button = ttk.Button(root, text="Применить", command=apply_values)
apply_button.pack()



root.mainloop()
