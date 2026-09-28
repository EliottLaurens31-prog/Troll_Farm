import sys
import math

# ---------------------------------------------------------------------------
# 1. INITIALISATION ET CARTOGRAPHIE
# ---------------------------------------------------------------------------
width, height = [int(i) for i in input().split()]

my_shack_x = -1
my_shack_y = -1
grid_map = []

for y in range(height):
    line = input()
    grid_map.append(line)
    for x in range(width):
        if line[x] == '0':
            my_shack_x = x
            my_shack_y = y

current_turn = 0
print(f"Ma cabane est en ({my_shack_x}, {my_shack_y})", file=sys.stderr, flush=True)

# ---------------------------------------------------------------------------
# 2. BOUCLE DE JEU
# ---------------------------------------------------------------------------
while True:
    current_turn += 1

    # --- LECTURE DE L'INVENTAIRE ---
    my_plums, my_lemons, my_apples = 0, 0, 0

    for i in range(2):
        plum, lemon, apple, banana, iron, wood = [int(j) for j in input().split()]
        if i == 0:
            my_plums = plum
            my_lemons = lemon
            my_apples = apple

    # --- LECTURE DES ARBRES ET CARTOGRAPHIE EN TEMPS RÉEL ---
    trees_count = int(input())
    trees_with_fruits = []


    for i in range(trees_count):
        inputs = input().split()
        _type = inputs[0]
        x, y = int(inputs[1]), int(inputs[2])
        fruits = int(inputs[5])

        if fruits > 0:
            trees_with_fruits.append({
                "type": _type,
                "x": x, "y": y,
                "fruits": fruits
            })


    # --- LECTURE DES TROLLS ---
    trolls_count = int(input())
    my_trolls = []

    for i in range(trolls_count):
        data = [int(j) for j in input().split()]
        _id = data[0]
        player = data[1]
        x, y = data[2], data[3]
        capacity = data[5]
        carry_plum, carry_lemon, carry_apple, carry_banana = data[8], data[9], data[10], data[11]

        if player == 0:
            my_trolls.append({
                "id": _id, "x": x, "y": y,
                "capacity": capacity,
                "carried": carry_plum + carry_lemon + carry_apple + carry_banana,
                "carry_plum": carry_plum,
                "carry_lemon": carry_lemon,
                "carry_apple": carry_apple
            })

    # ---------------------------------------------------------------------------
    # 3. PRISE DE DÉCISION & CORPS DE L'IA
    # ---------------------------------------------------------------------------
    actions = []
    sorted_trolls = sorted(my_trolls, key=lambda t: t["id"])
    total_trolls = len(sorted_trolls)

    # === MODULE 1 : CALCUL DES BESOINS D'ENTRAÎNEMENT ===
    target_speed, target_harvest,target_carry = 1, 1, 1


    cost_plums = total_trolls + (target_speed ** 2)
    cost_lemons = total_trolls + (target_carry ** 2)
    cost_apples = total_trolls + (target_harvest ** 2)

    # Limite de recrutement (on recrute tant qu'on a le temps de rentabiliser, tour 180)
    is_recruiting_phase = (current_turn <= 180)

    if is_recruiting_phase and my_plums >= cost_plums and my_lemons >= cost_lemons and my_apples >= cost_apples:
        actions.append(f"TRAIN {target_speed} {target_carry} {target_harvest} 0")

    missing_plums = max(0, cost_plums - my_plums)
    missing_lemons = max(0, cost_lemons - my_lemons)
    missing_apples = max(0, cost_apples - my_apples)



    # === MODULE 2 : ACTIONS PAR TROLL===

    for index, troll in enumerate(sorted_trolls):
        troll_id = troll["id"]
        tx, ty = troll["x"], troll["y"]
        is_full = troll["carried"] >= troll["capacity"]
        is_carrying = troll["carried"] > 0
        dist_to_shack = abs(tx - my_shack_x) + abs(ty - my_shack_y)
        space_left_in_bag = troll["capacity"] - troll["carried"]
        m_plums = max(0, missing_plums - troll["carry_plum"])
        m_lemons = max(0, missing_lemons - troll["carry_lemon"])
        m_apples = max(0, missing_apples - troll["carry_apple"])
        if is_carrying and m_plums == 0 and m_lemons == 0 and m_apples == 0:
                is_full = True
        if is_full or (is_carrying and len(trees_with_fruits) == 0):
            if dist_to_shack <= 1:
                actions.append(f"DROP {troll_id}")
            else:
                actions.append(f"MOVE {troll_id} {my_shack_x} {my_shack_y}")
        else:
            current_tree = next((t for t in trees_with_fruits if t["x"] == tx and t["y"] == ty), None)
            if current_tree:
                actions.append(f"HARVEST {troll_id}")
            else:
                best_tree = None

                recruiting_needed = []
                if missing_plums > 0: recruiting_needed.append("PLUM")
                if missing_lemons > 0: recruiting_needed.append("LEMON")
                if missing_apples > 0: recruiting_needed.append("APPLE")

                priority_trees = [t for t in trees_with_fruits if t["type"] in recruiting_needed]
                if len(priority_trees) > 0:
                    best_tree = min(priority_trees, key=lambda t: abs(t["x"] - tx) + abs(t["y"] - ty))

                if best_tree is None and len(trees_with_fruits) > 0:
                    best_tree = min(trees_with_fruits, key=lambda t: abs(t["x"] - tx) + abs(t["y"] - ty))

                if best_tree:
                    actions.append(f"MOVE {troll_id} {best_tree['x']} {best_tree['y']}")
                else:
                    actions.append("WAIT")

    # ---------------------------------------------------------------------------
    # 4. ENVOI DES COMMANDES
    # ---------------------------------------------------------------------------
    if actions:
        print(";".join(actions))
    else:
        print("WAIT")