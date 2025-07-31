// Mock multiplayer data for the medieval empire game
class MockMultiplayerData {
  constructor() {
    this.initializeData();
  }

  initializeData() {
    // Load from localStorage or use defaults
    const savedData = localStorage.getItem('medievalMultiplayerData');
    if (savedData) {
      const data = JSON.parse(savedData);
      this.players = data.players || this.generateInitialPlayers();
      this.raidHistory = data.raidHistory || {};
      this.tradeOffers = data.tradeOffers || [];
      this.alliances = data.alliances || [];
    } else {
      this.players = this.generateInitialPlayers();
      this.raidHistory = {};
      this.tradeOffers = [];
      this.alliances = [];
    }
  }

  generateInitialPlayers() {
    const players = {};
    
    // AI players
    const aiPlayers = [
      { username: 'KingArthur', kingdomName: "Arthur's Camelot", empire: 'norman' },
      { username: 'VikingRagnar', kingdomName: 'Ragnar\'s Hold', empire: 'viking' },
      { username: 'SaxonEdward', kingdomName: 'Edward\'s Realm', empire: 'saxon' },
      { username: 'CelticBoudica', kingdomName: 'Boudica\'s Lands', empire: 'celtic' },
      { username: 'FrankishCharles', kingdomName: 'Charles\' Empire', empire: 'frankish' },
      { username: 'QueenEleanor', kingdomName: 'Eleanor\'s Kingdom', empire: 'norman' },
      { username: 'VikingErik', kingdomName: 'Erik\'s Stronghold', empire: 'viking' },
      { username: 'SaxonAlfred', kingdomName: 'Alfred\'s Domain', empire: 'saxon' }
    ];

    aiPlayers.forEach(aiPlayer => {
      players[aiPlayer.username] = {
        ...aiPlayer,
        resources: this.getEmpireStartingResources(aiPlayer.empire),
        buildings: this.getDefaultBuildings(),
        constructionQueue: [],
        army: Math.floor(Math.random() * 100) + 50,
        power: Math.floor(Math.random() * 5000) + 2000,
        lastActive: Date.now() - Math.floor(Math.random() * 3600000) // Last active within 1 hour
      };
    });

    return players;
  }

  getEmpireStartingResources(empire) {
    const base = { gold: 1500, wood: 800, stone: 600, food: 400 };
    const empireBonus = this.getEmpireBonus(empire);
    
    Object.keys(empireBonus).forEach(resource => {
      if (base[resource]) {
        base[resource] = Math.floor(base[resource] * (1 + empireBonus[resource] / 100));
      }
    });

    return base;
  }

  getEmpireBonus(empire) {
    const bonuses = {
      norman: { gold: 25, stone: 20 },
      viking: { wood: 30, food: 15 },
      saxon: { food: 25, gold: 15 },
      celtic: { wood: 20, stone: 20 },
      frankish: { gold: 20, food: 20 }
    };
    return bonuses[empire] || {};
  }

  getDefaultBuildings() {
    return [
      {
        id: 1,
        type: 'castle',
        level: 1,
        constructing: false,
        description: 'The heart of your kingdom. Increases population capacity.',
        production: { gold: 2 }
      },
      {
        id: 2,
        type: 'farm',
        level: 1,
        constructing: false,
        description: 'Produces food to feed your population.',
        production: { food: 3 }
      },
      {
        id: 3,
        type: 'lumbermill',
        level: 1,
        constructing: false,
        description: 'Harvests wood from the nearby forests.',
        production: { wood: 2 }
      },
      {
        id: 4,
        type: 'mine',
        level: 1,
        constructing: false,
        description: 'Extracts stone and precious metals.',
        production: { stone: 2, gold: 1 }
      },
      {
        id: 5,
        type: 'barracks',
        level: 1,
        constructing: false,
        description: 'Trains soldiers to defend your kingdom.',
        production: {}
      },
      {
        id: 6,
        type: 'blacksmith',
        level: 1,
        constructing: false,
        description: 'Crafts weapons and tools for your kingdom.',
        production: { gold: 1 }
      }
    ];
  }

  registerPlayer(playerData) {
    this.players[playerData.username] = {
      ...playerData,
      resources: this.getEmpireStartingResources(playerData.empire),
      buildings: this.getDefaultBuildings(),
      constructionQueue: [],
      army: 25,
      power: 1000,
      lastActive: Date.now()
    };
    this.saveData();
    return this.players[playerData.username];
  }

  getPlayerResources(username) {
    return this.players[username]?.resources || { gold: 0, wood: 0, stone: 0, food: 0 };
  }

  getPlayerBuildings(username) {
    return this.players[username]?.buildings || [];
  }

  getPlayerArmy(username) {
    return this.players[username]?.army || 0;
  }

  getConstructionQueue(username) {
    return this.players[username]?.constructionQueue || [];
  }

  updatePlayerResources(username, resources) {
    if (this.players[username]) {
      this.players[username].resources = { ...resources };
      this.players[username].lastActive = Date.now();
      this.saveData();
    }
  }

  updatePlayerBuildings(username, buildings) {
    if (this.players[username]) {
      this.players[username].buildings = [...buildings];
      this.players[username].lastActive = Date.now();
      // Recalculate power
      this.players[username].power = this.calculatePlayerPower(username);
      this.saveData();
    }
  }

