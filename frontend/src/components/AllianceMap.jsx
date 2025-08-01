import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Shield, Crown, Sword, Flame, User, MapPin } from 'lucide-react';
import apiService from '../services/apiService';

const AllianceMap = () => {
  const [allianceMap, setAllianceMap] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedAlliance, setSelectedAlliance] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAllianceMap();
  }, []);

  const loadAllianceMap = async () => {
    try {
      setLoading(true);
      const response = await apiService.getAllianceMap();
      setAllianceMap(response.alliances || []);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Failed to load alliance map:', err);
    } finally {
      setLoading(false);
    }
  };

  const getFlagColor = (color) => {
    const colors = {
      red: 'bg-red-600',
      blue: 'bg-blue-600',
      green: 'bg-green-600',
      purple: 'bg-purple-600',
      gold: 'bg-amber-500',
      silver: 'bg-slate-400'
    };
    return colors[color] || 'bg-slate-600';
  };

  const getFlagIcon = (symbol) => {
    const icons = {
      crown: Crown,
      sword: Sword,
      shield: Shield,
      dragon: Flame,
      eagle: '🦅',
      lion: '🦁'
    };
    return icons[symbol] || Shield;
  };

  const getFlagPattern = (pattern, color) => {
    const baseColor = getFlagColor(color);
    
    switch (pattern) {
      case 'stripes':
        return `${baseColor} bg-gradient-to-r from-current via-white/20 to-current`;
      case 'cross':
        return `${baseColor} relative after:absolute after:inset-0 after:bg-white/30 after:bg-gradient-to-b after:from-transparent after:via-white/40 after:to-transparent`;
      case 'diagonal':
        return `${baseColor} bg-gradient-to-br from-current via-white/20 to-current`;
      default:
        return baseColor;
    }
  };

  const renderFlag = (flag) => {
    const IconComponent = getFlagIcon(flag.symbol);
    const isStringIcon = typeof IconComponent === 'string';
    
    return (
      <div 
        className={`w-8 h-6 rounded-sm flex items-center justify-center text-white text-xs font-bold ${getFlagPattern(flag.pattern, flag.color)}`}
        title={`${flag.color} ${flag.pattern} ${flag.symbol}`}
      >
        {isStringIcon ? (
          <span className="text-sm">{IconComponent}</span>
        ) : (
          <IconComponent className="w-4 h-4" />
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
        <CardContent className="p-6">
          <div className="text-center">
            <div className="text-lg">Loading alliance map...</div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
        <CardContent className="p-6">
          <div className="text-center text-red-400">
            <div className="text-lg">Failed to load alliance map</div>
            <div className="text-sm mt-2">{error}</div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Map Header */}
      <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <MapPin className="w-6 h-6 text-amber-400" />
              <span>Alliance Territories</span>
            </div>
            <Badge variant="outline">
              {allianceMap.length} Major Alliances (10+ members)
            </Badge>
          </CardTitle>
        </CardHeader>
      </Card>

      {allianceMap.length === 0 ? (
        <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
          <CardContent className="p-6">
            <div className="text-center text-slate-400">
              <MapPin className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-medium mb-2">No Major Alliances</h3>
              <p className="text-sm">
                Alliances need 10 or more members to appear on the map with their blazons.
                Form powerful alliances to claim territory!
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Visual Map */}
          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
            <CardHeader>
              <CardTitle>Realm Map</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="relative bg-gradient-to-br from-slate-700 to-slate-800 rounded-lg p-4 min-h-96 overflow-hidden">
                {/* Background pattern */}
                <div className="absolute inset-0 opacity-10">
                  <div className="grid grid-cols-10 grid-rows-8 h-full w-full">
                    {Array.from({ length: 80 }).map((_, i) => (
                      <div key={i} className="border border-slate-600/50"></div>
                    ))}
                  </div>
                </div>

                {/* Alliance territories */}
                {allianceMap.map((alliance) => (
                  <div
                    key={alliance.id}
                    className="absolute cursor-pointer group"
                    style={{
                      left: `${(alliance.coordinates.x / 1000) * 100}%`,
                      top: `${(alliance.coordinates.y / 800) * 100}%`,
                      transform: 'translate(-50%, -50%)'
                    }}
                    onClick={() => setSelectedAlliance(alliance)}
                  >
                    {/* Territory influence circle */}
                    <div 
                      className="absolute rounded-full border-2 border-dashed opacity-30 group-hover:opacity-60 transition-opacity"
                      style={{
                        width: `${alliance.influence}px`,
                        height: `${alliance.influence}px`,
                        borderColor: alliance.flag.color === 'gold' ? '#F59E0B' : 
                                   alliance.flag.color === 'red' ? '#DC2626' :
                                   alliance.flag.color === 'blue' ? '#2563EB' :
                                   alliance.flag.color === 'green' ? '#16A34A' :
                                   alliance.flag.color === 'purple' ? '#9333EA' : '#6B7280',
                        transform: 'translate(-50%, -50%)'
                      }}
                    />

                    {/* Alliance flag */}
                    <div className="relative z-10 transform group-hover:scale-110 transition-transform">
                      {renderFlag(alliance.flag)}
                    </div>

                    {/* Tooltip on hover */}
                    <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-black/80 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-20">
                      <div className="font-semibold">{alliance.name}</div>
                      <div>Leader: {alliance.leaderUsername}</div>
                      <div>{alliance.memberCount} members</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Alliance List */}
          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
            <CardHeader>
              <CardTitle>Major Alliances</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {allianceMap.map((alliance) => (
                  <Card 
                    key={alliance.id} 
                    className={`bg-slate-700/50 border-slate-600 cursor-pointer hover:border-slate-500 transition-colors ${
                      selectedAlliance?.id === alliance.id ? 'border-amber-500 bg-amber-500/10' : ''
                    }`}
                    onClick={() => setSelectedAlliance(alliance)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          {renderFlag(alliance.flag)}
                          <div>
                            <h3 className="font-semibold text-white">{alliance.name}</h3>
                            <p className="text-sm text-slate-400">Level {alliance.level}</p>
                          </div>
                        </div>
                        <Badge variant="outline" className="text-amber-400">
                          {alliance.memberCount} members
                        </Badge>
                      </div>

                      <div className="space-y-2">
                        <div className="flex items-center space-x-2 text-sm text-slate-400">
                          <User className="w-4 h-4" />
                          <span>Leader: {alliance.leaderUsername}</span>
                        </div>
                        
                        {alliance.description && (
                          <p className="text-sm text-slate-300 italic">
                            "{alliance.description}"
                          </p>
                        )}

                        <div className="flex items-center justify-between text-xs text-slate-500">
                          <span>Territory Influence: {alliance.influence}%</span>
                          <span>Coordinates: ({Math.round(alliance.coordinates.x)}, {Math.round(alliance.coordinates.y)})</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
};

export default AllianceMap;