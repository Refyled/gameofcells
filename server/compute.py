import random
import math
from collections import defaultdict, Counter

def compute_game_turn(grid_size, numberOfVit, original_grid, cells_moves):
    """
    Compute one turn of the game, with validity checks on moves.

    :param grid_size: (int) size of the NxN grid
    :param numberOfVit: (int) desired total # of vitamins on the board after the turn
    :param original_grid: (list of dict) the initial arrangement of cells
        Example:
        [
            {'x': 2, 'y': 2, 'weight': 5, 'player': 'p1'},
            {'x': 2, 'y': 3, 'weight': 4, 'player': 'p2'},
            {'x': 0, 'y': 0, 'weight': 1, 'player': 'vitamin'}
        ]
    :param cells_moves: (list of dict) describing desired moves, e.g.:
        [
            {
                'x': 2, 'y': 2, 'player': 'p1',
                'move_up': 2, 'move_down': 0, 'move_left': 0, 'move_right': 0, 'move_stay': 3
            },
            ...
        ]

    :return: (move_animation, new_grid)

        * move_animation: list of dict describing each sub-cell's move (for animation)
            [
                {
                    'origin_x': <int>,
                    'origin_y': <int>,
                    'weight': <int>,
                    'direction': 'up'/'down'/'left'/'right'/'stay',
                    'player': <str>,
                    'result': 'survives'/'dies_midway'/'dies_arrival'
                },
                ...
            ]

        * new_grid: the final arrangement of the grid (list of dict)
            [
                {'x': <int>, 'y': <int>, 'weight': <int>, 'player': <str>},
                ...
            ]
    """

    # ------------------------------------------------------------
    # STEP 0: Organize the original grid into a lookup
    #         (x, y, player) -> weight
    # ------------------------------------------------------------
    original_lookup = {}
    for cell in original_grid:
        x, y, w, p = cell['x'], cell['y'], cell['weight'], cell['player']
        # If the same player is present multiple times at the same spot, we sum them up
        # (This depends on your game rules. If your game doesn't allow multiple same-player cells
        # in the same spot, you can just store them directly. For safety, we sum.)
        original_lookup[(x, y, p)] = original_lookup.get((x, y, p), 0) + w

    # We'll also keep track of which cells have "used" a move, so we don't 
    # accidentally let them move twice.
    used_keys = set()  # set of (x,y,player)

    # ------------------------------------------------------------
    # STEP 1: Build sub-cells from valid moves
    # ------------------------------------------------------------
    directions = {
        'up':    (0, -1),
        'down':  (0,  1),
        'left':  (-1, 0),
        'right': (1,  0),
        'stay':  (0,  0)
    }

    # We'll store sub-cells in a list of dict:
    # {
    #   'origin_x': <int>,
    #   'origin_y': <int>,
    #   'x': <int>,  # intended final x (if no collision)
    #   'y': <int>,  # intended final y
    #   'player': <str>,
    #   'weight': <int>,
    #   'direction': 'up'/'down'/'left'/'right'/'stay'
    # }
    sub_cells = []

    # For move_animation building, we also keep a list of all "attempted expansions"
    # in the order they are read from cells_moves (plus any leftover cells that didn't move).
    # We'll fill 'result' later.
    move_animation_expansions = []

    def create_animation_entry(ox, oy, w, d, p):
        return {
            'origin_x': ox,
            'origin_y': oy,
            'weight': w,
            'direction': d,
            'player': p,
            'result': 'survives'  # default (we'll adjust later)
        }

    # Validate each move request
    for move in cells_moves:
        ox, oy = move['x'], move['y']
        pl = move['player']
        key = (ox, oy, pl)

        # Check if a cell with that (x,y,player) exists
        if key not in original_lookup:
            # invalid => ignore
            continue

        # Make sure we haven't used that same cell before
        if key in used_keys:
            # This cell already moved => ignore
            continue

        cell_weight = original_lookup[key]
        # Sum the splits
        up_    = move.get('move_up', 0)
        down_  = move.get('move_down', 0)
        left_  = move.get('move_left', 0)
        right_ = move.get('move_right', 0)
        stay_  = move.get('move_stay', 0)

        total_split = up_ + down_ + left_ + right_ + stay_

        # Check if the total matches the cell's weight
        if total_split != cell_weight:
            # invalid => ignore
            continue

        # Next, check if any of these sub-splits try to move out of bounds
        # For each direction that has w>0, see if final x,y would go out of [0, grid_size-1].
        # If so, it's invalid => ignore this entire move.
        is_invalid_move = False
        move_splits = {
            'up': up_,
            'down': down_,
            'left': left_,
            'right': right_,
            'stay': stay_
        }
        for d_name, w in move_splits.items():
            if w <= 0:
                continue
            dx, dy = directions[d_name]
            final_x = ox + dx
            final_y = oy + dy
            # Check bounds
            if final_x < 0 or final_x >= grid_size or final_y < 0 or final_y >= grid_size:
                is_invalid_move = True
                break

        if is_invalid_move:
            # out of bounds => ignore
            continue

        # If we reach here => the move is valid
        used_keys.add(key)
        # Remove the cell from original_lookup so we don't "stay" it later
        del original_lookup[key]

        # Create sub-cells
        for d_name, w in move_splits.items():
            if w <= 0:
                continue
            dx, dy = directions[d_name]
            final_x = ox + dx
            final_y = oy + dy
            sub_cells.append({
                'origin_x': ox,
                'origin_y': oy,
                'x': final_x,
                'y': final_y,
                'player': pl,
                'weight': w,
                'direction': d_name
            })

            # For animation
            move_animation_expansions.append(create_animation_entry(ox, oy, w, d_name, pl))

    # ------------------------------------------------------------
    # STEP 2: For any cell in original_lookup that wasn't used,
    #         we keep it "as-is" (they stay in place).
    # ------------------------------------------------------------
    for (ox, oy, pl), w in original_lookup.items():
        # That cell didn't move => produce one "stay" sub-cell
        sub_cells.append({
            'origin_x': ox,
            'origin_y': oy,
            'x': ox,
            'y': oy,
            'player': pl,
            'weight': w,
            'direction': 'stay'
        })
        # Also add an animation entry
        move_animation_expansions.append(create_animation_entry(ox, oy, w, 'stay', pl))

    # ------------------------------------------------------------
    # STEP 3: Resolve mid-way collisions (cells crossing paths)
    # ------------------------------------------------------------
    # We'll repeatedly scan for pairs that cross until no more mid-way collisions occur.

    has_midway_collision = True
    while has_midway_collision:
        has_midway_collision = False
        to_remove = set()

        n = len(sub_cells)
        i = 0
        while i < n - 1:
            j = i + 1
            while j < n:
                if i in to_remove:
                    j += 1
                    continue
                if j in to_remove:
                    j += 1
                    continue

                A = sub_cells[i]
                B = sub_cells[j]

                # Condition for mid-way collision:
                #  - A's origin == B's destination
                #  - B's origin == A's destination
                #  - origin != destination
                if (A['origin_x'] == B['x'] and
                    A['origin_y'] == B['y'] and
                    B['origin_x'] == A['x'] and
                    B['origin_y'] == A['y'] and
                    (A['origin_x'], A['origin_y']) != (A['x'], A['y'])):
                    # Mid-way collision
                    has_midway_collision = True
                    to_remove.add(i)
                    to_remove.add(j)

                    # Merge them
                    merged_player, merged_weight = resolve_merge(A, B)

                    # Create a new sub-cell with direction='stay'
                    # We'll place it at B's origin (arbitrary choice)
                    new_sub = {
                        'origin_x': A['origin_x'],
                        'origin_y': A['origin_y'],
                        'x': B['origin_x'],
                        'y': B['origin_y'],
                        'player': merged_player,
                        'weight': merged_weight,
                        'direction': 'stay'
                    }
                    sub_cells.append(new_sub)
                j += 1
            i += 1

        if to_remove:
            sub_cells = [s for idx, s in enumerate(sub_cells) if idx not in to_remove]

    # ------------------------------------------------------------
    # STEP 4: Collisions on final destinations
    # ------------------------------------------------------------
    # Group by final (x,y)
    final_map = defaultdict(list)
    for i, s in enumerate(sub_cells):
        final_map[(s['x'], s['y'])].append(i)

    to_remove = set()
    new_subs = []
    for pos, idxs in final_map.items():
        if len(idxs) < 2:
            continue  # no collision
        # Merge
        group = [sub_cells[i] for i in idxs if i not in to_remove]
        if len(group) < 2:
            continue

        # Step 1: Merge same-player sub-cells first
        accum = defaultdict(int)
        for sc in group:
            accum[sc['player']] += sc['weight']

        # Build a list of (player, weight)
        merges = [(p, w) for p, w in accum.items()]

        # Repeatedly merge until we have 1
        while len(merges) > 1:
            # Sort descending by weight
            merges.sort(key=lambda x: x[1], reverse=True)
            top1 = merges[0]
            top2 = merges[1]
            if top1[1] > top2[1]:
                merges[0] = (top1[0], top1[1] + top2[1])
                merges.pop(1)
            elif top1[1] < top2[1]:
                merges[1] = (top2[0], top2[1] + top1[1])
                merges.pop(0)
            else:
                # tie
                winner_idx = random.choice([0, 1])
                loser_idx = 1 - winner_idx
                winn = merges[winner_idx]
                losr = merges[loser_idx]
                merges[winner_idx] = (winn[0], winn[1] + losr[1])
                merges.pop(loser_idx)

        final_player, final_weight = merges[0]

        for i in idxs:
            to_remove.add(i)

        new_subs.append({
            'origin_x': group[0]['origin_x'],
            'origin_y': group[0]['origin_y'],
            'x': pos[0],
            'y': pos[1],
            'player': final_player,
            'weight': final_weight,
            'direction': group[0]['direction']
        })

    # Remove old
    sub_cells = [s for i, s in enumerate(sub_cells) if i not in to_remove]
    sub_cells.extend(new_subs)

    # ------------------------------------------------------------
    # STEP 5: Create the move_animation array
    #         We have "move_animation_expansions" describing 
    #         every (origin_x, origin_y, weight, direction, player) that was attempted.
    #         We'll see if it "survives" in sub_cells or "dies_midway"/"dies_arrival".
    # ------------------------------------------------------------
    # Build a Counter for final sub_cells
    final_counter = Counter()
    for sc in sub_cells:
        # Each surviving sub-cell can be identified by
        # (origin_x, origin_y, direction, player, weight).
        k = (sc['origin_x'], sc['origin_y'], sc['direction'], sc['player'], sc['weight'])
        final_counter[k] += 1

    # Now, move_animation starts as a copy of expansions, then we fix their 'result'.
    move_animation = []
    for anim_sub in move_animation_expansions:
        key = (anim_sub['origin_x'], 
               anim_sub['origin_y'], 
               anim_sub['direction'], 
               anim_sub['player'], 
               anim_sub['weight'])
        if final_counter[key] > 0:
            # Survives
            anim_sub['result'] = 'survives'
            final_counter[key] -= 1
        else:
            # Died (either mid-way or final)
            # We'll just label them 'dies_arrival' for simplicity,
            # or you could attempt further logic to detect mid-way collisions specifically.
            anim_sub['result'] = 'dies_arrival'

        move_animation.append(anim_sub)

    # ------------------------------------------------------------
    # STEP 6: Add vitamins if needed
    # ------------------------------------------------------------
    vitamins_count = 0
    for sc in sub_cells:
        if sc['player'] == 'vitamin':
            vitamins_count += sc['weight']  # typically = 1

    missing = numberOfVit - vitamins_count
    if missing > 0:
        # find free spots
        occupied = {(sc['x'], sc['y']) for sc in sub_cells}
        all_positions = [(x, y) for x in range(grid_size) for y in range(grid_size)]
        free_positions = [pos for pos in all_positions if pos not in occupied]
        random.shuffle(free_positions)
        to_place = min(missing, len(free_positions))
        for i in range(to_place):
            px, py = free_positions[i]
            sub_cells.append({
                'origin_x': px,
                'origin_y': py,
                'x': px,
                'y': py,
                'player': 'vitamin',
                'weight': 1,
                'direction': 'stay'
            })

    # ------------------------------------------------------------
    # STEP 7: Build the final new_grid
    # ------------------------------------------------------------
    new_grid = []
    for sc in sub_cells:
        new_grid.append({
            'x': sc['x'],
            'y': sc['y'],
            'weight': sc['weight'],
            'player': sc['player']
        })

    return move_animation, new_grid

