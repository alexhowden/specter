import numpy as np
import pyautogui as pag
import time
import mss
from shapely.geometry import Polygon, Point
from ultralytics import YOLO
import cv2 as cv
import random
import pytesseract
import re

import vars

# return img of area
def get_scr(area):
    with mss.mss() as sct:
        ss = sct.grab(area)
        img = np.array(ss)
        img = img[:, :, :3]
        
        return img

# scan part of the screen for words/numbers
def text_scan(area):
    img = get_scr(area)

    if area in vars.l_area:
        raw_text = pytesseract.image_to_string(img)

        lines = raw_text.strip().splitlines()
        loot = [int(re.sub(r'\D', '', line)) for line in lines if re.search(r'\d', line)]
        return loot

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    gray = cv.equalizeHist(gray)
    gray = cv.bitwise_not(gray)
    _, thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

    resized = cv.resize(thresh, None, fx=4, fy=4, interpolation=cv.INTER_LINEAR)
    config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'

    return pytesseract.image_to_string(resized, config=config)
    
# get current state of the game
def get_state():
    img = get_scr(vars.s_area)

    model = YOLO("models/yolo11_state.pt")
    
    results = model.predict(source=img, line_width=3, verbose=False, conf=0.5)[0]
    detected_objects = [model.names[int(c)] for c in results.boxes.cls]

    if 'attack' in detected_objects:
        vars.state = 'home'
        try:
            # collect resources
            gold_loc = results[detected_objects.index('gold')].boxes.xywh
            elixir_loc = results[detected_objects.index('elixir')].boxes.xywh
            pag.doubleClick(gold_loc[0][0] / 2 + vars.s_area['left'], gold_loc[0][1] / 2 + vars.s_area['top'])
            pag.doubleClick(elixir_loc[0][0] / 2 + vars.s_area['left'], elixir_loc[0][1] / 2 + vars.s_area['top'])
        except ValueError:
            pass
        
    elif 'next' in detected_objects:
        vars.state = 'searching'
    elif 'end' in detected_objects:
        vars.state = 'attacking'
    else:
        vars.state = 'unknown'

    return results, detected_objects

# initialization function
def init(attack_strat="dragons", troop_cap=200, heroes=1):
    vars.attack_strat = attack_strat
    vars.troop_cap = troop_cap
    vars.heroes = heroes

    results, detected_objects = get_state()

    if vars.state == 'home':
        loc = results[detected_objects.index('attack')].boxes.xywh
    elif vars.state == 'searching' or vars.state == 'attacking':
        loc = results[detected_objects.index('end')].boxes.xywh
    else:
        print(f"Invalid state: {vars.state}")
        exit()
    
    x = loc[0][0] / 2 + vars.s_area['left']
    vars.size = 2 if x > 80 else 1 if x > 60 else 0

# start searching for a base
def start_search():
    if vars.state == 'home':
        pag.leftClick(vars.attack_loc[vars.size][0] + 50, vars.attack_loc[vars.size][1] - 50)
        pag.leftClick(*vars.attack_loc[vars.size])
        time.sleep(.1)
        pag.leftClick(*vars.find_loc[vars.size])
    elif vars.state == 'searching' or vars.state == 'attacking':
        pag.doubleClick(*vars.next_loc[vars.size])
    else:
        print("not at home or searching")
        exit()

    vars.state = 'searching'
    time.sleep(vars.search_timer)

# request troops
def request_troops():
    pag.leftClick(79, 1002)
    time.sleep(.1)
    pag.leftClick(802, 1021)
    time.sleep(.1)
    pag.leftClick(551, 964)

# drop trophies if over threshold
def drop():
    start_search()
    vars.state = 'attacking'

    try:
        pag.leftClick(*vars.lightning)
        x, y = vars.s_area['left'] + vars.s_area['width'] / 2, vars.s_area['top'] + vars.s_area['height'] / 2
        pag.leftClick(x, y)
        pag.leftClick(*vars.end_loc[vars.size])
        time.sleep(.1)
        pag.leftClick(540, 945)
        time.sleep(.3)
        pag.leftClick(*vars.return_loc)

        time.sleep(1.2)
        vars.state = 'home'
    except ValueError as err:
        print(err)

# search for base that meets criteria
def search():
    start_search()
    tried = 0

    while vars.state == 'searching':
        loot = text_scan(vars.l_area[vars.size])
        print(f"Loot: {loot}")

        if len(loot) < 2 and tried < 4:
            print("trying again")
            tried += 1
            continue
        elif tried == 4:
            print("couldn't detect loot, attacking anways")
            ## TODO: change with next todo
            loot = [vars.loot_threshold, 0]

        # TODO: change loot threshold here
        if sum(loot) < vars.loot_threshold:
            print("loot too low, skipping")
            search()
            time.sleep(3)
        else:
            print("sufficient loot")
            attack()

# main attack function
def attack():
    img = get_scr(vars.s_area)
    model = YOLO("models/yolo11_attack.pt")
    results = model.predict(source=img, show=vars.show_model, line_width=2, verbose=False, task="segment", conf=0.6)[0]
    detected_objects = [model.names[int(c)] for c in results.boxes.cls]

    border_polygons = []

    for i, cls in enumerate(results.boxes.cls):
        class_name = model.names[int(cls)]
        if class_name == "border":
            mask = results.masks.xy[i]
            poly = Polygon(mask)
            if poly.is_valid:
                border_polygons.append(poly)
            
    if len(border_polygons) == 0:
        if vars.err_ct > 4:
            exit()
        vars.err_ct += 1
        print("no borders detected, skipping")
        return
    else:
        vars.err_ct = 0
    
    vars.state = 'attacking'
    try:
        if vars.attack_strat == "dragons":
            if attack_dragons(results, detected_objects, border_polygons) == 0:
                return
        elif vars.attack_strat == "balloons":
            attack_balloons(results, detected_objects, border_polygons)

        while vars.state == 'attacking':
            time.sleep(5)
            get_state()

        pag.doubleClick(*vars.return_loc)
        time.sleep(1)

    except ValueError as err:
        print(err)

