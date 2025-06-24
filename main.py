import time
import vars
import pyautogui as pag
from core import *

pag.FAILSAFE = True

init(attack_strat="dragons", troop_cap=200, heroes=2)

ct = 0
while True:
    get_state()
    print(f"State: {vars.state}")

    if ct == 8:
        for i in range(0, 5):
            drop()
        ct = 0
    else:
        search()
        get_state()
        ct += 1
        print("attacking in:")
        for i in range(0, 1):
            print(abs(i - 5))
            time.sleep(1)
