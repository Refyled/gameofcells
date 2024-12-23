
---

### API Endpoints and Events: `server.py`

---

#### HTTP Endpoints

1. **`GET /state`**  
   **Description**:  
   Retrieves the current state of the game, including the grid configuration, turn information, and player details.

   **Method**: `GET`  
   **URL**: `/state`

   ---

   **Response**:  
   Returns a JSON object containing the following fields:

   - **`turn`** *(int)*: The current turn number in the game.
   - **`grid`** *(array)*: A list of cells on the grid, each represented as an object:
     - **`x`** *(int)*: The x-coordinate of the cell.
     - **`y`** *(int)*: The y-coordinate of the cell.
     - **`weight`** *(int)*: The weight of the cell, determining its strength.
     - **`player`** *(string)*: The player ID owning the cell (or `"vitamin"` for vitamin cells).
   - **`grid_size`** *(int)*: The size of the grid (NxN).
   - **`timeBetweenMoves`** *(int)*: The time interval (in seconds) between turns.
   - **`players`** *(array)*: A list of connected player IDs.

   ---

   **Example Response**:
   ```json
   {
     "turn": 4,
     "grid": [
       { "x": 2, "y": 2, "weight": 5, "player": "p1" },
       { "x": 3, "y": 3, "weight": 4, "player": "p2" },
       { "x": 0, "y": 0, "weight": 1, "player": "vitamin" }
     ],
     "grid_size": 10,
     "timeBetweenMoves": 1,
     "players": ["p1", "p2"]
   }
   ```

2. **`POST /moves`**

   **Description**:  
   Receives a list of moves for the current turn, processes them, and updates the game state accordingly.

   **Method**: `POST`  
   **URL**: `/moves`

   ---

   **Request Body**:  
   A JSON object containing:
   - **`moves`** *(array)*: A list of moves, where each move is represented as an object:
     - **`x`** *(int)*: The x-coordinate of the cell initiating the move.
     - **`y`** *(int)*: The y-coordinate of the cell initiating the move.
     - **`player`** *(string)*: The player ID submitting the move.
     - **`move_up`**, **`move_down`**, **`move_left`**, **`move_right`**, **`move_stay`** *(int)*: The distribution of the cell's weight in each direction.

   ---

   **Example Request**:
   ```json
   {
     "moves": [
       {
         "x": 2,
         "y": 2,
         "player": "p1",
         "move_up": 1,
         "move_down": 0,
         "move_left": 0,
         "move_right": 2,
         "move_stay": 1
       }
     ]
   }
   ```

   **Response**:  
   The response is a JSON object containing the following fields:

   - **`move_animation`** *(array)*: A detailed description of all movements that occurred during the turn. Each element in the array is an object with the following fields:
     - **`origin_x`** *(int)*: The x-coordinate where the cell started its move.
     - **`origin_y`** *(int)*: The y-coordinate where the cell started its move.
     - **`direction`** *(string)*: The direction of the movement (`"up"`, `"down"`, `"left"`, `"right"`, or `"stay"`).
     - **`weight`** *(int)*: The weight of the moving cell.
     - **`result`** *(string)*: The outcome of the movement. Possible values:
       - `"survives"`: The cell successfully completed its move.
       - `"dies_midway"`: The cell was destroyed mid-move due to a collision.
       - `"dies_arrival"`: The cell was destroyed upon reaching its destination.

   - **`new_grid`** *(array)*: The updated state of the grid after processing the moves. Each element is an object with the following fields:
     - **`x`** *(int)*: The x-coordinate of the cell.
     - **`y`** *(int)*: The y-coordinate of the cell.
     - **`weight`** *(int)*: The weight of the cell.
     - **`player`** *(string)*: The player ID owning the cell, or `"vitamin"` for vitamin cells.

   **Example Response**:
   ```json
   {
     "move_animation": [
       {
         "origin_x": 2,
         "origin_y": 2,
         "direction": "right",
         "weight": 2,
         "result": "survives"
       },
       {
         "origin_x": 2,
         "origin_y": 2,
         "direction": "stay",
         "weight": 1,
         "result": "survives"
       }
     ],
     "new_grid": [
       { "x": 3, "y": 2, "weight": 2, "player": "p1" },
       { "x": 2, "y": 2, "weight": 1, "player": "p1" }
     ]
   }
   ```