# up to date; returns 0
def attack_dragons(results, detected_objects, border_polygons) -> int:
    th = None
    airdefs = []

    for obj in detected_objects:
        if obj.startswith("th_"):
            th = obj[3]
        elif obj.startswith("airdef_"):
            airdefs.append(obj)

    # if th == None:
    #     print("town hall not detected, skipping")
    #     search()
    #     return
    if len(airdefs) < 2:
        print("air defense(s) not detected, skipping")
        search()
        return

    airdefs.sort()
    selected_airdefs = airdefs[:2]
    side = None

    for airdef in selected_airdefs:
        idx = detected_objects.index(airdef)
        airdef_loc = results[idx].boxes.xywh
        airdef_center = Point(
            airdef_loc[0][0] / 2 + vars.s_area['left'],
            airdef_loc[0][1] / 2 + vars.s_area['top']
        )
        airdef_center_loc = [int(airdef_center.x), int(airdef_center.y)]
        side = int(airdef_center.x > vars.s_area['width'] / 2) if len(airdefs) > 0 else 0
        
        # Lightning on airdef
        pag.doubleClick(*vars.lightning)
        pag.doubleClick(*airdef_center_loc)
        pag.doubleClick(*airdef_center_loc)
        pag.leftClick(*airdef_center_loc)

    # placing troops on border
    pag.doubleClick(*vars.dragons)

    counter = 0
    valid_points = []

    for poly in border_polygons:
        coords = list(poly.exterior.coords)
        valid_points.extend(coords)

    # placing draogns
    side_points = [
        (x, y) for (x, y) in valid_points
        if (side == 0 and int(x / 2) < vars.s_area['width'] / 2) or
            (side == 1 and int(x / 2) >= vars.s_area['width'] / 2)
    ]

    if not side_points:
        side_points = valid_points

    while counter < 6 and side_points:
        x, y = random.choice(side_points)
        screen_x = int(x / 2 + vars.s_area['left'])
        screen_y = int(y / 2 + vars.s_area['top'])
        
        pag.doubleClick(screen_x, screen_y)
        counter += 1
    
    # placing hero
    for h in vars.hero:
        pag.leftClick(*h)
        x, y = random.choice(valid_points)
        screen_x = int(x / 2 + vars.s_area['left'])
        screen_y = int(y / 2 + vars.s_area['top'])
        pag.leftClick(screen_x, screen_y)

    # event goblins
    x, y = random.choice(side_points)
    screen_x = int(x / 2 + vars.s_area['left'])
    screen_y = int(y / 2 + vars.s_area['top'])
    
    pag.doubleClick(vars.slot1)
    pag.doubleClick(screen_x, screen_y)
    pag.doubleClick(screen_x, screen_y)
    pag.doubleClick(screen_x, screen_y)
    pag.doubleClick(screen_x, screen_y)
    pag.doubleClick(screen_x, screen_y)

# may need updating
def attack_balloons(results, detected_objects, border_polygons):
    th = None
    airdefs = []

    for obj in detected_objects:
        if obj.startswith("th_"):
            th = obj[3]
        elif obj.startswith("airdef_"):
            airdefs.append(obj)

    airdefs.sort()

    if len(airdefs) > 2 or th.endswith('7'):
        print("multiple air defenses detected, skipping")
        return
    if len(airdefs) > 0 and airdefs[-1] in ['airdef_4', 'airdef_5']:
        return
    if len(airdefs) == 0 and (th.endswith('5') or th.endswith('6')):
        print("airdef present but not detected, skipping")
        return

    airdef_loc = None
    if len(airdefs) > 0:
        airdef_loc = results[detected_objects.index(airdefs[-1])].boxes.xywh
        airdef_center = Point(airdef_loc[0][0] / 2 + vars.s_area['left'], airdef_loc[0][1] / 2 + vars.s_area['top'])
        airdef_center_loc = [int(airdef_center.x), int(airdef_center.y)]
        print(f"Highest air defense loc: {airdef_center_loc}")

    side = int(airdef_center.x > vars.s_area['width'] / 2) if len(airdefs) > 0 else 0
    print(f"Side: {side}")

    # lightning on air defense
    pag.doubleClick(*vars.lightning)
    time.sleep(.1)
    pag.doubleClick(*airdef_center_loc)
    time.sleep(.5)
    pag.leftClick(*vars.balloons)

    pag.doubleClick(*vars.balloons)

    # placing troops on border
    counter = 0

    valid_points = []

    for poly in border_polygons:
        coords = list(poly.exterior.coords)
        valid_points.extend(coords)

    counter = 0
    while counter < 5:
        x, y = random.choice(valid_points)
        if (side == 0 and int(x / 2) < vars.s_area['width'] / 2) or (side == 1 and int(x / 2) >= vars.s_area['width'] / 2):
            screen_x = int(x / 2 + vars.s_area['left'])
            screen_y = int(y / 2 + vars.s_area['top'])
            
            pag.doubleClick(screen_x, screen_y)
            pag.doubleClick(screen_x, screen_y)
            pag.doubleClick(screen_x, screen_y)
            counter += 1
