import time
import pyautogui as pag

while True:
    pag.doubleClick(720, 900)
    pag.drag(xOffset=0, yOffset=10, duration=0.1, button="left")

    time.sleep(295)
