import cv2
import screen_brightness_control as sbc


def calculate_brightness(frame):
    # converting frame to gray
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Calculate
    brightness = int(gray.mean())

    return brightness

def main():

    brightness = sbc.get_brightness()    # get brightness of primary monitor
    global primary_monitor               # bad-coder)
    primary_monitor = sbc.get_brightness(display=0)   # get brightness of primary monitor
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
            sbc.set_brightness(100)
        elif 80 <= brightness <= 90:
            sbc.set_brightness(80)
        elif 70 <= brightness <= 80:
            sbc.set_brightness(60)
        elif 50 <= brightness <= 70:
            sbc.set_brightness(40)
        else:
            sbc.set_brightness(30)

        print(sbc.get_brightness(display=0))
        # Прерываем цикл, если нажата клавиша 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Освобождаем ресурсы
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