def resolve_merge(A, B):
    """
    Merge sub-cells A and B that collided mid-way.
    Return (winning_player, combined_weight).
    
    Rules:
    1) If same player => sum up directly
    2) Else heavier wins
    3) If tie => random
    4) Vitamins are always eaten (lowest priority). 
       But if it's a tie (vitamin has weight=1, the other cell has weight=1?), 
       we randomize as well.
    """
    pA, wA = A['player'], A['weight']
    pB, wB = B['player'], B['weight']

    # same player => direct sum
    if pA == pB:
        return pA, wA + wB

    # different players => compare
    if wA > wB:
        return pA, wA + wB
    elif wB > wA:
        return pB, wA + wB
    else:
        # tie => random
        winner = random.choice([pA, pB])
        return winner, wA + wB


def generate_initial_grid(players, grid_size, start_weight, number_of_vitamins):
    """
    Génère une grille de départ pour le jeu.

    :param players: (list[str]) Liste d'identifiants de joueurs, ex. ['p1', 'p2']
    :param grid_size: (int) Taille N de la grille (N x N)
    :param start_weight: (int) Poids de départ pour chaque cellule de joueur
    :param number_of_vitamins: (int) Nombre total de vitamines à placer

    :return: (list[dict]) Liste de cellules, même format que new_grid/original_grid
             ex. [
                {'x': 2, 'y': 2, 'weight': 4, 'player': 'p1'},
                {'x': 3, 'y': 4, 'weight': 4, 'player': 'p2'},
                {'x': 0, 'y': 0, 'weight': 1, 'player': 'vitamin'},
                ...
             ]
    """

    # On va construire un tableau (liste de dictionnaires)
    initial_grid = []

    # Calcul du "centre" (flottant) ; pour une grille 6x6 => centre = (2.5, 2.5)
    cx = (grid_size - 1) / 2.0
    cy = (grid_size - 1) / 2.0

    # Pour éviter les bords et ne pas tomber pile au milieu,
    # on définit un rayon intermédiaire (on laisse 1 case de marge sur les bords).
    # Si grid_size=6, rayon = ~1.5 => on placera les joueurs
    # sur un pseudo-cercle de rayon=1.5 autour du centre.
    radius = max(1.0, (grid_size - 1) / 2.0 - 1)

    n_players = len(players)
    if n_players == 0:
        # S'il n'y a pas de joueurs, on ne place que les vitamines
        pass
    else:
        # Placement "en cercle" des joueurs
        for i, player_id in enumerate(players):
            angle = 2 * math.pi * i / n_players  # Répartition uniforme
            # Calcul de la position flottante
            float_x = cx + radius * math.cos(angle)
            float_y = cy + radius * math.sin(angle)

            # On arrondit
            px = int(round(float_x))
            py = int(round(float_y))

            # On s'assure de rester dans [1, grid_size - 2]
            # pour éviter strictement les bords (0 et grid_size-1).
            px = max(1, min(grid_size - 2, px))
            py = max(1, min(grid_size - 2, py))

            # Ajouter la cellule dans la grille initiale
            initial_grid.append({
                'x': px,
                'y': py,
                'weight': start_weight,
                'player': player_id
            })

    # Maintenant, on place les vitamines (poids=1)
    # On va piocher random dans les cases libres
    occupied = set((c['x'], c['y']) for c in initial_grid)
    all_positions = [(x, y) for x in range(grid_size) for y in range(grid_size)]
    free_positions = [pos for pos in all_positions if pos not in occupied]

    # On mélange au hasard
    random.shuffle(free_positions)

    # On place autant de vitamines que demandé (ou moins s'il n'y a pas assez de cases)
    nb_vitamins_to_place = min(number_of_vitamins, len(free_positions))
    for i in range(nb_vitamins_to_place):
        x_vit, y_vit = free_positions[i]
        initial_grid.append({
            'x': x_vit,
            'y': y_vit,
            'weight': 1,
            'player': 'vitamin'   # identifiant "vitamin"
        })

    return initial_grid