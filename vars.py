s_area = {"top": 687, "left": 0, "width": 935, "height": 431}
l_area = [{"top": 924, "left": 42, "width": 35, "height": 20},
          {"top": 820, "left": 61, "width": 55, "height": 30},
          {"top": 734, "left": 78, "width": 70, "height": 35}]

t_area = {"top": 740, "left": 90, "width": 38, "height": 14}
big_t_area = {"top": 830, "left": 660, "width": 55, "height": 22}

attack_loc = [[47, 1089],
              [69, 1076],
              [88, 1065]]
end_loc = [[49, 1068],
           [73, 1042],
           [93, 1022]]
next_loc = [[428, 1058],
            [656, 1027],
            [848, 1000]]
find_loc = [[315, 1015],
            [480, 965],
            [630, 920]]
return_loc = [468, 1045]

slot1 = [273, 1072]
slot2 = [316, 1072]
slot3 = [359, 1072]
slot4 = [400, 1072]
slot5 = [440, 1072]

state = None
size = 2

err_ct = 0

lightning = slot5
dragons = slot2

balloons = slot1

th = 9

search_timer = 5

attack_strat = None
troop_cap = None
heroes = None
hero = [slot3, slot4]

loot_threshold = 800000

show_model = False
