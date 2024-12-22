// server.js
const express = require('express');
const axios = require('axios');
const path = require('path');

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// -----------------------------------------------------------------
// 1) Servir les fichiers statiques de "public/"
app.use(express.static('public'));

// Rediriger la racine "/" vers "front.html"
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'front.html'));
});

// -----------------------------------------------------------------
// CONFIGURATION GLOBALE
// -----------------------------------------------------------------
const PYTHON_API = 'http://localhost:8000'; // URL de votre serveur Python

// Variables pour la partie
let currentGridSize = 10;
let currentVitaminsCount = 3;
let currentPlayers = [];   // Liste de joueurs type ['Alice', 'Bob']
let startWeight = 4;
let currentGrid = [];
let currentTurnNumber = 0;
let timeBetweenMoves = 0;

// Permet de stocker les joueurs connectés "en attente" (avant le begin)
let connectedPlayers = [];

// Mouvements par tour
let movesBuffer = {};
let turnTimer = null;

// -----------------------------------------------------------------
// FONCTIONS DE TOUR (inchangées)
// -----------------------------------------------------------------
function startTurn() {
  currentTurnNumber++;
  movesBuffer = {};

  console.log(`\n=== DÉBUT DU TOUR ${currentTurnNumber} === (timeBetweenMoves=${timeBetweenMoves})`);

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

  const allMoves = [];
  for (const playerName in movesBuffer) {
    allMoves.push(...movesBuffer[playerName]);
  }

  console.log(`=> Tour ${currentTurnNumber} : envoi de ${allMoves.length} moves au Python`);

  try {
    const pythonResp = await axios.post(`${PYTHON_API}/moves`, { moves: allMoves });
    const { move_animation, new_grid } = pythonResp.data;

    currentGrid = new_grid;
    console.log(`=> Tour ${currentTurnNumber} terminé, nouvelle grille reçue.`);

    startTurn();
  } catch (err) {
    console.error("Erreur compute_game_turn:", err);
    // On relance quand même un nouveau tour
    startTurn();
  }
}

function checkIfAllPlayersHavePlayed() {
  if (timeBetweenMoves !== 0) return;

  let nbPlayed = 0;
  for (const p of currentPlayers) {
    if (movesBuffer[p]) {
      nbPlayed++;
    }
  }
  if (nbPlayed === currentPlayers.length) {
    console.log("=> Tous les joueurs ont joué, on termine le tour immédiatement.");
    endTurn();
  }
}

// -----------------------------------------------------------------
// ROUTES
// -----------------------------------------------------------------

// 0) get /players => liste des joueurs connectés "pour la partie"
app.get('/players', (req, res) => {
  res.json({
    connectedPlayers
  });
});

// 1) POST /join => un joueur s'identifie par son nom
//    body: { name: "Alice" }
app.post('/join', (req, res) => {
  const { name } = req.body;
  if (!name) {
    return res.status(400).json({ error: "Missing 'name' field" });
  }

  // Ajoute le joueur s'il n'y est pas déjà
  if (!connectedPlayers.includes(name)) {
    connectedPlayers.push(name);
    console.log(`Nouveau joueur connecté: ${name}`);
  }
  
  res.json({ message: "Player joined", players: connectedPlayers });
});

// 2) POST /begin => démarre la partie avec la liste de joueurs connectés
//    body: { grid_size, number_of_vitamins, start_weight, time_between_moves }
app.post('/begin', async (req, res) => {
  try {
    // On récupère les paramètres
    const {
      grid_size,
      number_of_vitamins,
      start_weight: sw,
      time_between_moves: tbm
    } = req.body;

    currentGridSize = parseInt(grid_size, 10) || 10;
    currentVitaminsCount = parseInt(number_of_vitamins, 10) || 3;
    startWeight = parseInt(sw, 10) || 4;
    timeBetweenMoves = parseInt(tbm, 10) || 0;

    // Les joueurs de la partie sont ceux qui ont fait /join
    currentPlayers = connectedPlayers.slice(); // clone

    // On appelle /init du Python
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
    
    // On lance le premier tour
    startTurn();

    res.json({ message: "Game started", grid: currentGrid });
  } catch (err) {
    console.error(err);
    res.status(500).send("Erreur lors du /begin.");
  }
});

// 3) POST /moves => un joueur envoie ses coups
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

// 4) GET /state => renvoie l'état courant
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
// LANCEMENT DU SERVEUR
// -----------------------------------------------------------------
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Serveur Node lancé sur http://localhost:${PORT}`);
});
