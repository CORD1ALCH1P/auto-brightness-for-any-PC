import screen_brightness_control as sbc
import datetime
from datetime import date
from threading import Timer



class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

def check():
    current_date_time = datetime.datetime.now()
    current_time = current_date_time.time()
    global time_night
    time_night = datetime.time(15, 0, 0)#время для ночь кода выключать 75%
    global time_day
    time_day = datetime.time(12, 0, 0)#время дял включения 75%
    global brightness
    brightness = sbc.get_brightness()# получаем яркость монитора
    global primary
    primary = sbc.get_brightness(display=0)# получаем яркость главного монитора
    print(current_time)
    print('check')
    if current_time < time_day:
        sbc.set_brightness(50)
    elif current_time < time_night:
        sbc.set_brightness(75)
    else:
        sbc.set_brightness(25)
for monitor in sbc.list_monitors():
    print(monitor, ':', sbc.get_brightness(display=monitor), '%')

if __name__ == '__main__':
    RepeatTimer(120, check).start()
