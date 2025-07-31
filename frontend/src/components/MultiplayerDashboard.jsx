import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Coins, Hammer, TreePine, Mountain, Wheat, Crown, Clock, Users, Sword, Shield, TrendingUp, Star } from 'lucide-react';
import { mockMultiplayerData } from '../utils/mockMultiplayerData';

const MultiplayerDashboard = ({ player, onLogout }) => {
  const [resources, setResources] = useState(mockMultiplayerData.getPlayerResources(player.username));
  const [buildings, setBuildings] = useState(mockMultiplayerData.getPlayerBuildings(player.username));
  const [constructionQueue, setConstructionQueue] = useState(mockMultiplayerData.getConstructionQueue(player.username));
  const [leaderboard, setLeaderboard] = useState(mockMultiplayerData.getLeaderboard());
  const [nearbyPlayers, setNearbyPlayers] = useState(mockMultiplayerData.getNearbyPlayers(player.username));
  const [selectedTarget, setSelectedTarget] = useState(null);
  const [armySize, setArmySize] = useState(mockMultiplayerData.getPlayerArmy(player.username));

  // Resource icons mapping
  const resourceIcons = {
    gold: Coins,
    wood: TreePine,
    stone: Mountain,
    food: Wheat
  };

  // Building icons mapping
  const buildingIcons = {
    castle: Crown,
    farm: Wheat,
    lumbermill: TreePine,
    mine: Mountain,
    barracks: Users,
    blacksmith: Hammer
  };

  // Empire bonuses
  const empireBonus = mockMultiplayerData.getEmpireBonus(player.empire);

  // Real-time resource updates with empire bonuses
  useEffect(() => {
    const interval = setInterval(() => {
      setResources(prevResources => {
        const newResources = { ...prevResources };
        const buildingBonus = mockMultiplayerData.calculateResourceGeneration(buildings, player.empire);
        
        newResources.gold = Math.floor(newResources.gold + buildingBonus.gold);
        newResources.wood = Math.floor(newResources.wood + buildingBonus.wood);
        newResources.stone = Math.floor(newResources.stone + buildingBonus.stone);
        newResources.food = Math.floor(newResources.food + buildingBonus.food);
        
        mockMultiplayerData.updatePlayerResources(player.username, newResources);
        return newResources;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [buildings, player.empire, player.username]);

  // Construction timer updates
  useEffect(() => {
    const interval = setInterval(() => {
      setConstructionQueue(prevQueue => {
        const newQueue = prevQueue.map(item => ({
          ...item,
          timeRemaining: Math.max(0, item.timeRemaining - 1)
        })).filter(item => {
          if (item.timeRemaining <= 0) {
            // Complete construction
            setBuildings(prevBuildings => 
              prevBuildings.map(building => 
                building.id === item.buildingId 
                  ? { ...building, level: building.level + 1, constructing: false }
                  : building
              )
            );
            return false;
          }
          return true;
        });
        
        mockMultiplayerData.updateConstructionQueue(player.username, newQueue);
        return newQueue;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [player.username]);

  // Update leaderboard periodically
  useEffect(() => {
    const interval = setInterval(() => {
      setLeaderboard(mockMultiplayerData.getLeaderboard());
      setNearbyPlayers(mockMultiplayerData.getNearbyPlayers(player.username));
    }, 5000);

    return () => clearInterval(interval);
  }, [player.username]);

  const canAffordBuilding = (cost) => {
    return Object.keys(cost).every(resource => resources[resource] >= cost[resource]);
  };

  const startConstruction = (building) => {
    const cost = mockMultiplayerData.getBuildingCost(building.type, building.level + 1);
    if (!canAffordBuilding(cost) || building.constructing) return;

    // Deduct resources
    const newResources = { ...resources };
    Object.keys(cost).forEach(resource => {
      newResources[resource] -= cost[resource];
    });
    
    setResources(newResources);
    mockMultiplayerData.updatePlayerResources(player.username, newResources);

    // Add to construction queue
    const constructionTime = mockMultiplayerData.getBuildingTime(building.type, building.level + 1);
    const newQueueItem = {
      id: Date.now(),
      buildingId: building.id,
      buildingType: building.type,
      targetLevel: building.level + 1,
      timeRemaining: constructionTime
    };

    setConstructionQueue(prev => [...prev, newQueueItem]);
    setBuildings(prev => 
      prev.map(b => b.id === building.id ? { ...b, constructing: true } : b)
    );
  };

  const launchRaid = (targetPlayer) => {
    if (armySize === 0) return;
    
    // Mock raid results
    const success = Math.random() > 0.5;
    const stolenResources = success ? {
      gold: Math.floor(Math.random() * 200) + 50,
      wood: Math.floor(Math.random() * 100) + 25,
      stone: Math.floor(Math.random() * 100) + 25,
      food: Math.floor(Math.random() * 50) + 10
    } : {};

    if (success) {
      const newResources = { ...resources };
      Object.keys(stolenResources).forEach(resource => {
        newResources[resource] += stolenResources[resource];
      });
      setResources(newResources);
      mockMultiplayerData.updatePlayerResources(player.username, newResources);
      
      // Add raid to history
      mockMultiplayerData.addRaidHistory(player.username, targetPlayer.username, true, stolenResources);
    } else {
      mockMultiplayerData.addRaidHistory(player.username, targetPlayer.username, false, {});
    }

    // Reduce army size
    setArmySize(prev => Math.max(0, prev - Math.floor(Math.random() * 10) - 5));
  };

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const calculatePower = () => {
    const buildingPower = buildings.reduce((total, building) => total + (building.level * 100), 0);
    const armyPower = armySize * 50;
    return buildingPower + armyPower;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-4">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-yellow-600 bg-clip-text text-transparent">
            {player.kingdomName}
          </h1>
          <div className="flex items-center space-x-4 mt-2">
            <Badge variant="secondary">{player.empire.charAt(0).toUpperCase() + player.empire.slice(1)} Empire</Badge>
            <Badge variant="outline">Power: {calculatePower().toLocaleString()}</Badge>
            <Badge variant="outline">Army: {armySize}</Badge>
          </div>
        </div>
        <Button onClick={onLogout} variant="outline">Logout</Button>
      </div>

      {/* Resources Panel with Empire Bonuses */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {Object.entries(resources).map(([resourceType, amount]) => {
          const IconComponent = resourceIcons[resourceType];
          const bonus = empireBonus[resourceType] || 0;
          return (
            <Card key={resourceType} className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
              <CardContent className="p-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-amber-500/20 rounded-lg">
                    <IconComponent className="w-6 h-6 text-amber-400" />
                  </div>
                  <div>
                    <p className="text-sm text-slate-400 capitalize">{resourceType}</p>
                    <p className="text-xl font-bold">{amount.toLocaleString()}</p>
                    {bonus > 0 && (
                      <p className="text-xs text-green-400">+{bonus}% bonus</p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Tabs defaultValue="kingdom" className="w-full">
        <TabsList className="grid w-full grid-cols-4 bg-slate-800/50">
          <TabsTrigger value="kingdom">Kingdom</TabsTrigger>
          <TabsTrigger value="military">Military</TabsTrigger>
          <TabsTrigger value="diplomacy">Diplomacy</TabsTrigger>
          <TabsTrigger value="rankings">Rankings</TabsTrigger>
        </TabsList>

        <TabsContent value="kingdom" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Buildings Panel */}
            <div className="lg:col-span-2">
              <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Crown className="w-6 h-6 text-amber-400" />
                    <span>Your Buildings</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {buildings.map(building => {
                      const IconComponent = buildingIcons[building.type];
                      const cost = mockMultiplayerData.getBuildingCost(building.type, building.level + 1);
                      const canAfford = canAffordBuilding(cost);
                      const buildTime = mockMultiplayerData.getBuildingTime(building.type, building.level + 1);

                      return (
                        <Card key={building.id} className="bg-slate-700/50 border-slate-600 hover:border-slate-500 transition-colors">
                          <CardContent className="p-4">
                            <div className="flex items-center justify-between mb-3">
                              <div className="flex items-center space-x-3">
                                <div className="p-2 bg-slate-600 rounded-lg">
                                  <IconComponent className="w-6 h-6 text-amber-400" />
                                </div>
                                <div>
                                  <h3 className="font-semibold capitalize">{building.type}</h3>
                                  <Badge variant="secondary" className="text-xs">
                                    Level {building.level}
                                  </Badge>
                                </div>
                              </div>
                            </div>

                            <div className="space-y-2 mb-4">
                              <p className="text-sm text-slate-400">{building.description}</p>
                              <div className="text-xs text-slate-500">
                                Production: {building.production && Object.entries(building.production).map(([resource, amount]) => {
                                  const bonus = empireBonus[resource] || 0;
                                  const finalAmount = Math.floor(amount * (1 + bonus / 100));
                                  return `+${finalAmount}/s ${resource}`;
                                }).join(', ')}
                              </div>
                            </div>

                            {building.constructing ? (
                              <div className="text-center">
                                <Badge variant="outline" className="mb-2">
                                  <Clock className="w-3 h-3 mr-1" />
                                  Upgrading...
                                </Badge>
                              </div>
                            ) : (
                              <div className="space-y-2">
                                <div className="text-xs text-slate-400">
                                  Next level cost:
                                  {Object.entries(cost).map(([resource, amount]) => (
                                    <span key={resource} className={`ml-2 ${resources[resource] >= amount ? 'text-green-400' : 'text-red-400'}`}>
                                      {amount} {resource}
                                    </span>
                                  ))}
                                </div>
                                <div className="text-xs text-slate-400">
                                  Build time: {formatTime(buildTime)}
                                </div>
                                <Button 
                                  onClick={() => startConstruction(building)}
                                  disabled={!canAfford || building.constructing}
                                  className="w-full bg-amber-600 hover:bg-amber-700 disabled:bg-slate-600"
                                >
                                  Upgrade to Level {building.level + 1}
                                </Button>
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Construction Queue */}
            <div>
              <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Hammer className="w-6 h-6 text-amber-400" />
                    <span>Construction Queue</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {constructionQueue.length === 0 ? (
                    <p className="text-slate-400 text-center py-8">No constructions in progress</p>
                  ) : (
                    <div className="space-y-3">
                      {constructionQueue.map(item => (
                        <Card key={item.id} className="bg-slate-700/50 border-slate-600">
                          <CardContent className="p-3">
                            <div className="flex items-center justify-between mb-2">
                              <span className="capitalize font-medium">{item.buildingType}</span>
                              <Badge variant="outline">Level {item.targetLevel}</Badge>
                            </div>
                            <div className="space-y-2">
                              <div className="flex justify-between text-sm">
                                <span className="text-slate-400">Time remaining:</span>
                                <span className="font-mono">{formatTime(item.timeRemaining)}</span>
                              </div>
                              <Progress 
                                value={((mockMultiplayerData.getBuildingTime(item.buildingType, item.targetLevel) - item.timeRemaining) / mockMultiplayerData.getBuildingTime(item.buildingType, item.targetLevel)) * 100} 
                                className="h-2"
                              />
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="military" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Army Management */}
            <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Users className="w-6 h-6 text-amber-400" />
                  <span>Army Management</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span>Current Army Size:</span>
                    <Badge variant="outline" className="text-lg px-3 py-1">{armySize} soldiers</Badge>
                  </div>
                  <div className="space-y-2">
                    <Button className="w-full bg-green-600 hover:bg-green-700">
                      Recruit Soldiers (Cost: 50 gold, 30 food)
                    </Button>
                    <Button className="w-full bg-blue-600 hover:bg-blue-700">
                      Train Army (Increase combat effectiveness)
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Raid Targets */}
            <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Sword className="w-6 h-6 text-red-400" />
                  <span>Nearby Targets</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {nearbyPlayers.map(target => (
                    <Card key={target.username} className="bg-slate-700/50 border-slate-600">
                      <CardContent className="p-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-medium">{target.kingdomName}</h4>
                            <div className="flex space-x-2 text-xs text-slate-400">
                              <span>Power: {target.power.toLocaleString()}</span>
                              <span>Empire: {target.empire}</span>
                            </div>
                          </div>
                          <div className="space-x-2">
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => setSelectedTarget(target)}
                            >
                              Scout
                            </Button>
                            <Button 
                              size="sm" 
                              className="bg-red-600 hover:bg-red-700"
                              onClick={() => launchRaid(target)}
                              disabled={armySize === 0}
                            >
                              Raid
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="diplomacy" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Trade Offers */}
            <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Coins className="w-6 h-6 text-green-400" />
                  <span>Trade Center</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Button className="w-full bg-green-600 hover:bg-green-700">
                    Create Trade Offer
                  </Button>
                  <div className="space-y-3">
                    <h4 className="font-medium">Active Trades</h4>
                    <div className="text-center text-slate-400 py-4">
                      No active trades
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Alliances */}
            <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Shield className="w-6 h-6 text-blue-400" />
                  <span>Alliances</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Button className="w-full bg-blue-600 hover:bg-blue-700">
                    Create Alliance
                  </Button>
                  <div className="space-y-3">
                    <h4 className="font-medium">Current Alliances</h4>
                    <div className="text-center text-slate-400 py-4">
                      No alliances formed
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="rankings" className="space-y-6">
          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="w-6 h-6 text-amber-400" />
                <span>Global Rankings</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {leaderboard.map((player, index) => (
                  <Card key={player.username} className={`border-slate-600 ${
                    player.username === player.username ? 'bg-amber-500/10 border-amber-500' : 'bg-slate-700/50'
                  }`}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-slate-600">
                            {index < 3 ? (
                              <Star className="w-4 h-4 text-amber-400" />
                            ) : (
                              <span className="text-sm font-bold">{index + 1}</span>
                            )}
                          </div>
                          <div>
                            <h4 className="font-medium">{player.kingdomName}</h4>
                            <p className="text-sm text-slate-400">{player.empire} Empire</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-bold">{player.power.toLocaleString()}</p>
                          <p className="text-sm text-slate-400">Power</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default MultiplayerDashboard;