  updateConstructionQueue(username, queue) {
    if (this.players[username]) {
      this.players[username].constructionQueue = [...queue];
      this.players[username].lastActive = Date.now();
      this.saveData();
    }
  }

  calculateResourceGeneration(buildings, empire) {
    const generation = { gold: 0, wood: 0, stone: 0, food: 0 };
    const empireBonus = this.getEmpireBonus(empire);
    
    buildings.forEach(building => {
      if (building.production) {
        Object.entries(building.production).forEach(([resource, amount]) => {
          const bonus = empireBonus[resource] || 0;
          const finalAmount = amount * building.level * (1 + bonus / 100);
          generation[resource] += finalAmount;
        });
      }
    });

    return generation;
  }

  calculatePlayerPower(username) {
    const player = this.players[username];
    if (!player) return 0;
    
    const buildingPower = player.buildings.reduce((total, building) => total + (building.level * 100), 0);
    const armyPower = player.army * 50;
    const resourcePower = Object.values(player.resources).reduce((total, amount) => total + Math.floor(amount / 100), 0);
    
    return buildingPower + armyPower + resourcePower;
  }

  getBuildingCost(buildingType, level) {
    const baseCosts = {
      castle: { gold: 100, wood: 80, stone: 120 },
      farm: { gold: 50, wood: 60, stone: 30 },
      lumbermill: { gold: 40, wood: 30, stone: 50 },
      mine: { gold: 80, wood: 40, stone: 60 },
      barracks: { gold: 120, wood: 100, stone: 80 },
      blacksmith: { gold: 90, wood: 70, stone: 50 }
    };

    const baseCost = baseCosts[buildingType] || {};
    const multiplier = Math.pow(1.5, level - 1);

    const cost = {};
    Object.entries(baseCost).forEach(([resource, amount]) => {
      cost[resource] = Math.floor(amount * multiplier);
    });

    return cost;
  }

  getBuildingTime(buildingType, level) {
    const baseTimes = {
      castle: 120, // 2 minutes
      farm: 60,    // 1 minute
      lumbermill: 45,
      mine: 90,
      barracks: 100,
      blacksmith: 75
    };

    const baseTime = baseTimes[buildingType] || 60;
    const multiplier = Math.pow(1.3, level - 1);

    return Math.floor(baseTime * multiplier);
  }

  getLeaderboard() {
    const sortedPlayers = Object.values(this.players)
      .map(player => ({
        ...player,
        power: this.calculatePlayerPower(player.username)
      }))
      .sort((a, b) => b.power - a.power)
      .slice(0, 10);

    return sortedPlayers;
  }

  getNearbyPlayers(currentUsername) {
    const currentPlayer = this.players[currentUsername];
    if (!currentPlayer) return [];

    return Object.values(this.players)
      .filter(player => player.username !== currentUsername)
      .map(player => ({
        ...player,
        power: this.calculatePlayerPower(player.username)
      }))
      .sort(() => Math.random() - 0.5) // Randomize for "nearby" effect
      .slice(0, 5);
  }

  addRaidHistory(attackerUsername, defenderUsername, success, stolenResources) {
    if (!this.raidHistory[attackerUsername]) {
      this.raidHistory[attackerUsername] = [];
    }

    this.raidHistory[attackerUsername].unshift({
      id: Date.now(),
      defender: defenderUsername,
      success,
      stolenResources,
      timestamp: Date.now()
    });

    // Keep only last 10 raids
    this.raidHistory[attackerUsername] = this.raidHistory[attackerUsername].slice(0, 10);
    this.saveData();
  }

  getRaidHistory(username) {
    return this.raidHistory[username] || [];
  }

  // Mock AI player activities (simulate other players being active)
  simulateAIActivity() {
    Object.keys(this.players).forEach(username => {
      const player = this.players[username];
      if (username.includes('King') || username.includes('Viking') || username.includes('Saxon') || username.includes('Celtic') || username.includes('Frankish') || username.includes('Queen')) {
        // Simulate AI resource generation and building upgrades
        const generation = this.calculateResourceGeneration(player.buildings, player.empire);
        Object.keys(generation).forEach(resource => {
          player.resources[resource] += Math.floor(generation[resource] * Math.random() * 10);
        });

        // Occasionally upgrade buildings
        if (Math.random() < 0.1) {
          const randomBuilding = player.buildings[Math.floor(Math.random() * player.buildings.length)];
          if (randomBuilding && !randomBuilding.constructing) {
            randomBuilding.level += 1;
          }
        }

        // Update power
        player.power = this.calculatePlayerPower(username);
      }
    });
    this.saveData();
  }

  saveData() {
    const dataToSave = {
      players: this.players,
      raidHistory: this.raidHistory,
      tradeOffers: this.tradeOffers,
      alliances: this.alliances
    };
    localStorage.setItem('medievalMultiplayerData', JSON.stringify(dataToSave));
  }

  resetData() {
    localStorage.removeItem('medievalMultiplayerData');
    this.initializeData();
  }
}

export const mockMultiplayerData = new MockMultiplayerData();

// Simulate AI activity every 30 seconds
setInterval(() => {
  mockMultiplayerData.simulateAIActivity();
}, 30000);