import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Coins, Hammer, TreePine, Mountain, Wheat, Crown, Clock, Users, Sword, Shield, TrendingUp, Star, MessageCircle, User, Settings } from 'lucide-react';
import { useRealTimeData, useLeaderboard, useNearbyPlayers } from '../hooks/useRealTimeData';
import ChatSystem from './ChatSystem';
import ProfileModal from './ProfileModal';
import AdminPanel from './AdminPanel';
import { useToast } from '../hooks/use-toast';

const MultiplayerDashboard = ({ player, onLogout }) => {
  const { 
    resources, 
    buildings, 
    constructionQueue, 
    army, 
    loading, 
    error,
    upgradeBuilding,
    recruitSoldiers,
    launchRaid
  } = useRealTimeData(player);
  
  const { leaderboard } = useLeaderboard();
  const { nearbyPlayers } = useNearbyPlayers();
  
  const [selectedTarget, setSelectedTarget] = useState(null);
  const [showProfile, setShowProfile] = useState(false);
  const [showAdmin, setShowAdmin] = useState(false);
  const { toast } = useToast();

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

  const canAffordBuilding = (building) => {
    if (!resources || !building) return false;
    // This will be calculated by the backend
    return true; // Let backend handle the validation
  };

  const startConstruction = async (building) => {
    try {
      const result = await upgradeBuilding(building.id);
      if (result.success) {
        toast({
          title: "Construction Started",
          description: `Upgrading ${building.type} to level ${building.level + 1}`,
        });
      }
    } catch (error) {
      toast({
        title: "Construction Failed",
        description: error.message,
        variant: "destructive"
      });
    }
  };

  const handleRaid = async (targetPlayer) => {
    try {
      const result = await launchRaid(targetPlayer.username);
      if (result.success) {
        const raidResult = result.raid_result;
        toast({
          title: raidResult.success ? "Raid Successful!" : "Raid Failed",
          description: raidResult.battleReport,
          variant: raidResult.success ? "default" : "destructive"
        });
      }
    } catch (error) {
      toast({
        title: "Raid Failed",
        description: error.message,
        variant: "destructive"
      });
    }
  };

  const handleRecruitSoldiers = async () => {
    try {
      const result = await recruitSoldiers('soldiers', 10);
      if (result.success) {
        toast({
          title: "Soldiers Recruited",
          description: "10 soldiers have joined your army",
        });
      }
    } catch (error) {
      toast({
        title: "Recruitment Failed",
        description: error.message,
        variant: "destructive"
      });
    }
  };

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const calculatePower = () => {
    return player?.power || 0;
  };

  const getArmySize = () => {
    if (!army) return 0;
    if (typeof army === 'object') {
      return Object.values(army).reduce((total, count) => total + count, 0);
    }
    return army;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center text-white">
        <div className="text-xl">Loading your kingdom...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center text-white">
        <div className="text-center">
          <div className="text-xl mb-4">Error loading kingdom data</div>
          <div className="text-red-400">{error}</div>
          <Button onClick={() => window.location.reload()} className="mt-4">
            Retry
          </Button>
        </div>
      </div>
    );
  }

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
            <Badge variant="outline">Army: {getArmySize()}</Badge>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Button onClick={() => setShowProfile(true)} variant="outline">
            <User className="w-4 h-4 mr-2" />
            Profile
          </Button>
          {player.username === 'admin' && (
            <Button onClick={() => setShowAdmin(true)} variant="destructive">
              <Settings className="w-4 h-4 mr-2" />
              Admin Panel
            </Button>
          )}
          <Button onClick={onLogout} variant="outline">Logout</Button>
        </div>
      </div>

      {/* Resources Panel with Empire Bonuses */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {Object.entries(resources || {}).map(([resourceType, amount]) => {
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
                    <p className="text-xl font-bold">{(amount || 0).toLocaleString()}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Tabs defaultValue="kingdom" className="w-full">
        <TabsList className="grid w-full grid-cols-5 bg-slate-800/50">
          <TabsTrigger value="kingdom">Kingdom</TabsTrigger>
          <TabsTrigger value="military">Military</TabsTrigger>
          <TabsTrigger value="diplomacy">Diplomacy</TabsTrigger>
          <TabsTrigger value="rankings">Rankings</TabsTrigger>
          <TabsTrigger value="chat">
            <MessageCircle className="w-4 h-4 mr-2" />
            Chat
          </TabsTrigger>
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
                    {buildings && buildings.map(building => {
                      const IconComponent = buildingIcons[building.type];
                      
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
                                Production: {building.production && Object.entries(building.production || {}).map(([resource, amount]) => {
                                  const finalAmount = Math.floor(amount || 0);
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
                                <Button 
                                  onClick={() => startConstruction(building)}
                                  disabled={building.constructing}
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
                                value={item.progress || 0} 
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
                    <Badge variant="outline" className="text-lg px-3 py-1">{getArmySize()} soldiers</Badge>
                  </div>
                  <div className="space-y-2">
                    <Button 
                      onClick={handleRecruitSoldiers}
                      className="w-full bg-green-600 hover:bg-green-700"
                    >
                      Recruit 10 Soldiers (Cost: 500 gold, 300 food)
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
                  {nearbyPlayers && nearbyPlayers.map(target => (
                    <Card key={target.username} className="bg-slate-700/50 border-slate-600">
                      <CardContent className="p-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-medium">{target.kingdomName}</h4>
                            <div className="flex space-x-2 text-xs text-slate-400">
                              <span>Power: {target.power?.toLocaleString() || 'N/A'}</span>
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
                              onClick={() => handleRaid(target)}
                              disabled={getArmySize() === 0}
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
                {leaderboard && leaderboard.map((playerEntry, index) => (
                  <Card key={playerEntry.username} className={`border-slate-600 ${
                    playerEntry.username === player.username ? 'bg-amber-500/10 border-amber-500' : 'bg-slate-700/50'
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
                            <h4 className="font-medium">{playerEntry.kingdomName}</h4>
                            <p className="text-sm text-slate-400">{playerEntry.empire} Empire</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-bold">{playerEntry.power?.toLocaleString() || 'N/A'}</p>
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

        <TabsContent value="chat" className="space-y-6">
          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
            <CardContent className="p-6">
              <ChatSystem player={player} />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Profile Modal */}
        <ProfileModal 
          isOpen={showProfile} 
          onClose={() => setShowProfile(false)} 
          player={player}
          onUpdate={(updatedPlayer) => {
            // Update current player data
            Object.assign(player, updatedPlayer);
          }}
        />

        {/* Admin Panel */}
        {showAdmin && player.username === 'admin' && (
          <div className="fixed inset-0 z-50 bg-black/80">
            <div className="h-full overflow-y-auto">
              <AdminPanel currentUser={player} />
              <Button 
                onClick={() => setShowAdmin(false)}
                className="fixed top-4 right-4 z-60"
                variant="outline"
              >
                Close Admin Panel
              </Button>
            </div>
          </div>
        )}
      </Tabs>
    </div>
  );
};

export default MultiplayerDashboard;