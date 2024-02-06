import GUIAPP
import subprocess
import cv2
import screen_brightness_control as sbc

# default brightness level settings
max_bright = 100
pre_max_bright = 80
half_bright = 60
low_bright = 40
min_bright = 30

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

    # init web-camera
    cap = cv2.VideoCapture(0)

    while True:
        # capture frame from web-camera
        ret, frame = cap.read()

        # get level of AO brightness
        brightness = calculate_brightness(frame)

        # print level AO brightness
        print(f"Brightness: {brightness}")
        #
        # # here you can tune your own settings (sry for if logic)
        # if brightness > 90:
        #     sbc.set_brightness(max_bright)
        # elif 80 <= brightness <= 90:
        #     sbc.set_brightness(pre_max_bright)
        # elif 70 <= brightness <= 80:
        #     sbc.set_brightness(half_bright)
        # elif 50 <= brightness <= 70:
        #     sbc.set_brightness(low_bright)
        # else:
        #     sbc.set_brightness(min_bright)
        if brightness > 90:
            subprocess.run(["python", "backend_module.py", str(max_bright)])
        elif 80 <= brightness <= 90:
            subprocess.run(["python", "backend_module.py", str(pre_max_bright)])
        elif 70 <= brightness <= 80:
            subprocess.run(["python", "backend_module.py", str(half_bright)])
        elif 50 <= brightness <= 70:
            subprocess.run(["python", "backend_module.py", str(low_bright)])
        else:
            subprocess.run(["python", "backend_module.py", str(min_bright)])

        print(sbc.get_brightness(display=0))

    # Освобождаем ресурсы
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
