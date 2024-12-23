# communication.py

import socketio
import requests
from logic import GameLogic  # Importer la classe GameLogic au lieu de build_moves

BASE_URL = "http://localhost:3000"
MY_PLAYER_NAME = "p1"
last_turn_played = None

sio = socketio.Client()

def send_moves(player_name, turn, moves):
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
    print("Bot (Python) connecté au serveur Node. SID =", sio.sid)
    sio.emit('join', {"name": MY_PLAYER_NAME})

@sio.event
def disconnect():
    print("Bot déconnecté")

@sio.on('stateUpdate')
def on_state_update(data):
    global last_turn_played
    turn = data.get("turn")
    grid = data.get("grid", [])
    grid_size = data.get("grid_size", 10)
    
    if turn == last_turn_played:
        return
    
    # Créer une instance de GameLogic
    game_logic = GameLogic(MY_PLAYER_NAME, grid_size)
    
    # Appeler la méthode build_moves sur l'instance
    moves_for_this_turn = game_logic.build_moves(grid)
    
    if not moves_for_this_turn:
        print(f"Tour {turn}: pas de cellule pour {MY_PLAYER_NAME}, aucun move.")
        last_turn_played = turn
        return
    
    print(f"Tour {turn}: on envoie {len(moves_for_this_turn)} moves.")
    for move in moves_for_this_turn:
        print(move)
    
    send_moves(MY_PLAYER_NAME, turn, moves_for_this_turn)
    last_turn_played = turn

def main():
    try:
        sio.connect(BASE_URL, wait_timeout=10)
        print("Connexion réussie, on attend les stateUpdate...")
        sio.wait()
    except Exception as e:
        print(f"Impossible de se connecter à {BASE_URL} : {e}")

if __name__ == "__main__":
    main()
