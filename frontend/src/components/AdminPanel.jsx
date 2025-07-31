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
import { Shield, Users, MessageSquare, Settings, Edit, Trash2, Ban, CheckCircle } from 'lucide-react';
import { mockMultiplayerData } from '../utils/mockMultiplayerData';
import { mockChatData } from '../utils/mockChatData';

const AdminPanel = ({ currentUser }) => {
  const [players, setPlayers] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [editDialog, setEditDialog] = useState(false);
  const [editData, setEditData] = useState({});
  const [banDialog, setBanDialog] = useState(false);
  const [systemMessage, setSystemMessage] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = () => {
    // Load all players
    const allPlayers = Object.values(mockMultiplayerData.players).map(player => ({
      ...player,
      power: mockMultiplayerData.calculatePlayerPower(player.username),
      status: 'active', // Mock status
      lastLogin: new Date(player.lastActive).toLocaleString(),
      banned: false // Mock ban status
    }));
    setPlayers(allPlayers);

    // Load chat messages
    setChatMessages(mockChatData.getGlobalMessages().slice(-50));
  };

  const handleEditPlayer = (player) => {
    setSelectedPlayer(player);
    setEditData({
      username: player.username,
      kingdomName: player.kingdomName,
      empire: player.empire,
      bio: player.bio || '',
      resources: { ...player.resources },
      army: player.army
    });
    setEditDialog(true);
  };

  const handleSavePlayer = () => {
    if (selectedPlayer) {
      // Update player data
      const playerData = mockMultiplayerData.players[selectedPlayer.username];
      if (playerData) {
        playerData.kingdomName = editData.kingdomName;
        playerData.empire = editData.empire;
        playerData.bio = editData.bio;
        playerData.resources = { ...editData.resources };
        playerData.army = editData.army;
        mockMultiplayerData.saveData();
      }
      setEditDialog(false);
      loadData();
    }
  };

  const handleDeletePlayer = (username) => {
    if (window.confirm(`Are you sure you want to delete player ${username}?`)) {
      delete mockMultiplayerData.players[username];
      mockMultiplayerData.saveData();
      loadData();
    }
  };

  const handleBanPlayer = (username) => {
    setSelectedPlayer({ username });
    setBanDialog(true);
  };

  const handleSendSystemMessage = () => {
    if (systemMessage.trim()) {
      mockChatData.addGlobalMessage('SYSTEM', systemMessage.trim(), 'system');
      setSystemMessage('');
      loadData();
    }
  };

  const handleDeleteMessage = (messageId) => {
    mockChatData.deleteMessage(messageId);
    loadData();
  };

  const getTotalStats = () => {
    const totalPlayers = players.length;
    const activePlayers = players.filter(p => p.status === 'active').length;
    const totalMessages = chatMessages.length;
    const totalPower = players.reduce((sum, p) => sum + p.power, 0);

    return { totalPlayers, activePlayers, totalMessages, totalPower };
  };

  const stats = getTotalStats();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-red-400 to-red-600 bg-clip-text text-transparent">
              Administration Panel
            </h1>
            <p className="text-slate-400">Welcome, {currentUser.username}</p>
          </div>
          <Badge variant="destructive" className="px-4 py-2">
            <Shield className="w-4 h-4 mr-2" />
            ADMIN ACCESS
          </Badge>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <Users className="w-8 h-8 text-blue-400" />
                <div>
                  <p className="text-2xl font-bold">{stats.totalPlayers}</p>
                  <p className="text-sm text-slate-400">Total Players</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-8 h-8 text-green-400" />
                <div>
                  <p className="text-2xl font-bold">{stats.activePlayers}</p>
                  <p className="text-sm text-slate-400">Active Players</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <MessageSquare className="w-8 h-8 text-purple-400" />
                <div>
                  <p className="text-2xl font-bold">{stats.totalMessages}</p>
                  <p className="text-sm text-slate-400">Chat Messages</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-slate-800/50 border-slate-700">
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <Settings className="w-8 h-8 text-amber-400" />
                <div>
                  <p className="text-2xl font-bold">{stats.totalPower.toLocaleString()}</p>
                  <p className="text-sm text-slate-400">Total Power</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="players" className="w-full">
          <TabsList className="grid w-full grid-cols-3 bg-slate-800/50">
            <TabsTrigger value="players">Player Management</TabsTrigger>
            <TabsTrigger value="chat">Chat Moderation</TabsTrigger>
            <TabsTrigger value="system">System Tools</TabsTrigger>
          </TabsList>

          <TabsContent value="players" className="space-y-4">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle>Player Management</CardTitle>
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
                        <TableHead>Resources</TableHead>
                        <TableHead>Last Login</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {players.map(player => (
                        <TableRow key={player.username}>
                          <TableCell className="font-medium">{player.username}</TableCell>
                          <TableCell>{player.kingdomName}</TableCell>
                          <TableCell>
                            <Badge variant="secondary">{player.empire}</Badge>
                          </TableCell>
                          <TableCell>{player.power.toLocaleString()}</TableCell>
                          <TableCell>
                            <div className="text-xs">
                              G:{player.resources.gold} W:{player.resources.wood} 
                              S:{player.resources.stone} F:{player.resources.food}
                            </div>
                          </TableCell>
                          <TableCell className="text-xs">{player.lastLogin}</TableCell>
                          <TableCell>
                            <div className="flex space-x-2">
                              <Button 
                                size="sm" 
                                variant="outline"
                                onClick={() => handleEditPlayer(player)}
                              >
                                <Edit className="w-3 h-3" />
                              </Button>
                              <Button 
                                size="sm" 
                                variant="destructive"
                                onClick={() => handleBanPlayer(player.username)}
                              >
                                <Ban className="w-3 h-3" />
                              </Button>
                              <Button 
                                size="sm" 
                                variant="destructive"
                                onClick={() => handleDeletePlayer(player.username)}
                              >
                                <Trash2 className="w-3 h-3" />
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

          <TabsContent value="chat" className="space-y-4">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle>Chat Moderation</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* System Message */}
                  <div className="flex space-x-2">
                    <Input
                      value={systemMessage}
                      onChange={(e) => setSystemMessage(e.target.value)}
                      placeholder="Send system message..."
                      className="bg-slate-700 border-slate-600"
                    />
                    <Button onClick={handleSendSystemMessage} className="bg-red-600 hover:bg-red-700">
                      Send System Message
                    </Button>
                  </div>

                  {/* Recent Messages */}
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {chatMessages.map(message => (
                      <div key={message.id} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="font-medium text-sm">{message.username}</span>
                            <Badge variant="secondary" className="text-xs">{message.empire}</Badge>
                            <span className="text-xs text-slate-400">
                              {new Date(message.timestamp).toLocaleString()}
                            </span>
                          </div>
                          <p className="text-sm text-slate-300">{message.content}</p>
                        </div>
                        <Button 
                          size="sm" 
                          variant="destructive"
                          onClick={() => handleDeleteMessage(message.id)}
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="system" className="space-y-4">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle>System Tools</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Button 
                    className="bg-amber-600 hover:bg-amber-700"
                    onClick={() => {
                      if (window.confirm('Reset all player data?')) {
                        mockMultiplayerData.resetData();
                        loadData();
                      }
                    }}
                  >
                    Reset Game Data
                  </Button>
                  <Button 
                    className="bg-blue-600 hover:bg-blue-700"
                    onClick={() => {
                      mockChatData.clearMessages();
                      loadData();
                    }}
                  >
                    Clear Chat History
                  </Button>
                  <Button 
                    className="bg-green-600 hover:bg-green-700"
                    onClick={() => {
                      mockMultiplayerData.simulateAIActivity();
                      loadData();
                    }}
                  >
                    Simulate AI Activity
                  </Button>
                  <Button 
                    className="bg-purple-600 hover:bg-purple-700"
                    onClick={loadData}
                  >
                    Refresh Data
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Edit Player Dialog */}
        <Dialog open={editDialog} onOpenChange={setEditDialog}>
          <DialogContent className="bg-slate-800 border-slate-700">
            <DialogHeader>
              <DialogTitle>Edit Player: {selectedPlayer?.username}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Kingdom Name</Label>
                <Input
                  value={editData.kingdomName || ''}
                  onChange={(e) => setEditData({...editData, kingdomName: e.target.value})}
                  className="bg-slate-700 border-slate-600"
                />
              </div>
              <div className="space-y-2">
                <Label>Empire</Label>
                <Select value={editData.empire} onValueChange={(value) => setEditData({...editData, empire: value})}>
                  <SelectTrigger className="bg-slate-700 border-slate-600">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="norman">Norman</SelectItem>
                    <SelectItem value="viking">Viking</SelectItem>
                    <SelectItem value="saxon">Saxon</SelectItem>
                    <SelectItem value="celtic">Celtic</SelectItem>
                    <SelectItem value="frankish">Frankish</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Biography</Label>
                <Textarea
                  value={editData.bio || ''}
                  onChange={(e) => setEditData({...editData, bio: e.target.value})}
                  className="bg-slate-700 border-slate-600"
                  placeholder="Player biography..."
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Gold</Label>
                  <Input
                    type="number"
                    value={editData.resources?.gold || 0}
                    onChange={(e) => setEditData({
                      ...editData, 
                      resources: {...editData.resources, gold: parseInt(e.target.value) || 0}
                    })}
                    className="bg-slate-700 border-slate-600"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Army Size</Label>
                  <Input
                    type="number"
                    value={editData.army || 0}
                    onChange={(e) => setEditData({...editData, army: parseInt(e.target.value) || 0})}
                    className="bg-slate-700 border-slate-600"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setEditDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={handleSavePlayer} className="bg-blue-600 hover:bg-blue-700">
                  Save Changes
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