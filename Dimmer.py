import screen_brightness_control as sbc

brightness = sbc.get_brightness()# get brightness of monitor
global primary
primary = sbc.get_brightness(display=0)# get brightness of prim. monitor
sbc.set_brightness(2)
for monitor in sbc.list_monitors():
    print(monitor, ':', sbc.get_brightness(display=monitor), '%')
#for .exe format, if you need use pyinstaller -F (file_name);