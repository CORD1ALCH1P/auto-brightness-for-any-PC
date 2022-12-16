import screen_brightness_control as sbc
import datetime
from datetime import date
from threading import Timer



class RepeatTimer(Timer):#for timer
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

def check():
    current_date_time = datetime.datetime.now()
    current_time = current_date_time.time()
    global time_night
    time_night = datetime.time(15, 0, 0)#time for night mod 75%/you can change
    global time_day
    time_day = datetime.time(12, 0, 0)#time for off 75%/you can change
    global brightness
    brightness = sbc.get_brightness()# get brightness of monitor
    global primary
    primary = sbc.get_brightness(display=0)# get brightness of prim. monitor
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
    RepeatTimer(120, check).start()#evrey 120 sec. will check

#for .exe format, if you need use pyinstaller -F (file_name);