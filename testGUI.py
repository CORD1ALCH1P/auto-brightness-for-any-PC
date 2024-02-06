import cv2
import screen_brightness_control as sbc
import tkinter as tk

def calculate_brightness(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brightness = int(gray.mean())
    return brightness

def set_brightness():
    global max_val, pre_max_val, half_val, low_val, min_val
    brightness = sbc.get_brightness(display=0)
    brightness_label.config(text=f"Brightness: {brightness}")

    if brightness > 90:
        sbc.set_brightness(max_val)
    elif 80 <= brightness <= 90:
        sbc.set_brightness(pre_max_val)
    elif 70 <= brightness <= 80:
        sbc.set_brightness(half_val)
    elif 50 <= brightness <= 70:
        sbc.set_brightness(low_val)
    else:
        sbc.set_brightness(min_val)

def update_max(value):
    global max_val
    max_val = int(value)

def update_pre_max(value):
    global pre_max_val
    pre_max_val = int(value)

def update_half(value):
    global half_val
    half_val = int(value)

def update_low(value):
    global low_val
    low_val = int(value)

def update_min(value):
    global min_val
    min_val = int(value)

def main():
    brightness = sbc.get_brightness(display=0)
    print(f"Primary Monitor Brightness: {brightness}")

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        brightness = calculate_brightness(frame)
        brightness_label.config(text=f"Brightness: {brightness}")
        set_brightness()
        root.update_idletasks()
        root.update()

    cap.release()
    cv2.destroyAllWindows()

root = tk.Tk()
root.title("Brightness Control")

max_scale = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, label="Max", command=update_max)
pre_max_scale = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, label="Pre Max", command=update_pre_max)
half_scale = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, label="Half", command=update_half)
low_scale = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, label="Low", command=update_low)
min_scale = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, label="Min", command=update_min)
brightness_label = tk.Label(root, text="Brightness: ")

max_scale.pack()
pre_max_scale.pack()
half_scale.pack()
low_scale.pack()
min_scale.pack()
brightness_label.pack()

if __name__ == "__main__":
    main()
