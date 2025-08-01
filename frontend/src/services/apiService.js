import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token expiry
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('authToken');
      localStorage.removeItem('currentMedievalPlayer');
      window.location.reload();
    }
    return Promise.reject(error);
  }
);

class ApiService {
  // Authentication
  async register(userData) {
    try {
      const response = await api.post('/auth/register', userData);
      if (response.data.access_token) {
        localStorage.setItem('authToken', response.data.access_token);
      }
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  }

  async login(credentials) {
    try {
      const response = await api.post('/auth/login', credentials);
      if (response.data.access_token) {
        localStorage.setItem('authToken', response.data.access_token);
      }
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  }

  async getCurrentUser() {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get user info');
    }
  }

  // Game Data
  async getPlayerResources() {
    try {
      const response = await api.get('/game/player/resources');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get resources');
    }
  }

  async getPlayerBuildings() {
    try {
      const response = await api.get('/game/player/buildings');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get buildings');
    }
  }

  async upgradeBuilding(buildingId) {
    try {
      const response = await api.post('/game/buildings/upgrade', { buildingId });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to upgrade building');
    }
  }

  async getConstructionQueue() {
    try {
      const response = await api.get('/game/construction/queue');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get construction queue');
    }
  }

  async getPlayerArmy() {
    try {
      const response = await api.get('/game/player/army');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get army info');
    }
  }

  async recruitSoldiers(unitType, quantity) {
    try {
      const response = await api.post('/game/army/recruit', { unitType, quantity });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to recruit soldiers');
    }
  }

  async launchRaid(targetUsername) {
    try {
      const response = await api.post('/game/combat/raid', { targetUsername });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to launch raid');
    }
  }

  async getCombatHistory() {
    try {
      const response = await api.get('/game/combat/history');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get combat history');
    }
  }

  async getLeaderboard() {
    try {
      const response = await api.get('/game/leaderboard');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get leaderboard');
    }
  }

  async getNearbyPlayers() {
    try {
      const response = await api.get('/game/players/nearby');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get nearby players');
    }
  }

  async getPlayerProfile() {
    try {
      const response = await api.get('/game/player/profile');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get player profile');
    }
  }

  async updatePlayerProfile(profileData) {
    try {
      const response = await api.put('/game/player/profile', profileData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update profile');
    }
  }

  // Chat System
  async sendGlobalMessage(content) {
    try {
      const response = await api.post('/chat/global', { content });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to send message');
    }
  }

  async getGlobalMessages() {
    try {
      const response = await api.get('/chat/global');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get messages');
    }
  }

  async sendPrivateMessage(receiver, content) {
    try {
      const response = await api.post('/chat/private', { receiver, content });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to send private message');
    }
  }

  async getPrivateMessages() {
    try {
      const response = await api.get('/chat/private');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get private messages');
    }
  }

  async getOnlineUsers() {
    try {
      const response = await api.get('/chat/online-users');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get online users');
    }
  }

  async sendSystemMessage(content) {
    try {
      const response = await api.post('/chat/system-message', { content });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to send system message');
    }
  }

  async deleteMessage(messageId) {
    try {
      const response = await api.delete(`/chat/message/${messageId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to delete message');
    }
  }

  // Admin Functions
  async getAdminStats() {
    try {
      const response = await api.get('/admin/stats');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get admin stats');
    }
  }

  async getAllPlayers() {
    try {
      const response = await api.get('/admin/players');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get all players');
    }
  }

  async modifyPlayer(username, modifications) {
    try {
      const response = await api.put(`/admin/player/${username}`, modifications);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to modify player');
    }
  }

  async deletePlayer(username) {
    try {
      const response = await api.delete(`/admin/player/${username}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to delete player');
    }
  }

  async banPlayer(username, reason, duration = 0) {
    try {
      const response = await api.post(`/admin/ban-player/${username}`, { reason, duration });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to ban player');
    }
  }

  async unbanPlayer(username) {
    try {
      const response = await api.post(`/admin/unban-player/${username}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to unban player');
    }
  }

  async getAllChatMessages() {
    try {
      const response = await api.get('/admin/chat-messages');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get chat messages');
    }
  }

  async resetGameData(type = 'all') {
    try {
      const response = await api.post('/admin/reset-game-data', { type });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to reset game data');
    }
  }

  async getSystemInfo() {
    try {
      const response = await api.get('/admin/system-info');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get system info');
    }
  }

  // Army Training
  async trainArmy(trainingType = 'basic') {
    try {
      const response = await api.post('/game/army/train', { type: trainingType });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to train army');
    }
  }

  // Diplomacy - Trade System
  async createTradeOffer(offering, requesting, duration = 3600) {
    try {
      const response = await api.post('/diplomacy/trade/create', { offering, requesting, duration });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to create trade offer');
    }
  }

  async getTradeOffers() {
    try {
      const response = await api.get('/diplomacy/trade/offers');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get trade offers');
    }
  }

  async getMyTradeOffers() {
    try {
      const response = await api.get('/diplomacy/trade/my-offers');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get my trade offers');
    }
  }

  async acceptTradeOffer(offerId) {
    try {
      const response = await api.post(`/diplomacy/trade/accept/${offerId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to accept trade');
    }
  }

  // Alliance System
  async createAlliance(name, description) {
    try {
      const response = await api.post('/diplomacy/alliance/create', { name, description });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to create alliance');
    }
  }

  async getAlliances() {
    try {
      const response = await api.get('/diplomacy/alliance/list');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get alliances');
    }
  }

  async getMyAlliance() {
    try {
      const response = await api.get('/diplomacy/alliance/my');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get my alliance');
    }
  }

  async inviteToAlliance(username) {
    try {
      const response = await api.post('/diplomacy/alliance/invite', { username });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to send invitation');
    }
  }

  async getAllianceInvites() {
    try {
      const response = await api.get('/diplomacy/alliance/invites');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get alliance invites');
    }
  }

  async acceptAllianceInvite(inviteId) {
    try {
      const response = await api.post(`/diplomacy/alliance/accept/${inviteId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to accept invitation');
    }
  }

  async leaveAlliance() {
    try {
      const response = await api.post('/diplomacy/alliance/leave');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to leave alliance');
    }
  }

  async getAllianceMap() {
    try {
      const response = await api.get('/diplomacy/alliance/map');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get alliance map');
    }
  }

  // Shop System
  async getShopItems() {
    try {
      const response = await api.get('/game/shop/items');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get shop items');
    }
  }

  async buyShopItem(itemId, quantity = 1) {
    try {
      const response = await api.post(`/game/shop/buy/${itemId}`, { quantity });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to buy item');
    }
  }

  async purchaseShopItem(itemId, quantity = 1) {
    return this.buyShopItem(itemId, quantity);
  }
  async getServerStatus() {
    try {
      const response = await api.get('/status');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get server status');
    }
  }

  // Logout
  logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentMedievalPlayer');
  }
}

export default new ApiService();