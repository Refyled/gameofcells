import socketio
import requests
import random

# URL de base de votre serveur Node
BASE_URL = "http://localhost:3000"

# Nom du joueur (vous pouvez changer)
MY_PLAYER_NAME = "p1"

# Pour éviter de rejouer plusieurs fois sur le même tour
last_turn_played = None

# Crée un client Socket.IO
sio = socketio.Client()

def build_moves(grid, my_player_name, grid_size):
    """
    Construit une liste de moves pour ce tour.
    Si une cellule a un poids > 1, il y a une chance de diviser le poids entre deux directions aléatoires valides.
    """
    moves_for_this_turn = []

    # Filtrer mes cellules
    my_cells = [c for c in grid if c.get('player') == my_player_name]
    if not my_cells:
        return []

    for cell in my_cells:
        x = cell.get('x')
        y = cell.get('y')
        weight = cell.get('weight', 1)

        # Obtenir les directions valides pour cette cellule
        valid_directions = get_valid_directions(x, y, grid_size)

        if not valid_directions:
            # Aucune direction valide, rester sur place
            move = {
                "x": x,
                "y": y,
                "player": my_player_name,
                "move_up": 0,
                "move_down": 0,
                "move_left": 0,
                "move_right": 0,
                "move_stay": weight
            }
            moves_for_this_turn.append(move)
            continue

        move = {
            "x": x,
            "y": y,
            "player": my_player_name,
            "move_up": 0,
            "move_down": 0,
            "move_left": 0,
            "move_right": 0,
            "move_stay": 0
        }

        if weight <= 1:
            # Déplacer tout le poids dans une direction aléatoire
            direction = random.choice(valid_directions)
            move[direction] = weight
        else:
            # Décider aléatoirement de diviser le poids
            should_divide = random.random() < 0.5  # 50% de chance de diviser
            if should_divide and len(valid_directions) >= 2:
                # Choisir deux directions distinctes
                direction1, direction2 = random.sample(valid_directions, 2)
                # Diviser le poids de manière aléatoire
                split_point = random.randint(1, weight - 1)
                move[direction1] = split_point
                move[direction2] = weight - split_point
            else:
                # Ne pas diviser, déplacer tout le poids dans une direction
                direction = random.choice(valid_directions)
                move[direction] = weight

        moves_for_this_turn.append(move)

    return moves_for_this_turn

def get_valid_directions(x, y, grid_size):
    """
    Retourne les directions valides pour une cellule donnée en fonction de sa position et de la taille de la grille.
    """
    directions = []
    if y > 0:
        directions.append('move_up')
    if y < grid_size - 1:
        directions.append('move_down')
    if x > 0:
        directions.append('move_left')
    if x < grid_size - 1:
        directions.append('move_right')
    directions.append('move_stay')  # Toujours possible

    return directions

def send_moves(player_name, turn, moves):
    """
    Envoie la requête POST /moves vers le serveur Node, en HTTP.
    """
    body = {
        "player": player_name,
        "turn": turn,
        "moves": moves
    }
    try:
        resp = requests.post(f"{BASE_URL}/moves", json=body)
        resp.raise_for_status()
        print(f"=> Moves envoyés pour le tour {turn}, réponse: {resp.json()}")
    except requests.RequestException as e:
        print(f"Erreur lors de l'envoi /moves: {e}")

@sio.event
def connect():
    """
    S'exécute quand le client Socket.IO est connecté au serveur.
    """
    print("Bot (Python) connecté au serveur Node. SID =", sio.sid)
    # On peut envoyer un événement 'join' si le serveur le gère via socket
    sio.emit('join', {"name": MY_PLAYER_NAME})

@sio.event
def disconnect():
    """
    S'exécute quand la connexion Socket.IO est fermée.
    """
    print("Bot déconnecté")

@sio.on('stateUpdate')
def on_state_update(data):
    """
    Réception de l'événement 'stateUpdate' depuis le serveur Node.
    data est un dict Python contenant : turn, grid, grid_size, ...
    """
    global last_turn_played

    turn = data.get("turn")
    grid = data.get("grid", [])
    grid_size = data.get("grid_size", 10)  # Valeur par défaut si absent

    # Si on a déjà joué ce tour, on ne refait pas de moves
    if turn == last_turn_played:
        return

    # Construire un move
    moves_for_this_turn = build_moves(grid, MY_PLAYER_NAME, grid_size)
    if not moves_for_this_turn:
        print(f"Tour {turn}: pas de cellule pour {MY_PLAYER_NAME}, aucun move.")
        last_turn_played = turn
        return

    print(f"Tour {turn}: on envoie {len(moves_for_this_turn)} moves.")
    for move in moves_for_this_turn:
        print(move)

    # Poster /moves en HTTP
    send_moves(MY_PLAYER_NAME, turn, moves_for_this_turn)

    last_turn_played = turn

def main():
    # Connexion au serveur Node via Socket.IO
    try:
        sio.connect(BASE_URL, wait_timeout=10)
        print("Connexion réussie, on attend les stateUpdate...")
        sio.wait()  # bloquant, attend les événements
    except Exception as e:
        print(f"Impossible de se connecter à {BASE_URL} : {e}")

if __name__ == "__main__":
    main()