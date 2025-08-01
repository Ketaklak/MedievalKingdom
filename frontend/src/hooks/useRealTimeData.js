import { useState, useEffect, useCallback } from 'react';
import apiService from '../services/apiService';

export const useRealTimeData = (player) => {
  const [resources, setResources] = useState(null);
  const [buildings, setBuildings] = useState(null);
  const [constructionQueue, setConstructionQueue] = useState([]);
  const [army, setArmy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchGameData = useCallback(async () => {
    if (!player) return;

    try {
      setError(null);
      
      // Fetch all game data with individual error handling
      const fetchWithFallback = async (fetchFn, fallback) => {
        try {
          return await fetchFn();
        } catch (err) {
          console.warn('API call failed, using fallback:', err.message);
          return fallback;
        }
      };

      const [resourcesData, buildingsData, queueData, armyData] = await Promise.all([
        fetchWithFallback(() => apiService.getPlayerResources(), { resources: { gold: 0, wood: 0, stone: 0, food: 0 } }),
        fetchWithFallback(() => apiService.getPlayerBuildings(), { buildings: [] }),
        fetchWithFallback(() => apiService.getConstructionQueue(), { queue: [] }),
        fetchWithFallback(() => apiService.getPlayerArmy(), { army: { soldiers: 0, archers: 0, cavalry: 0 } })
      ]);

      setResources(resourcesData.resources || { gold: 0, wood: 0, stone: 0, food: 0 });
      setBuildings(buildingsData.buildings || []);
      setConstructionQueue(queueData.queue || []);
      setArmy(armyData.army || { soldiers: 0, archers: 0, cavalry: 0 });
      setLoading(false);
      
    } catch (err) {
      console.error('Failed to fetch game data:', err);
      setError(err.message);
      setLoading(false);
      
      // Set default values to prevent frontend crashes
      setResources({ gold: 0, wood: 0, stone: 0, food: 0 });
      setBuildings([]);
      setConstructionQueue([]);
      setArmy({ soldiers: 0, archers: 0, cavalry: 0 });
    }
  }, [player]);

  // Initial data fetch
  useEffect(() => {
    fetchGameData();
  }, [fetchGameData]);

  // Real-time updates every 10 seconds
  useEffect(() => {
    if (!player) return;

    const interval = setInterval(() => {
      fetchGameData();
    }, 10000); // 10 seconds

    return () => clearInterval(interval);
  }, [player, fetchGameData]);

  const upgradeBuilding = async (buildingId) => {
    try {
      const result = await apiService.upgradeBuilding(buildingId);
      
      // Update local state immediately
      if (result.success) {
        setResources(result.new_resources);
        
        // Update building state
        setBuildings(prevBuildings => 
          prevBuildings.map(building => 
            building.id === buildingId 
              ? { ...building, constructing: true }
              : building
          )
        );
        
        // Add to construction queue
        if (result.queue_item) {
          setConstructionQueue(prev => [...prev, result.queue_item]);
        }
      }
      
      return result;
    } catch (error) {
      throw error;
    }
  };

  const recruitSoldiers = async (unitType = 'soldiers', quantity = 1) => {
    try {
      const result = await apiService.recruitSoldiers(unitType, quantity);
      
      if (result.success) {
        setResources(result.new_resources);
        setArmy(result.new_army);
      }
      
      return result;
    } catch (error) {
      throw error;
    }
  };

  const launchRaid = async (targetUsername) => {
    try {
      const result = await apiService.launchRaid(targetUsername);
      
      // Refresh data after raid
      if (result.success) {
        await fetchGameData();
      }
      
      return result;
    } catch (error) {
      throw error;
    }
  };

  return {
    resources,
    buildings,
    constructionQueue,
    army,
    loading,
    error,
    refetch: fetchGameData,
    upgradeBuilding,
    recruitSoldiers,
    launchRaid
  };
};

export const useLeaderboard = () => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchLeaderboard = useCallback(async () => {
    try {
      setError(null);
      const data = await apiService.getLeaderboard();
      setLeaderboard(data.leaderboard || []);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch leaderboard:', err);
      setError(err.message);
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLeaderboard();
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchLeaderboard, 30000);
    return () => clearInterval(interval);
  }, [fetchLeaderboard]);

  return { leaderboard, loading, error, refetch: fetchLeaderboard };
};

export const useNearbyPlayers = () => {
  const [nearbyPlayers, setNearbyPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchNearbyPlayers = useCallback(async () => {
    try {
      setError(null);
      const data = await apiService.getNearbyPlayers();
      setNearbyPlayers(data.players || []);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch nearby players:', err);
      setError(err.message);
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNearbyPlayers();
    
    // Refresh every 60 seconds
    const interval = setInterval(fetchNearbyPlayers, 60000);
    return () => clearInterval(interval);
  }, [fetchNearbyPlayers]);

  return { nearbyPlayers, loading, error, refetch: fetchNearbyPlayers };
};