3. **`POST /init`**  
   **Description**:  
   Reinitializes the game with new parameters, including grid size, number of vitamins, starting weights, and the list of players.

   **Method**: `POST`  
   **URL**: `/init`

   ---

   **Request Body**:  
   A JSON object containing the following fields:

   - **`grid_size`** *(int)*: The size of the grid (NxN).
   - **`number_of_vitamins`** *(int)*: The total number of vitamin cells to be placed on the grid.
   - **`players`** *(array)*: A list of player IDs participating in the game.
   - **`start_weight`** *(int)*: The initial weight of each player's cells.

   **Example Request**:
   ```json
   {
     "grid_size": 10,
     "number_of_vitamins": 5,
     "players": ["p1", "p2"],
     "start_weight": 4
   }
   ```

   **Response**:  
   The response is a JSON object containing the following fields:

   - **`message`** *(string)*: A confirmation message indicating the game has been successfully reinitialized.
   - **`grid`** *(array)*: The initial state of the grid after reinitialization. Each cell is represented as an object with the following fields:
     - **`x`** *(int)*: The x-coordinate of the cell.
     - **`y`** *(int)*: The y-coordinate of the cell.
     - **`weight`** *(int)*: The initial weight of the cell.
     - **`player`** *(string)*: The player ID owning the cell, or `"vitamin"` for vitamin cells.

   ---

   **Example Response**:
   ```json
   {
     "message": "Game re-initialized",
     "grid": [
       { "x": 2, "y": 2, "weight": 4, "player": "p1" },
       { "x": 3, "y": 3, "weight": 4, "player": "p2" },
       { "x": 0, "y": 0, "weight": 1, "player": "vitamin" }
     ]
   }
   ```

---

#### Socket.IO Events

1. **`stateUpdate`**  
   **Description**:  
   Broadcasts the current state of the game to all connected clients. This event provides essential information about the grid, players, and game settings, allowing clients to update their visualizations or game logic. It is emitted upon computation of every new turn.

   ---

   **Payload**:  
   The event sends a JSON object with the following fields:

   - **`turn`** *(int)*: The current turn number in the game.
   - **`grid`** *(array)*: The state of the grid, represented as a list of cells. Each cell is an object with:
     - **`x`** *(int)*: The x-coordinate of the cell.
     - **`y`** *(int)*: The y-coordinate of the cell.
     - **`weight`** *(int)*: The weight of the cell.
     - **`player`** *(string)*: The player ID owning the cell, or `"vitamin"` for vitamin cells.
   - **`grid_size`** *(int)*: The size of the grid (NxN).
   - **`timeBetweenMoves`** *(int)*: The time interval (in seconds) between turns.
   - **`players`** *(array)*: A list of player IDs currently connected to the game.

   ---

   **Example Payload**:
   ```json
   {
     "turn": 3,
     "grid": [
       { "x": 2, "y": 2, "weight": 5, "player": "p1" },
       { "x": 3, "y": 3, "weight": 4, "player": "p2" },
       { "x": 0, "y": 0, "weight": 1, "player": "vitamin" }
     ],
     "grid_size": 10,
     "timeBetweenMoves": 1,
     "players": ["p1", "p2"]
   }
   ```

2. **`turnAnimation`**  
   **Description**:  
   Broadcasts the animation details for a specific turn to all connected clients. This event provides movement data and outcomes for cells, enabling clients to display animations and update their visualizations accordingly.

   ---

   **Payload**:  
   The event sends a JSON object with the following fields:

   - **`turn`** *(int)*: The turn number for which the animation is being broadcast.
   - **`move_animation`** *(array)*: A detailed list of all cell movements during the turn. Each movement is represented as an object with:
     - **`origin_x`** *(int)*: The starting x-coordinate of the cell.
     - **`origin_y`** *(int)*: The starting y-coordinate of the cell.
     - **`direction`** *(string)*: The direction of the movement (`"up"`, `"down"`, `"left"`, `"right"`, or `"stay"`).
     - **`weight`** *(int)*: The weight of the moving cell.
     - **`result`** *(string)*: The outcome of the movement:
       - `"survives"`: The cell successfully completed its move.
       - `"dies_midway"`: The cell was destroyed mid-move.
       - `"dies_arrival"`: The cell was destroyed upon reaching its destination.
   - **`grid_size`** *(int)*: The size of the grid (NxN).
   - **`timeBetweenMoves`** *(int)*: The time interval (in seconds) between turns.

   ---

   **Example Payload**:
   ```json
   {
     "turn": 3,
     "move_animation": [
       {
         "origin_x": 2,
         "origin_y": 2,
         "direction": "right",
         "weight": 2,
         "result": "survives"
       },
       {
         "origin_x": 2,
         "origin_y": 2,
         "direction": "stay",
         "weight": 1,
         "result": "survives"
       }
     ],
     "grid_size": 10,
     "timeBetweenMoves": 1
   }
   ```

