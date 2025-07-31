// Mock data for the medieval kingdom game
class MockGameData {
  constructor() {
    this.initializeData();
  }

  initializeData() {
    // Load from localStorage or use defaults
    const savedData = localStorage.getItem('medievalKingdomData');
    if (savedData) {
      const data = JSON.parse(savedData);
      this.resources = data.resources || this.getDefaultResources();
      this.buildings = data.buildings || this.getDefaultBuildings();
      this.constructionQueue = data.constructionQueue || [];
    } else {
      this.resources = this.getDefaultResources();
      this.buildings = this.getDefaultBuildings();
      this.constructionQueue = [];
    }
  }

  getDefaultResources() {
    return {
      gold: 1000,
      wood: 500,
      stone: 300,
      food: 200
    };
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

  getResources() {
    return { ...this.resources };
  }

  getBuildings() {
    return [...this.buildings];
  }

  getConstructionQueue() {
    return [...this.constructionQueue];
  }

  updateResources(newResources) {
    this.resources = { ...newResources };
    this.saveData();
  }

  updateBuildings(newBuildings) {
    this.buildings = [...newBuildings];
    this.saveData();
  }

  updateConstructionQueue(newQueue) {
    this.constructionQueue = [...newQueue];
    this.saveData();
  }

  calculateResourceGeneration(buildings) {
    const generation = { gold: 0, wood: 0, stone: 0, food: 0 };
    
    buildings.forEach(building => {
      if (building.production) {
        Object.entries(building.production).forEach(([resource, amount]) => {
          generation[resource] += amount * building.level;
        });
      }
    });

    return generation;
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

  saveData() {
    const dataToSave = {
      resources: this.resources,
      buildings: this.buildings,
      constructionQueue: this.constructionQueue
    };
    localStorage.setItem('medievalKingdomData', JSON.stringify(dataToSave));
  }

  resetData() {
    localStorage.removeItem('medievalKingdomData');
    this.initializeData();
  }
}

export const mockData = new MockGameData();