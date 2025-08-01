import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { User, Crown, Shield, Sword, Calendar, MapPin } from 'lucide-react';
import apiService from '../services/apiService';
import { useToast } from '../hooks/use-toast';

const ProfileModal = ({ isOpen, onClose, player, onUpdate }) => {
  const [editMode, setEditMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [profileData, setProfileData] = useState({
    kingdomName: player?.kingdomName || '',
    bio: player?.bio || '',
    location: player?.location || '',
    motto: player?.motto || '',
    empire: player?.empire || 'norman'
  });
  const { toast } = useToast();

  useEffect(() => {
    if (player) {
      setProfileData({
        kingdomName: player.kingdomName || '',
        bio: player.bio || '',
        location: player.location || '',
        motto: player.motto || '',
        empire: player.empire || 'norman'
      });
    }
  }, [player]);

  const handleSave = async () => {
    setLoading(true);
    try {
      // Check if race change is attempted and if player has scrolls
      if (profileData.empire !== player.empire) {
        const raceChangeScrolls = player.raceChangeScrolls || 0;
        if (raceChangeScrolls <= 0) {
          toast({
            title: "Race Change Restricted",
            description: "You need a Race Change Scroll to change your empire. Visit the Shop to purchase one.",
            variant: "destructive"
          });
          setLoading(false);
          return;
        }
        
        // Confirm race change
        const confirmed = window.confirm(`Are you sure you want to change your empire from ${player.empire} to ${profileData.empire}? This will consume one Race Change Scroll.`);
        if (!confirmed) {
          setLoading(false);
          return;
        }
      }

      await apiService.updatePlayerProfile(profileData);
      toast({
        title: "Profile Updated",
        description: "Your profile has been updated successfully!",
      });
      if (onUpdate) {
        onUpdate({ ...player, ...profileData });
      }
      setEditMode(false);
    } catch (error) {
      toast({
        title: "Update Failed",
        description: error.message,
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = () => {
    if (!player) return {};
    
    const buildingLevels = player.buildings?.reduce((sum, building) => sum + building.level, 0) || 0;
    const totalResources = Object.values(player.resources || {}).reduce((sum, amount) => sum + amount, 0);
    
    // Calculate total army size if army is an object, otherwise use as number
    let armySize = 0;
    if (player.army) {
      if (typeof player.army === 'object') {
        armySize = Object.values(player.army).reduce((total, count) => total + (count || 0), 0);
      } else {
        armySize = player.army;
      }
    }
    
    return {
      power: player.power || 0,
      buildingLevels,
      totalResources,
      army: armySize,
      joinDate: new Date(2024, 0, 1).toLocaleDateString(), // Mock join date for now
      lastActive: new Date(player.lastActive || Date.now()).toLocaleDateString()
    };
  };

  const getEmpireInfo = (empire) => {
    const empires = {
      norman: { name: 'Norman Empire', color: 'from-blue-600 to-blue-800', icon: Crown },
      viking: { name: 'Viking Kingdom', color: 'from-red-600 to-red-800', icon: Sword },
      saxon: { name: 'Saxon Realm', color: 'from-green-600 to-green-800', icon: Shield },
      celtic: { name: 'Celtic Clans', color: 'from-purple-600 to-purple-800', icon: Shield },
      frankish: { name: 'Frankish Empire', color: 'from-amber-600 to-amber-800', icon: Crown }
    };
    return empires[empire] || empires.norman;
  };

  const getEmpireBonus = (empire) => {
    const bonuses = {
      norman: { gold: 25, stone: 20 },
      viking: { wood: 30, food: 15 },
      saxon: { stone: 25, gold: 15 },
      celtic: { food: 25, wood: 20 },
      frankish: { gold: 20, food: 25 }
    };
    return bonuses[empire] || bonuses.norman;
  };

  if (!player) return null;

  const stats = calculateStats();
  const empireInfo = getEmpireInfo(player.empire);
  const empireBonus = getEmpireBonus(player.empire);
  const IconComponent = empireInfo.icon;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-slate-800 border-slate-700 max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="flex items-center space-x-3">
              <div className={`p-3 rounded-lg bg-gradient-to-r ${empireInfo.color}`}>
                <IconComponent className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">{player.kingdomName}</h2>
                <p className="text-slate-400">@{player.username}</p>
              </div>
            </DialogTitle>
            <div className="flex space-x-2">
              {editMode ? (
                <>
                  <Button 
                    onClick={handleSave} 
                    className="bg-green-600 hover:bg-green-700"
                    disabled={loading}
                  >
                    {loading ? 'Saving...' : 'Save Changes'}
                  </Button>
                  <Button variant="outline" onClick={() => setEditMode(false)} disabled={loading}>
                    Cancel
                  </Button>
                </>
              ) : (
                <Button onClick={() => setEditMode(true)} className="bg-blue-600 hover:bg-blue-700">
                  <User className="w-4 h-4 mr-2" />
                  Edit Profile
                </Button>
              )}
            </div>
          </div>
        </DialogHeader>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
          {/* Profile Information */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="bg-slate-700/50 border-slate-600">
              <CardHeader>
                <CardTitle>Profile Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {editMode ? (
                  <>
                    <div className="space-y-2">
                      <Label>Kingdom Name</Label>
                      <Input
                        value={profileData.kingdomName}
                        onChange={(e) => setProfileData({...profileData, kingdomName: e.target.value})}
                        className="bg-slate-600 border-slate-500"
                        disabled={loading}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Empire</Label>
                      <Select 
                        value={profileData.empire} 
                        onValueChange={(value) => setProfileData({...profileData, empire: value})}
                        disabled={loading}
                      >
                        <SelectTrigger className="bg-slate-600 border-slate-500">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="norman">Norman Empire</SelectItem>
                          <SelectItem value="viking">Viking Kingdom</SelectItem>
                          <SelectItem value="saxon">Saxon Realm</SelectItem>
                          <SelectItem value="celtic">Celtic Clans</SelectItem>
                          <SelectItem value="frankish">Frankish Empire</SelectItem>
                        </SelectContent>
                      </Select>
                      {profileData.empire !== player.empire && (
                        <p className="text-xs text-amber-400">
                          ⚠️ Changing empire requires a Race Change Scroll (You have: {player.raceChangeScrolls || 0})
                        </p>
                      )}
                    </div>
                    <div className="space-y-2">
                      <Label>Biography</Label>
                      <Textarea
                        value={profileData.bio}
                        onChange={(e) => setProfileData({...profileData, bio: e.target.value})}
                        placeholder="Tell us about your kingdom..."
                        className="bg-slate-600 border-slate-500"
                        rows={4}
                        disabled={loading}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Location</Label>
                      <Input
                        value={profileData.location}
                        onChange={(e) => setProfileData({...profileData, location: e.target.value})}
                        placeholder="Your location..."
                        className="bg-slate-600 border-slate-500"
                        disabled={loading}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Kingdom Motto</Label>
                      <Input
                        value={profileData.motto}
                        onChange={(e) => setProfileData({...profileData, motto: e.target.value})}
                        placeholder="Your kingdom's motto..."
                        className="bg-slate-600 border-slate-500"
                        disabled={loading}
                      />
                    </div>
                  </>
                ) : (
                  <>
                    <div className="flex items-center space-x-3">
                      <Badge variant="secondary">{empireInfo.name}</Badge>
                      <Badge variant="outline">Power: {stats.power.toLocaleString()}</Badge>
                    </div>
                    
                    {player.bio && (
                      <div>
                        <h4 className="font-medium text-amber-400 mb-2">Biography</h4>
                        <p className="text-slate-300">{player.bio}</p>
                      </div>
                    )}
                    
                    {player.location && (
                      <div className="flex items-center space-x-2 text-slate-400">
                        <MapPin className="w-4 h-4" />
                        <span>{player.location}</span>
                      </div>
                    )}
                    
                    {player.motto && (
                      <div>
                        <h4 className="font-medium text-amber-400 mb-2">Kingdom Motto</h4>
                        <p className="text-slate-300 italic">"{player.motto}"</p>
                      </div>
                    )}
                    
                    <div className="flex items-center space-x-2 text-slate-400">
                      <Calendar className="w-4 h-4" />
                      <span>Joined: {stats.joinDate}</span>
                    </div>
                    
                    <div className="flex items-center space-x-2 text-slate-400">
                      <User className="w-4 h-4" />
                      <span>Last Active: {stats.lastActive}</span>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Kingdom Stats */}
            <Card className="bg-slate-700/50 border-slate-600">
              <CardHeader>
                <CardTitle>Kingdom Statistics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-slate-600/50 rounded-lg">
                    <p className="text-2xl font-bold text-amber-400">{stats.power.toLocaleString()}</p>
                    <p className="text-sm text-slate-400">Total Power</p>
                  </div>
                  <div className="text-center p-3 bg-slate-600/50 rounded-lg">
                    <p className="text-2xl font-bold text-blue-400">{stats.buildingLevels}</p>
                    <p className="text-sm text-slate-400">Building Levels</p>
                  </div>
                  <div className="text-center p-3 bg-slate-600/50 rounded-lg">
                    <p className="text-2xl font-bold text-green-400">{stats.totalResources.toLocaleString()}</p>
                    <p className="text-sm text-slate-400">Total Resources</p>
                  </div>
                  <div className="text-center p-3 bg-slate-600/50 rounded-lg">
                    <p className="text-2xl font-bold text-red-400">{stats.army}</p>
                    <p className="text-sm text-slate-400">Army Size</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Sidebar */}
          <div className="space-y-4">
            {/* Empire Bonuses */}
            <Card className="bg-slate-700/50 border-slate-600">
              <CardHeader>
                <CardTitle className="text-sm">Empire Bonuses</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {Object.entries(empireBonus).map(([resource, bonus]) => (
                    <div key={resource} className="flex justify-between">
                      <span className="capitalize text-slate-400">{resource}:</span>
                      <span className="text-green-400">+{bonus}%</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Resources */}
            <Card className="bg-slate-700/50 border-slate-600">
              <CardHeader>
                <CardTitle className="text-sm">Current Resources</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {Object.entries(player.resources || {}).map(([resource, amount]) => (
                    <div key={resource} className="flex justify-between">
                      <span className="capitalize text-slate-400">{resource}:</span>
                      <span className="text-amber-400">{amount.toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Buildings */}
            <Card className="bg-slate-700/50 border-slate-600">
              <CardHeader>
                <CardTitle className="text-sm">Buildings</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {player.buildings?.map(building => (
                    <div key={building.id} className="flex justify-between">
                      <span className="capitalize text-slate-400">{building.type}:</span>
                      <Badge variant="outline" className="text-xs">Lv.{building.level}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ProfileModal;