3. **`join`**  
   **Description**:  
   Registers a player to the current game session. This event is triggered when a client connects to the server and provides the player's name for identification and participation.

   ---

   **Payload**:  
   The event sends a JSON object with the following field:

   - **`name`** *(string)*: The name or ID of the player joining the session.

   ---

   **Example Payload**:
   ```json
   {
     "name": "Player1"
   }
   ```

4. **`disconnect`**  
   **Description**:  
   Handles a player's disconnection and optionally updates the game state or player list.

---

### API Endpoints and Events: `server.js`

---

#### HTTP Endpoints

1. **`GET /`**  
   - **Description**: Serves the main game interface (`front.html`).

2. **`GET /settings`**  
   - **Description**: Serves the settings page (`settings.html`) for configuring game parameters.

3. **`GET /players`**  
   - **Description**: Retrieves the list of currently connected players.

4. **`POST /join`**  
   - **Description**: Registers a new player to the game.  
   - **Request Body**:  
     ```json
     {
       "name": "PlayerName"
     }
     ```
   - **Response**:  
     ```json
     {
       "message": "Player joined",
       "players": ["Player1", "Player2"]
     }
     ```

5. **`POST /begin`**  
   - **Description**: Starts a new game with custom parameters.  
   - **Request Body**:  
     ```json
     {
       "grid_size": 10,
       "number_of_vitamins": 3,
       "start_weight": 4,
       "time_between_moves": 1
     }
     ```
   - **Response**:  
     ```json
     {
       "message": "Game started",
       "grid": [
         { "x": 1, "y": 1, "weight": 3, "player": "p1" },
         { "x": 2, "y": 2, "weight": 4, "player": "p2" }
       ]
     }
     ```

6. **`POST /moves`**  
   - **Description**: Submits a player's moves for the current turn.  
   - **Request Body**:  
     ```json
     {
       "player": "p1",
       "turn": 3,
       "moves": [
         { "x": 1, "y": 1, "move_up": 1, "move_down": 0, "move_left": 0, "move_right": 2, "move_stay": 0 }
       ]
     }
     ```
   - **Response**:  
     ```json
     {
       "message": "Moves recorded"
     }
     ```

---

#### Socket.IO Events

1. **`connection`**  
   - **Description**: Triggered when a client connects to the server. Logs the connection and initializes communication with the player.

2. **`join`**  
   - **Description**: Registers a player in the game session via WebSocket.  
   - **Payload**:  
     ```json
     {
       "name": "PlayerName"
     }
     ```

3. **`disconnect`**  
   - **Description**: Triggered when a client disconnects from the server. Optionally updates the connected players list.

4. **`stateUpdate`**  
   - **Description**: Sends the current game state, including the grid, turn number, grid size, and connected players.  

   - **Payload**:  
     ```json
     {
       "turn": 3,
       "grid": [
         { "x": 1, "y": 1, "weight": 3, "player": "p1" },
         { "x": 2, "y": 2, "weight": 4, "player": "p2" }
       ],
       "grid_size": 10,
       "timeBetweenMoves": 1,
       "players": ["p1", "p2"]
     }
     ```

5. **`turnAnimation`**  
   - **Description**: Sends animation details for the current turn.  
   - **Payload**:  
     ```json
     {
       "turn": 3,
       "move_animation": [
         { "origin_x": 1, "origin_y": 1, "weight": 3, "direction": "right", "result": "survives" }
       ],
       "grid_size": 10,
       "timeBetweenMoves": 1
     }
     ```

---
