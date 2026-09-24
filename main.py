import sys
import math

# ---------------------------------------------------------------------------
# 1. INITIALISATION
# ---------------------------------------------------------------------------
width, height = [int(i) for i in input().split()]

my_shack_x = -1
my_shack_y = -1

for y in range(height):
    line = input()
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

    # --- LECTURE DES ARBRES ---
    trees_count = int(input())
    trees_with_fruits = []

    # NOUVEAU : On garde en mémoire toutes les positions des arbres (pour ne pas planter dessus)
    all_trees_positions = set()
    # NOUVEAU : On compte combien d'arbres on a près de notre cabane (distance <= 2)
    trees_near_shack = {"PLUM": 0, "LEMON": 0, "APPLE": 0, "BANANA": 0}

    for i in range(trees_count):
        inputs = input().split()
        _type = inputs[0]
        x = int(inputs[1])
        y = int(inputs[2])
        size = int(inputs[3])
        health = int(inputs[4])
        fruits = int(inputs[5])
        cooldown = int(inputs[6])

        all_trees_positions.add((x, y))

        # Est-ce que cet arbre est un "arbre de notre verger" (proche de la cabane) ?
        if abs(x - my_shack_x) + abs(y - my_shack_y) <= 2:
            trees_near_shack[_type] += 1

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

    # === MODULE 1 : ENTRAÎNEMENT ===
    target_speed, target_carry, target_harvest = 2, 2, 1
    total_trolls = len(my_trolls)

    cost_plums = total_trolls + (target_speed ** 2)
    cost_lemons = total_trolls + (target_carry ** 2)
    cost_apples = total_trolls + (target_harvest ** 2)

    recruiter_id = min([t["id"] for t in my_trolls]) if my_trolls else -1
    is_recruiting_phase = (total_trolls < 5) and (current_turn <= 180)

    if is_recruiting_phase and my_plums >= cost_plums and my_lemons >= cost_lemons and my_apples >= cost_apples:
        actions.append(f"TRAIN {target_speed} {target_carry} {target_harvest} 0")

    # === MODULE 2 : DÉTECTION DU DÉSÉQUILIBRE (VERGER) ===
    # On identifie les fruits qui nous manquent ET qui n'ont pas d'arbres près de chez nous
    fruits_to_plant = []
    missing_plums = max(0, cost_plums - my_plums)
    missing_lemons = max(0, cost_lemons - my_lemons)
    missing_apples = max(0, cost_apples - my_apples)

    if is_recruiting_phase:
        # Si on a besoin de prunes mais qu'on a moins de 2 pruniers près de la cabane : ALERTE INFÉRIORITÉ
        if missing_plums > 0 and trees_near_shack["PLUM"] < 2:
            fruits_to_plant.append("PLUM")
        if missing_lemons > 0 and trees_near_shack["LEMON"] < 2:
            fruits_to_plant.append("LEMON")
        if missing_apples > 0 and trees_near_shack["APPLE"] < 2:
            fruits_to_plant.append("APPLE")

    # === MODULE 3 : ACTIONS DES TROLLS ===
    for troll in my_trolls:
        troll_id = troll["id"]
        tx, ty = troll["x"], troll["y"]
        is_full = troll["carried"] >= troll["capacity"]
        is_carrying = troll["carried"] > 0
        dist_to_shack = abs(tx - my_shack_x) + abs(ty - my_shack_y)

        is_recruiter = (troll_id == recruiter_id) and is_recruiting_phase

        if is_recruiter:
            m_plums = max(0, missing_plums - troll["carry_plum"])
            m_lemons = max(0, missing_lemons - troll["carry_lemon"])
            m_apples = max(0, missing_apples - troll["carry_apple"])
            if is_carrying and m_plums == 0 and m_lemons == 0 and m_apples == 0:
                is_full = True  # Rentre immédiatement si on a tout le nécessaire !

        # NOUVEAU --- CAS A : LA PLANTATION ---
        action_assigned = False
        tree_on_current_tile = (tx, ty) in all_trees_positions

        # Si le troll est près de la cabane (mais pas dessus) ET sur une case d'herbe vide
        if 1 <= dist_to_shack <= 2 and not tree_on_current_tile:
            # On vérifie si le troll porte un fruit "en infériorité" qu'il faut planter
            for f_type in fruits_to_plant:
                if f_type == "PLUM" and troll["carry_plum"] > 0:
                    actions.append(f"PLANT {troll_id} PLUM")
                    action_assigned = True
                    break
                elif f_type == "LEMON" and troll["carry_lemon"] > 0:
                    actions.append(f"PLANT {troll_id} LEMON")
                    action_assigned = True
                    break
                elif f_type == "APPLE" and troll["carry_apple"] > 0:
                    actions.append(f"PLANT {troll_id} APPLE")
                    action_assigned = True
                    break

        if action_assigned:
            continue  # Passe au troll suivant si on a planté un arbre !

        # --- CAS B : Retour à la cabane ---
        if is_full or (is_carrying and len(trees_with_fruits) == 0):
            if dist_to_shack <= 1:
                actions.append(f"DROP {troll_id}")
            else:
                actions.append(f"MOVE {troll_id} {my_shack_x} {my_shack_y}")

        # --- CAS C : Recherche de nourriture ---
        else:
            if tree_on_current_tile and any(t["x"] == tx and t["y"] == ty for t in trees_with_fruits):
                actions.append(f"HARVEST {troll_id}")
            else:
                best_tree = None

                # Le Recruteur filtre par priorité
                if is_recruiter:
                    needed_types = []
                    if missing_plums > 0: needed_types.append("PLUM")
                    if missing_lemons > 0: needed_types.append("LEMON")
                    if missing_apples > 0: needed_types.append("APPLE")

                    priority_trees = [t for t in trees_with_fruits if t["type"] in needed_types]
                    if len(priority_trees) > 0:
                        best_tree = min(priority_trees, key=lambda t: abs(t["x"] - tx) + abs(t["y"] - ty))

                # Ouvrier (ou si recruteur ne trouve pas son fruit)
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