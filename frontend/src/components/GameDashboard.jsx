import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { Coins, Hammer, TreePine, Mountain, Wheat, Crown, Clock, Users } from 'lucide-react';
import { mockData } from '../utils/mockData';

const GameDashboard = () => {
  const [resources, setResources] = useState(mockData.getResources());
  const [buildings, setBuildings] = useState(mockData.getBuildings());
  const [constructionQueue, setConstructionQueue] = useState(mockData.getConstructionQueue());
  const [selectedBuilding, setSelectedBuilding] = useState(null);

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
    mine: Mountain,
    lumbermill: TreePine,
    barracks: Users,
    blacksmith: Hammer
  };

  // Real-time resource updates
  useEffect(() => {
    const interval = setInterval(() => {
      setResources(prevResources => {
        const newResources = { ...prevResources };
        const buildingBonus = mockData.calculateResourceGeneration(buildings);
        
        newResources.gold = Math.floor(newResources.gold + buildingBonus.gold);
        newResources.wood = Math.floor(newResources.wood + buildingBonus.wood);
        newResources.stone = Math.floor(newResources.stone + buildingBonus.stone);
        newResources.food = Math.floor(newResources.food + buildingBonus.food);
        
        mockData.updateResources(newResources);
        return newResources;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [buildings]);

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
        
        mockData.updateConstructionQueue(newQueue);
        return newQueue;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const canAffordBuilding = (cost) => {
    return Object.keys(cost).every(resource => resources[resource] >= cost[resource]);
  };

  const startConstruction = (building) => {
    const cost = mockData.getBuildingCost(building.type, building.level + 1);
    if (!canAffordBuilding(cost) || building.constructing) return;

    // Deduct resources
    const newResources = { ...resources };
    Object.keys(cost).forEach(resource => {
      newResources[resource] -= cost[resource];
    });
    
    setResources(newResources);
    mockData.updateResources(newResources);

    // Add to construction queue
    const constructionTime = mockData.getBuildingTime(building.type, building.level + 1);
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

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-4">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-4xl font-bold text-center mb-2 bg-gradient-to-r from-amber-400 to-yellow-600 bg-clip-text text-transparent">
          Medieval Kingdom
        </h1>
        <p className="text-center text-slate-400">Build your empire, manage your resources</p>
      </div>

      {/* Resources Panel */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {Object.entries(resources).map(([resourceType, amount]) => {
          const IconComponent = resourceIcons[resourceType];
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
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Buildings Panel */}
        <div className="lg:col-span-2">
          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Crown className="w-6 h-6 text-amber-400" />
                <span>Your Kingdom</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {buildings.map(building => {
                  const IconComponent = buildingIcons[building.type];
                  const cost = mockData.getBuildingCost(building.type, building.level + 1);
                  const canAfford = canAffordBuilding(cost);
                  const buildTime = mockData.getBuildingTime(building.type, building.level + 1);

                  return (
                    <Card key={building.id} className="bg-slate-700/50 border-slate-600 hover:border-slate-500 transition-colors cursor-pointer">
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
                            Production: {building.production && Object.entries(building.production).map(([resource, amount]) => 
                              `+${amount}/s ${resource}`
                            ).join(', ')}
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
                            value={((mockData.getBuildingTime(item.buildingType, item.targetLevel) - item.timeRemaining) / mockData.getBuildingTime(item.buildingType, item.targetLevel)) * 100} 
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
    </div>
  );
};

export default GameDashboard;