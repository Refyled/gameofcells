// server.js
const express = require('express');
const axios = require('axios');
const path = require('path');
const http = require('http'); // Pour créer un serveur HTTP brut
const { Server } = require('socket.io');

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 1) On crée un serveur HTTP Express, puis on attache Socket.IO
const httpServer = http.createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: "*",
  },
});

// -----------------------------------------------------------------
// 1) Servir les fichiers statiques de "public/"
app.use(express.static('public'));

// Page principale => front.html
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'front.html'));
});

// Nouvelle page => settings.html
app.get('/settings', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'settings.html'));
});

// -----------------------------------------------------------------
// CONFIGURATION GLOBALE
// -----------------------------------------------------------------
const PYTHON_API = 'http://localhost:8000';

let currentGridSize = 10;
let currentVitaminsCount = 3;
let currentPlayers = [];
let startWeight = 4;
let currentGrid = [];
let currentTurnNumber = 0;
let timeBetweenMoves = 0;

let movesBuffer = {};
let turnTimer = null;

// On maintient la liste de joueurs "connectés" au WebSocket (optionnel)
let connectedPlayers = [];

// -----------------------------------------------------------------
// SOCKET.IO : on gère les connexions
// -----------------------------------------------------------------
io.on('connection', (socket) => {
  console.log("Un client s'est connecté (socket ID =", socket.id, ")");

  socket.on('join', (data) => {
    const { name } = data;
    if (!connectedPlayers.includes(name)) {
      connectedPlayers.push(name);
      console.log(`Join via socket => ${name}`);
      // On informe tous les clients
      io.emit('playersList', connectedPlayers);
    }
  });

  socket.on('disconnect', () => {
    console.log(`Le client (socket ID=${socket.id}) s'est déconnecté`);
    // Ici, on pourrait retirer un joueur si on voulait
  });
});

// -----------------------------------------------------------------
// FONCTIONS DE TOUR
// -----------------------------------------------------------------
function emitState() {
  // Émet un événement "stateUpdate" si vous en avez besoin
  // (facultatif si on n'utilise plus "stateUpdate")
  io.emit('stateUpdate', {
    turn: currentTurnNumber,
    grid: currentGrid,
    grid_size: currentGridSize,
    timeBetweenMoves,
    players: currentPlayers
  });
}

function startTurn() {
  currentTurnNumber++;
  movesBuffer = {};
  console.log(`\n=== DÉBUT DU TOUR ${currentTurnNumber} === (timeBetweenMoves=${timeBetweenMoves})`);

  // Notifier les clients (optionnel si on n'utilise plus stateUpdate)
  emitState();

  // Timer si timeBetweenMoves>0
  if (timeBetweenMoves > 0) {
    if (turnTimer) {
      clearTimeout(turnTimer);
      turnTimer = null;
    }
    turnTimer = setTimeout(() => {
      console.log(`Fin du temps pour le tour ${currentTurnNumber} => on compile les coups`);
      endTurn();
    }, timeBetweenMoves * 1000);
  }
}

async function endTurn() {
  if (turnTimer) {
    clearTimeout(turnTimer);
    turnTimer = null;
  }

  // On compile tous les moves
  const allMoves = [];
  for (const playerName in movesBuffer) {
    allMoves.push(...movesBuffer[playerName]);
  }

  console.log(`=> Tour ${currentTurnNumber} : envoi de ${allMoves.length} moves au Python`);

  try {
    // On envoie la liste de moves directement
    const pythonResp = await axios.post(`${PYTHON_API}/moves`, allMoves);
    // On suppose le Python renvoie : { move_animation, new_grid }
    const { move_animation, new_grid } = pythonResp.data;

    currentGrid = new_grid;
    console.log(`=> Tour ${currentTurnNumber} terminé, nouvelle grille reçue.`);

    // On émet l'événement "turnAnimation" pour le front
    io.emit('turnAnimation', {
      turn: currentTurnNumber,
      grid_size: currentGridSize,     // <-- On renvoie la taille
      timeBetweenMoves: timeBetweenMoves, // <-- On renvoie le temps/coup
      move_animation
    });

    // Lance le tour suivant
    startTurn();
  } catch (err) {
    console.error("Erreur compute_game_turn:", err);
    startTurn();
  }
}

function checkIfAllPlayersHavePlayed() {
  if (timeBetweenMoves !== 0) return;
  let nbPlayed = 0;
  for (const p of currentPlayers) {
    if (movesBuffer[p]) nbPlayed++;
  }
  if (nbPlayed === currentPlayers.length) {
    console.log("=> Tous les joueurs ont joué, on termine le tour immédiatement.");
    endTurn();
  }
}

// -----------------------------------------------------------------
// ROUTES HTTP
// -----------------------------------------------------------------

app.get('/players', (req, res) => {
  res.json({ connectedPlayers });
});

app.post('/join', (req, res) => {
  const { name } = req.body;
  if (!name) {
    return res.status(400).json({ error: "Missing 'name' field" });
  }
  if (!connectedPlayers.includes(name)) {
    connectedPlayers.push(name);
    io.emit('playersList', connectedPlayers);
  }
  res.json({ message: "Player joined", players: connectedPlayers });
});

app.post('/begin', async (req, res) => {
  try {
    const {
      grid_size,
      number_of_vitamins,
      start_weight: sw,
      time_between_moves: tbm
    } = req.body;

    currentGridSize = parseInt(grid_size, 10) || 10;
    currentVitaminsCount = parseInt(number_of_vitamins, 10) || 3;
    startWeight = parseInt(sw, 10) || 4;
    timeBetweenMoves = tbm;

    currentPlayers = [...connectedPlayers];

    // On appelle Python /init
    const initBody = {
      grid_size: currentGridSize,
      number_of_vitamins: currentVitaminsCount,
      players: currentPlayers,
      start_weight: startWeight
    };
    const pythonResp = await axios.post(`${PYTHON_API}/init`, initBody);
    const { grid } = pythonResp.data;

    currentGrid = grid || [];
    currentTurnNumber = 0;

    console.log(`Partie BEGIN: grille=${currentGridSize}, vitamins=${currentVitaminsCount}, players=${currentPlayers}, TBM=${timeBetweenMoves}`);
    
    // Lance le premier tour
    startTurn();

    res.json({ message: "Game started", grid: currentGrid });
  } catch (err) {
    console.error(err);
    res.status(500).send("Erreur lors du /begin.");
  }
});

app.post('/moves', (req, res) => {
  try {
    const { player, turn } = req.body;
    const moves = Array.isArray(req.body.moves) ? req.body.moves : [];

    if (turn !== currentTurnNumber) {
      return res.json({
        error: "Tour invalide",
        currentTurn: currentTurnNumber
      });
    }

    movesBuffer[player] = moves;
    console.log(`=> Reçu ${moves.length} moves pour le joueur ${player} (tour=${turn}).`);

    if (timeBetweenMoves === 0) {
      checkIfAllPlayersHavePlayed();
    }
    res.json({ message: "Moves enregistrés" });
  } catch (err) {
    console.error(err);
    res.status(500).send("Erreur /moves");
  }
});

app.get('/state', (req, res) => {
  res.json({
    turn: currentTurnNumber,
    grid: currentGrid,
    grid_size: currentGridSize,
    timeBetweenMoves,
    players: currentPlayers
  });
});

// -----------------------------------------------------------------
const PORT = 3000;
httpServer.listen(PORT, () => {
  console.log(`Serveur Node+Socket.IO lancé sur http://localhost:${PORT}`);
});
