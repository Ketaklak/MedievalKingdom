# Medieval Empires - API Contracts & Backend Implementation Plan

## Overview
Complete multiplayer medieval empire game similar to OGame with real-time resource management, PvP combat, trading, and empire progression.

## Player System

### User Registration/Authentication
```
POST /api/auth/register
{
  "username": "string",
  "password": "string", 
  "kingdomName": "string",
  "empire": "norman|viking|saxon|celtic|frankish"
}

POST /api/auth/login
{
  "username": "string",
  "password": "string"
}

GET /api/auth/me
Authorization: Bearer token
```

### Player Profile
```
GET /api/players/profile
POST /api/players/profile
{
  "kingdomName": "string",
  "empire": "string"
}
```

## Resource Management

### Resources
```
GET /api/players/resources
PUT /api/players/resources
{
  "gold": number,
  "wood": number, 
  "stone": number,
  "food": number
}
```

### Real-time Resource Generation
- WebSocket connection for live updates
- Empire-specific bonuses applied server-side
- Resource generation based on building levels

## Building System

### Buildings CRUD
```
GET /api/players/buildings
POST /api/buildings/upgrade
{
  "buildingId": "string",
  "targetLevel": number
}

GET /api/buildings/queue
DELETE /api/buildings/queue/{queueId}
```

### Building Types & Costs
- Castle: Population capacity, gold production
- Farm: Food production
- Lumbermill: Wood production  
- Mine: Stone + gold production
- Barracks: Army training
- Blacksmith: Weapon crafting

## Military System

### Army Management
```
GET /api/players/army
POST /api/army/recruit
{
  "unitType": "soldier|archer|cavalry",
  "quantity": number
}

POST /api/army/train
{
  "unitType": "string"
}
```

### Combat & Raids
```
POST /api/combat/raid
{
  "targetUsername": "string",
  "armySize": number
}

GET /api/combat/history
GET /api/combat/incoming
```

## Multiplayer Features

### Leaderboards
```
GET /api/leaderboard/power
GET /api/leaderboard/empire/{empireType}
```

### Player Discovery
```
GET /api/players/nearby
GET /api/players/search?q=username
GET /api/players/{username}/profile
```

### Trading System
```
POST /api/trade/offers
{
  "offering": { "gold": 100, "wood": 50 },
  "requesting": { "stone": 75, "food": 25 },
  "duration": 3600
}

GET /api/trade/offers
POST /api/trade/accept/{offerId}
DELETE /api/trade/offers/{offerId}
```

### Alliance System
```
POST /api/alliances/create
{
  "name": "string",
  "description": "string"
}

POST /api/alliances/invite
{
  "allianceId": "string",
  "username": "string"
}

GET /api/alliances/my
GET /api/alliances/{id}/members
```

## Empire Bonuses (Server-side Application)

### Norman Empire
- Gold production: +25%
- Stone production: +20%
- Castle construction: +25% faster

### Viking Kingdom  
- Wood production: +30%
- Food production: +15%
- Raid damage: +30%

### Saxon Realm
- Food production: +25%
- Gold production: +15% 
- Defensive bonus: +20%

### Celtic Clans
- Wood production: +20%
- Stone production: +20%
- Unique druid buildings

### Frankish Empire
- Gold production: +20%
- Food production: +20%
- Trade route bonus: +20%

## Real-time Features

### WebSocket Events
```
// Client -> Server
"resource_update"
"building_complete"
"raid_launched"

// Server -> Client  
"resource_generated"
"building_finished"
"raid_incoming"
"player_online"
```

## Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  username: String,
  passwordHash: String,
  email: String,
  createdAt: Date,
  lastActive: Date
}
```

### Players Collection
```javascript
{
  _id: ObjectId,
  userId: ObjectId,
  kingdomName: String,
  empire: String,
  resources: {
    gold: Number,
    wood: Number, 
    stone: Number,
    food: Number
  },
  buildings: [{
    id: String,
    type: String,
    level: Number,
    constructing: Boolean
  }],
  army: {
    soldiers: Number,
    archers: Number,
    cavalry: Number
  },
  power: Number,
  coordinates: { x: Number, y: Number }
}
```

### Construction Queue Collection
```javascript
{
  _id: ObjectId,
  playerId: ObjectId,
  buildingId: String,
  buildingType: String,
  targetLevel: Number,
  startTime: Date,
  completionTime: Date,
  completed: Boolean
}
```

### Raids Collection
```javascript
{
  _id: ObjectId,
  attackerId: ObjectId,
  defenderId: ObjectId,
  armySize: Number,
  success: Boolean,
  stolenResources: Object,
  timestamp: Date,
  battleReport: String
}
```

## Mock Data Migration

### Current Mock Features to Replace:
1. **mockMultiplayerData.js** -> Database operations
2. **localStorage persistence** -> MongoDB collections
3. **AI player simulation** -> Scheduled background jobs
4. **Real-time updates** -> WebSocket implementation
5. **Resource generation timers** -> Server-side cron jobs

### Frontend Integration Changes:
1. Replace mock API calls with real HTTP requests
2. Implement WebSocket connection for real-time updates
3. Add authentication token management
4. Replace localStorage with server state management
5. Add error handling for network requests

## Implementation Priority:
1. Authentication system & player creation
2. Resource management & building system
3. Real-time resource generation
4. Combat & raid system
5. Trading & alliance features
6. WebSocket integration for live updates