import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Shield, Users, MessageSquare, Settings, Edit, Trash2, Ban, CheckCircle, Terminal, Refresh, AlertTriangle } from 'lucide-react';
import apiService from '../services/apiService';
import { useToast } from '../hooks/use-toast';

const AdminPanel = ({ currentUser }) => {
  const [stats, setStats] = useState({});
  const [players, setPlayers] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [systemInfo, setSystemInfo] = useState({});
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [editDialog, setEditDialog] = useState(false);
  const [editData, setEditData] = useState({});
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState([]);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [serverLogs, setServerLogs] = useState([]);
  const [broadcastMessage, setBroadcastMessage] = useState('');
  const [selectedPlayerForReset, setSelectedPlayerForReset] = useState(null);
  const { toast } = useToast();

  useEffect(() => {
    loadData();
    initializeConsole();
    
    // Auto-refresh every 30 seconds if enabled
    const interval = setInterval(() => {
      if (autoRefresh) {
        loadData();
      }
    }, 10000); // Reduced to 10 seconds for more real-time feel

    return () => clearInterval(interval);
  }, [autoRefresh]);

  const initializeConsole = () => {
    // Capture console logs
    const originalLog = console.log;
    const originalError = console.error;
    const originalWarn = console.warn;

    console.log = (...args) => {
      addLogEntry('info', args.join(' '));
      originalLog.apply(console, args);
    };

    console.error = (...args) => {
      addLogEntry('error', args.join(' '));
      originalError.apply(console, args);
    };

    console.warn = (...args) => {
      addLogEntry('warning', args.join(' '));
      originalWarn.apply(console, args);
    };

    // Capture unhandled errors
    window.addEventListener('error', (event) => {
      addLogEntry('error', `${event.message} at ${event.filename}:${event.lineno}:${event.colno}`);
    });

    // Capture unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      addLogEntry('error', `Unhandled promise rejection: ${event.reason}`);
    });
  };

  const addLogEntry = (level, message) => {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = {
      id: Date.now() + Math.random(),
      timestamp,
      level,
      message: typeof message === 'object' ? JSON.stringify(message) : message
    };

    setLogs(prevLogs => {
      const newLogs = [logEntry, ...prevLogs];
      return newLogs.slice(0, 1000); // Keep only last 1000 logs
    });
  };

  const loadData = async () => {
    try {
      setLoading(true);

      // Load admin stats
      const statsResponse = await apiService.getAdminStats();
      setStats(statsResponse);

      // Load all players
      const playersResponse = await apiService.getAdminPlayers();
      setPlayers(playersResponse.players || []);

      // Load chat messages
      const chatResponse = await apiService.getAdminChatMessages();
      setChatMessages(chatResponse.messages || []);

      // Load system info
      const systemResponse = await apiService.getAdminSystemInfo();
      setSystemInfo(systemResponse);

      // Load server logs
      const logsResponse = await apiService.getServerLogs(50);
      setServerLogs(logsResponse.logs || []);

      addLogEntry('info', 'Admin data refreshed successfully');
    } catch (error) {
      addLogEntry('error', `Failed to load admin data: ${error.message}`);
      console.error('Failed to load admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEditPlayer = (player) => {
    setSelectedPlayer(player);
    setEditData({
      username: player.username,
      kingdomName: player.kingdomName,
      empire: player.empire,
      bio: player.bio || '',
      location: player.location || '',
      motto: player.motto || '',
      isAdmin: player.isAdmin || false,
      resources: player.resources || { gold: 0, wood: 0, stone: 0, food: 0 }
    });
    setEditDialog(true);
  };

  const handleSavePlayer = async () => {
    try {
      setLoading(true);
      
      // Update player data
      await apiService.updatePlayerAdmin(selectedPlayer.username, editData);
      
      toast({
        title: "Player Updated",
        description: `Successfully updated ${editData.username}`,
      });

      addLogEntry('info', `Admin updated player: ${editData.username}`);
      setEditDialog(false);
      loadData(); // Refresh data
    } catch (error) {
      toast({
        title: "Update Failed",
        description: error.message,
        variant: "destructive"
      });
      addLogEntry('error', `Failed to update player ${editData.username}: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteMessage = async (messageId) => {
    try {
      await apiService.deleteMessage(messageId);
      toast({
        title: "Message Deleted",
        description: "Message has been removed",
      });
      addLogEntry('info', `Admin deleted message: ${messageId}`);
      loadData();
    } catch (error) {
      toast({
        title: "Delete Failed",
        description: error.message,
        variant: "destructive"
      });
      addLogEntry('error', `Failed to delete message: ${error.message}`);
    }
  };

  const clearLogs = () => {
    setLogs([]);
    addLogEntry('info', 'Console logs cleared');
  };

  const handleBroadcastMessage = async () => {
    if (!broadcastMessage.trim()) {
      toast({
        title: "Invalid Input",
        description: "Broadcast message cannot be empty",
        variant: "destructive"
      });
      return;
    }

    try {
      await apiService.broadcastMessage(broadcastMessage);
      toast({
        title: "Broadcast Sent",
        description: "System message has been sent to all players",
      });
      setBroadcastMessage('');
      addLogEntry('info', `Broadcast sent: ${broadcastMessage}`);
    } catch (error) {
      toast({
        title: "Broadcast Failed",
        description: error.message,
        variant: "destructive"
      });
      addLogEntry('error', `Broadcast failed: ${error.message}`);
    }
  };

  const handleResetPlayerResources = async (username) => {
    try {
      await apiService.resetPlayerResources(username);
      toast({
        title: "Resources Reset",
        description: `Resources have been reset for ${username}`,
      });
      addLogEntry('info', `Resources reset for player: ${username}`);
      loadData(); // Refresh data
    } catch (error) {
      toast({
        title: "Reset Failed",
        description: error.message,
        variant: "destructive"
      });
      addLogEntry('error', `Failed to reset resources for ${username}: ${error.message}`);
    }
  };

  const getLogLevelColor = (level) => {
    const colors = {
      info: 'text-blue-400',
      warning: 'text-yellow-400',
      error: 'text-red-400'
    };
    return colors[level] || 'text-slate-400';
  };

  const getLogLevelIcon = (level) => {
    const icons = {
      info: '🔵',
      warning: '🟡',
      error: '🔴'
    };
    return icons[level] || '⚪';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-red-400 to-red-600 bg-clip-text text-transparent">
              Admin Control Panel
            </h1>
            <p className="text-slate-400 mt-1">Medieval Empires Administration</p>
          </div>
          <div className="flex space-x-2">
            <Button 
              onClick={loadData} 
              disabled={loading}
              variant="outline"
            >
              <Refresh className="w-4 h-4 mr-2" />
              {loading ? 'Loading...' : 'Refresh'}
            </Button>
            <Button 
              onClick={() => setAutoRefresh(!autoRefresh)}
              variant={autoRefresh ? "default" : "outline"}
            >
              Auto-refresh: {autoRefresh ? 'ON' : 'OFF'}
            </Button>
          </div>
        </div>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="bg-slate-800/50 border-slate-700">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="players">Players</TabsTrigger>
            <TabsTrigger value="chat">Chat Management</TabsTrigger>
            <TabsTrigger value="console">Console & Logs</TabsTrigger>
            <TabsTrigger value="tools">Admin Tools</TabsTrigger>
            <TabsTrigger value="system">System Info</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-slate-400">Total Players</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-blue-400">{stats.totalPlayers || 0}</div>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-slate-400">Active Players</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-400">{stats.activePlayers || 0}</div>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-slate-400">Total Messages</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-amber-400">{stats.totalMessages || 0}</div>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-slate-400">Total Power</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-purple-400">{(stats.totalPower || 0).toLocaleString()}</div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Players Tab */}
          <TabsContent value="players" className="space-y-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Users className="w-5 h-5" />
                  <span>Player Management</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Username</TableHead>
                        <TableHead>Kingdom</TableHead>
                        <TableHead>Empire</TableHead>
                        <TableHead>Power</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {players.map((player) => (
                        <TableRow key={player.username}>
                          <TableCell className="font-medium">
                            {player.username}
                            {player.isAdmin && <Badge variant="destructive" className="ml-2">Admin</Badge>}
                          </TableCell>
                          <TableCell>{player.kingdomName}</TableCell>
                          <TableCell className="capitalize">{player.empire}</TableCell>
                          <TableCell>{(player.power || 0).toLocaleString()}</TableCell>
                          <TableCell>
                            <Badge variant={player.lastActive ? "default" : "secondary"}>
                              {player.lastActive ? 'Active' : 'Inactive'}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <div className="flex space-x-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleEditPlayer(player)}
                              >
                                <Edit className="w-4 h-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Chat Management Tab */}
          <TabsContent value="chat" className="space-y-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <MessageSquare className="w-5 h-5" />
                  <span>Chat Messages</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {chatMessages.map((message) => (
                    <div key={message.id} className="flex justify-between items-start p-3 bg-slate-700/50 rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="font-semibold text-amber-400">{message.username}</span>
                          <span className="text-xs text-slate-500">
                            {new Date(message.timestamp).toLocaleString()}
                          </span>
                        </div>
                        <p className="text-slate-300">{message.content}</p>
                      </div>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleDeleteMessage(message.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Console & Logs Tab */}
          <TabsContent value="console" className="space-y-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Terminal className="w-5 h-5" />
                    <span>Debug Console</span>
                  </div>
                  <div className="flex space-x-2">
                    <Badge variant="outline">{logs.length} entries</Badge>
                    <Button size="sm" variant="outline" onClick={clearLogs}>
                      Clear
                    </Button>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-black/50 rounded-lg p-4 font-mono text-sm max-h-96 overflow-y-auto">
                  {logs.length === 0 ? (
                    <p className="text-slate-500">No logs yet. Console output will appear here.</p>
                  ) : (
                    logs.map((log) => (
                      <div key={log.id} className="flex items-start space-x-2 mb-1">
                        <span className="text-slate-500 text-xs w-20 flex-shrink-0">{log.timestamp}</span>
                        <span className="w-4 flex-shrink-0">{getLogLevelIcon(log.level)}</span>
                        <span className={getLogLevelColor(log.level)}>{log.message}</span>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Log Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-400">Info</p>
                      <p className="text-2xl font-bold text-blue-400">
                        {logs.filter(log => log.level === 'info').length}
                      </p>
                    </div>
                    <div className="text-blue-400">🔵</div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-400">Warnings</p>
                      <p className="text-2xl font-bold text-yellow-400">
                        {logs.filter(log => log.level === 'warning').length}
                      </p>
                    </div>
                    <div className="text-yellow-400">🟡</div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-slate-800/50 border-slate-700">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-400">Errors</p>
                      <p className="text-2xl font-bold text-red-400">
                        {logs.filter(log => log.level === 'error').length}
                      </p>
                    </div>
                    <div className="text-red-400">🔴</div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* System Info Tab */}
          <TabsContent value="system" className="space-y-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Settings className="w-5 h-5" />
                  <span>System Information</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <p className="text-sm text-slate-400">Server Status</p>
                    <Badge variant={systemInfo.status === 'healthy' ? 'default' : 'destructive'}>
                      {systemInfo.status || 'Unknown'}
                    </Badge>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm text-slate-400">Database</p>
                    <Badge variant={systemInfo.database === 'connected' ? 'default' : 'destructive'}>
                      {systemInfo.database || 'Unknown'}
                    </Badge>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm text-slate-400">CPU Usage</p>
                    <p className="text-white">{systemInfo.cpuUsage || 'N/A'}</p>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm text-slate-400">Memory Usage</p>
                    <p className="text-white">{systemInfo.memoryUsage || 'N/A'}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Edit Player Dialog */}
        <Dialog open={editDialog} onOpenChange={setEditDialog}>
          <DialogContent className="bg-slate-800 border-slate-700 max-w-2xl">
            <DialogHeader>
              <DialogTitle>Edit Player: {selectedPlayer?.username}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Username</Label>
                  <Input
                    value={editData.username || ''}
                    onChange={(e) => setEditData({...editData, username: e.target.value})}
                    className="bg-slate-600 border-slate-500"
                    disabled
                  />
                </div>
                <div className="space-y-2">
                  <Label>Kingdom Name</Label>
                  <Input
                    value={editData.kingdomName || ''}
                    onChange={(e) => setEditData({...editData, kingdomName: e.target.value})}
                    className="bg-slate-600 border-slate-500"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Empire</Label>
                <Select 
                  value={editData.empire} 
                  onValueChange={(value) => setEditData({...editData, empire: value})}
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
              </div>

              <div className="space-y-2">
                <Label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={editData.isAdmin || false}
                    onChange={(e) => setEditData({...editData, isAdmin: e.target.checked})}
                    className="rounded"
                  />
                  <span>Admin User</span>
                </Label>
                <p className="text-xs text-slate-400">Grant administrative privileges to this user</p>
              </div>

              <div className="space-y-2">
                <Label>Resources</Label>
                <div className="grid grid-cols-2 gap-2">
                  {['gold', 'wood', 'stone', 'food'].map(resource => (
                    <div key={resource} className="space-y-1">
                      <Label className="capitalize text-xs">{resource}</Label>
                      <Input
                        type="number"
                        value={editData.resources?.[resource] || 0}
                        onChange={(e) => setEditData({
                          ...editData, 
                          resources: {
                            ...editData.resources,
                            [resource]: parseInt(e.target.value) || 0
                          }
                        })}
                        className="bg-slate-600 border-slate-500"
                      />
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex space-x-2">
                <Button 
                  onClick={handleSavePlayer}
                  disabled={loading}
                  className="flex-1 bg-green-600 hover:bg-green-700"
                >
                  {loading ? 'Saving...' : 'Save Changes'}
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setEditDialog(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default AdminPanel;