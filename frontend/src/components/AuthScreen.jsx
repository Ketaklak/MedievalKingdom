import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { Crown, Sword, Shield, Zap, Users, Coins } from 'lucide-react';

const AuthScreen = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    email: '',
    kingdomName: '',
    empire: 'norman'
  });

  const empires = [
    {
      id: 'norman',
      name: 'Norman Empire',
      description: 'Masters of conquest and castle building',
      bonuses: { gold: 25, stone: 20 },
      icon: Crown,
      color: 'from-blue-600 to-blue-800',
      speciality: 'Castle construction +25% faster, +20% stone production'
    },
    {
      id: 'viking',
      name: 'Viking Kingdom',
      description: 'Fierce raiders and skilled shipbuilders',
      bonuses: { wood: 30, food: 15 },
      icon: Sword,
      color: 'from-red-600 to-red-800',
      speciality: 'Raid damage +30%, +30% wood production'
    },
    {
      id: 'saxon',
      name: 'Saxon Realm',
      description: 'Agricultural masters and defensive specialists',
      bonuses: { food: 25, gold: 15 },
      icon: Shield,
      color: 'from-green-600 to-green-800',
      speciality: 'Farm production +25%, defensive bonus +20%'
    },
    {
      id: 'celtic',
      name: 'Celtic Clans',
      description: 'Nature-bound warriors with mystical knowledge',
      bonuses: { wood: 20, stone: 20 },
      icon: Zap,
      color: 'from-purple-600 to-purple-800',
      speciality: 'Balanced resource bonus, unique druid buildings'
    },
    {
      id: 'frankish',
      name: 'Frankish Empire',
      description: 'Elite cavalry and diplomatic prowess',
      bonuses: { gold: 20, food: 20 },
      icon: Users,
      color: 'from-amber-600 to-amber-800',
      speciality: 'Trade routes +20%, cavalry units +25% strength'
    }
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleEmpireSelect = (empireId) => {
    setFormData(prev => ({ ...prev, empire: empireId }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      if (isLogin) {
        // Login
        await onLogin({
          username: formData.username,
          password: formData.password,
          isRegistration: false
        });
      } else {
        // Registration
        await onLogin({
          username: formData.username,
          password: formData.password,
          email: formData.email || `${formData.username}@medievalempires.com`,
          kingdomName: formData.kingdomName,
          empire: formData.empire,
          isRegistration: true
        });
      }
    } catch (error) {
      setError(error.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const selectedEmpire = empires.find(e => e.id === formData.empire);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-6xl">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-amber-400 to-yellow-600 bg-clip-text text-transparent">
            Medieval Empires
          </h1>
          <p className="text-xl text-slate-300">Build your empire, conquer your enemies, rule the medieval world</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Login/Register Form */}
          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-2xl text-center">
                {isLogin ? 'Enter Your Kingdom' : 'Create Your Empire'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="username">Username</Label>
                  <Input
                    id="username"
                    value={formData.username}
                    onChange={(e) => handleInputChange('username', e.target.value)}
                    placeholder="Enter your username"
                    className="bg-slate-700 border-slate-600"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    value={formData.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
                    placeholder="Enter your password"
                    className="bg-slate-700 border-slate-600"
                    required
                  />
                </div>

                {!isLogin && (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="kingdomName">Kingdom Name</Label>
                      <Input
                        id="kingdomName"
                        value={formData.kingdomName}
                        onChange={(e) => handleInputChange('kingdomName', e.target.value)}
                        placeholder="Name your kingdom"
                        className="bg-slate-700 border-slate-600"
                        required
                      />
                    </div>

                    <div className="space-y-4">
                      <Label>Choose Your Empire</Label>
                      <div className="grid grid-cols-1 gap-3">
                        {empires.map(empire => {
                          const IconComponent = empire.icon;
                          return (
                            <div
                              key={empire.id}
                              onClick={() => handleEmpireSelect(empire.id)}
                              className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                                formData.empire === empire.id
                                  ? 'border-amber-500 bg-slate-700/70'
                                  : 'border-slate-600 bg-slate-700/30 hover:border-slate-500'
                              }`}
                            >
                              <div className="flex items-center space-x-3">
                                <div className={`p-2 rounded-lg bg-gradient-to-r ${empire.color}`}>
                                  <IconComponent className="w-6 h-6 text-white" />
                                </div>
                                <div className="flex-1">
                                  <h3 className="font-semibold text-white">{empire.name}</h3>
                                  <p className="text-sm text-slate-400">{empire.description}</p>
                                  <div className="flex space-x-2 mt-2">
                                    {Object.entries(empire.bonuses).map(([resource, bonus]) => (
                                      <Badge key={resource} variant="secondary" className="text-xs">
                                        +{bonus}% {resource}
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </>
                )}

                <div className="space-y-4">
                  <Button type="submit" className="w-full bg-amber-600 hover:bg-amber-700 text-lg py-3">
                    {isLogin ? 'Enter Kingdom' : 'Found Empire'}
                  </Button>

                  <div className="text-center">
                    <button
                      type="button"
                      onClick={() => setIsLogin(!isLogin)}
                      className="text-amber-400 hover:text-amber-300 underline"
                    >
                      {isLogin ? "Don't have a kingdom? Create one" : "Already have a kingdom? Enter here"}
                    </button>
                  </div>
                </div>
              </form>
            </CardContent>
          </Card>

          {/* Empire Preview */}
          {!isLogin && selectedEmpire && (
            <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-3">
                  <div className={`p-3 rounded-lg bg-gradient-to-r ${selectedEmpire.color}`}>
                    <selectedEmpire.icon className="w-8 h-8 text-white" />
                  </div>
                  <span>{selectedEmpire.name}</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <p className="text-slate-300">{selectedEmpire.description}</p>
                  
                  <div>
                    <h4 className="font-semibold mb-3 text-amber-400">Empire Bonuses</h4>
                    <div className="grid grid-cols-2 gap-3">
                      {Object.entries(selectedEmpire.bonuses).map(([resource, bonus]) => (
                        <div key={resource} className="flex items-center space-x-2 p-3 bg-slate-700/50 rounded-lg">
                          <Coins className="w-5 h-5 text-amber-400" />
                          <div>
                            <p className="font-medium capitalize">{resource}</p>
                            <p className="text-sm text-green-400">+{bonus}% production</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-3 text-amber-400">Special Abilities</h4>
                    <div className="p-4 bg-slate-700/50 rounded-lg">
                      <p className="text-slate-300">{selectedEmpire.speciality}</p>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-3 text-amber-400">Starting Resources</h4>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className="flex justify-between">
                        <span>Gold:</span>
                        <span className="text-amber-400">1,500</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Wood:</span>
                        <span className="text-amber-400">800</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Stone:</span>
                        <span className="text-amber-400">600</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Food:</span>
                        <span className="text-amber-400">400</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Game Features Preview */}
          {isLogin && (
            <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Game Features</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center space-x-3 p-3 bg-slate-700/50 rounded-lg">
                    <Crown className="w-6 h-6 text-amber-400" />
                    <div>
                      <h4 className="font-medium">Build Your Empire</h4>
                      <p className="text-sm text-slate-400">Construct buildings, manage resources</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3 p-3 bg-slate-700/50 rounded-lg">
                    <Sword className="w-6 h-6 text-red-400" />
                    <div>
                      <h4 className="font-medium">Raid & Conquer</h4>
                      <p className="text-sm text-slate-400">Attack other players, steal resources</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3 p-3 bg-slate-700/50 rounded-lg">
                    <Users className="w-6 h-6 text-blue-400" />
                    <div>
                      <h4 className="font-medium">Global Rankings</h4>
                      <p className="text-sm text-slate-400">Compete with thousands of players</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3 p-3 bg-slate-700/50 rounded-lg">
                    <Coins className="w-6 h-6 text-green-400" />
                    <div>
                      <h4 className="font-medium">Trade & Diplomacy</h4>
                      <p className="text-sm text-slate-400">Form alliances, trade resources</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthScreen;