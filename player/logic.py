# logic.py

import random
from collections import defaultdict

class GameLogic:
    def __init__(self, my_player_name, grid_size):
        self.my_player_name = my_player_name
        self.grid_size = grid_size
        self.directions = ['move_up', 'move_down', 'move_left', 'move_right']
        self.direction_vectors = {
            'move_up': (0, -1),
            'move_down': (0, 1),
            'move_left': (-1, 0),
            'move_right': (1, 0)
        }
        self.interest_weights = {
            'enemy_smaller': 10,
            'enemy_larger': -10,
            'vitamin': 15,
            'friendly': -5,
            'enemy_near': -20  # Affecte la décision de séparer
        }
        self.enemy_near_threshold = 3  # Distance seuil pour considérer les ennemis comme proches

    def build_moves(self, grid):
        """
        Construit une liste de moves pour ce tour en évaluant l'intérêt des directions.
        """
        moves_for_this_turn = []
        
        # Séparer les cellules par type
        my_cells = [cell for cell in grid if cell.get('player') == self.my_player_name]
        enemy_cells = [cell for cell in grid if cell.get('player') not in [self.my_player_name, 'vitamin']]
        vitamins = [cell for cell in grid if cell.get('player') == 'vitamin']
        
        if not my_cells:
            return []
        
        for cell in my_cells:
            x, y, weight = cell.get('x'), cell.get('y'), cell.get('weight', 1)
            
            # Obtenir les directions valides pour cette cellule
            valid_directions = self.get_valid_directions(x, y)
            
            if not valid_directions:
                # Aucune direction valide, rester sur place
                move = {
                    "x": x,
                    "y": y,
                    "player": self.my_player_name,
                    "move_up": 0,
                    "move_down": 0,
                    "move_left": 0,
                    "move_right": 0,
                    "move_stay": weight
                }
                moves_for_this_turn.append(move)
                continue
            
            # Évaluer l'intérêt de chaque direction valide
            interests = {direction: self.evaluate_interest(x, y, direction, grid, enemy_cells, vitamins) 
                         for direction in valid_directions}
            
            # Décider s'il faut se séparer ou rester ensemble
            if self.is_enemy_near(x, y, enemy_cells):
                # Préfère rester ensemble
                split = False
            else:
                # Préfère se séparer
                split = True
            
            if split and weight >= len(valid_directions):
                # Choisir autant de directions que possible avec le plus d'intérêt
                sorted_directions = sorted(interests.items(), key=lambda item: item[1], reverse=True)
                top_directions = [dir for dir, val in sorted_directions if val > 0]
                
                # Limiter le nombre de directions au poids disponible
                max_split = min(weight, len(top_directions))
                if max_split == 0:
                    # Si aucune direction n'a un intérêt positif, rester sur place
                    move = {
                        "x": x,
                        "y": y,
                        "player": self.my_player_name,
                        "move_up": 0,
                        "move_down": 0,
                        "move_left": 0,
                        "move_right": 0,
                        "move_stay": weight
                    }
                else:
                    selected_directions = top_directions[:max_split]
                    move = self.create_move(x, y, selected_directions, weight)
            else:
                # Choisir la direction avec le plus d'intérêt
                best_direction = max(interests, key=interests.get)
                move = {
                    "x": x,
                    "y": y,
                    "player": self.my_player_name,
                    "move_up": 0,
                    "move_down": 0,
                    "move_left": 0,
                    "move_right": 0,
                    "move_stay": 0
                }
                move[best_direction] = weight
            
            moves_for_this_turn.append(move)
        
        return moves_for_this_turn

    def get_valid_directions(self, x, y):
        """
        Retourne les directions valides pour une cellule donnée en fonction de sa position et de la taille de la grille.
        """
        valid_directions = []
        for direction, (dx, dy) in self.direction_vectors.items():
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                valid_directions.append(direction)
        return valid_directions

    def evaluate_interest(self, x, y, direction, grid, enemy_cells, vitamins):
        """
        Évalue l'intérêt d'une direction en fonction des cellules ennemies, amies et des vitamines.
        """
        dx, dy = self.direction_vectors[direction]
        interest = 0
        enemies_near = False
        
        for distance in range(1, self.grid_size):
            nx, ny = x + dx * distance, y + dy * distance
            if not (0 <= nx < self.grid_size and 0 <= ny < self.grid_size):
                break  # Sortie de la grille
            
            cell = self.get_cell(nx, ny, grid)
            if not cell:
                continue  # Cellule vide
            
            if cell['player'] == 'vitamin':
                # Les vitamines augmentent l'intérêt
                interest += self.interest_weights['vitamin'] / distance
            elif cell['player'] != self.my_player_name:
                # Cellule ennemie
                if cell['weight'] < 5:  # Supposons que 5 est la taille moyenne
                    interest += self.interest_weights['enemy_smaller'] / distance
                else:
                    interest += self.interest_weights['enemy_larger'] / distance
                if distance <= self.enemy_near_threshold:
                    enemies_near = True
            else:
                # Cellule amie
                if enemies_near:
                    # Si des ennemis sont proches, minimiser la pénalité
                    interest += self.interest_weights['friendly'] / distance / 2
                else:
                    interest += self.interest_weights['friendly'] / distance

        return interest

    def is_enemy_near(self, x, y, enemy_cells):
        """
        Vérifie si des ennemis sont proches de la cellule (distance <= threshold).
        """
        for enemy in enemy_cells:
            distance = abs(enemy['x'] - x) + abs(enemy['y'] - y)
            if distance <= self.enemy_near_threshold:
                return True
        return False

    def get_cell(self, x, y, grid):
        """
        Retourne la cellule à la position (x, y) ou None si vide.
        """
        for cell in grid:
            if cell['x'] == x and cell['y'] == y:
                return cell
        return None

    def create_move(self, x, y, directions, weight):
        """
        Crée un move en répartissant le poids sur les directions spécifiées.
        """
        move = {
            "x": x,
            "y": y,
            "player": self.my_player_name,
            "move_up": 0,
            "move_down": 0,
            "move_left": 0,
            "move_right": 0,
            "move_stay": 0
        }
        split_weight = weight // len(directions)
        remainder = weight % len(directions)
        for direction in directions:
            move[direction] = split_weight
        # Répartir le reste
        for i in range(remainder):
            move[directions[i % len(directions)]] += 1
        return move
