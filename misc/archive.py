import time
import pyautogui as pag
import cv2 as cv
import numpy as np
import random
from shapely.geometry import Point

# limited time event
def train_yetis():
    pag.doubleClick(79, 1002)
    time.sleep(.1)
    pag.leftClick(583, 826)
    time.sleep(.1)
    pag.moveTo(634, 1016)
    pag.drag(xOffset=-300, yOffset=0, duration=0.25, button="left")
    time.sleep(.1)
    for i in range(0, 6):
        pag.leftClick(758, 983)
    time.sleep(.1)
    pag.doubleClick(61, 830)
    time.sleep(.1)
    pag.doubleClick(61, 830)
    time.sleep(.1)

# template matching, doesn't work too great
def find_button(ref_img, threshold=0.8):
    ss = pag.screenshot()
    ss = np.array(ss)
    ss = cv.cvtColor(ss, cv.COLOR_RGB2BGR)

    ref = cv.imread(ref_img, cv.IMREAD_COLOR)
    result = cv.matchTemplate(ss, ref, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

    if max_val >= threshold:
        button_x = max_loc[0] + ref.shape[1] // 2
        button_y = max_loc[1] + ref.shape[0] // 2
        return (button_x / 2, button_y / 2)
    else:
        return None

# limited time event
def attack_supayetis(results, detected_objects, border_polygons) -> int:
    th = None
    archertowers = []

    for obj in detected_objects:
        if obj.startswith("th_"):
            th = obj[3]
        elif obj.startswith("archertower"):
            archertowers.append(obj)

    if len(archertowers) == 0:
        print("archer towers too high level, skipping")
        return 0

    if th == None or int(th[-1]) > 7 or (th.endswith('7') and len(archertowers) < 2):
        print("th undetected or above 7, skipping")
        return 0
    
    archertowers.sort()
    
    archertower_loc = results[detected_objects.index(archertowers[-1])].boxes.xywh
    archertower_center = Point(archertower_loc[0][0] / 2 + vars.s_area['left'], archertower_loc[0][1] / 2 + vars.s_area['top'])
    archertower_center_loc = [int(archertower_center.x), int(archertower_center.y)]

    # lightning archer tower
    pag.doubleClick(*vars.lightning)
    time.sleep(.1)
    pag.doubleClick(*archertower_center_loc)
    pag.doubleClick(*archertower_center_loc)
    time.sleep(.5)
    pag.leftClick(*vars.yetis)

    pag.doubleClick(*vars.yetis)

    # placing troops on border
    counter = 0

    valid_points = []

    for poly in border_polygons:
        coords = list(poly.exterior.coords)
        valid_points.extend(coords)

    for i in range(0, 6):
        x, y = random.choice(valid_points)
        screen_x = int(x / 2 + vars.s_area['left'])
        screen_y = int(y / 2 + vars.s_area['top'])
        
        pag.leftClick(screen_x, screen_y)

    time.sleep(3)

    return 1

# get trophy count
def get_trophies():
    counter = 0
    trophies = -1
    ### change trophy range according to town hall / personal pref
    while (trophies < 800 or trophies > 1250) and counter < 2:
        try:
            trophies = int(text_scan(vars.t_area))
            counter += 1
        except:
            print("failed to read trophies, trying again")
            trophies = -1
            counter += 1

    if trophies != -1:
        return trophies
    else:
        pag.doubleClick(92, 728)
        time.sleep(.1)
        pag.leftClick(70, 705)
        time.sleep(.3)
        try:
            trophies = int(text_scan(vars.big_t_area))
        except:
            trophies = 1000

    return trophies
