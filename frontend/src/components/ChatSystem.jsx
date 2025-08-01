import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { ScrollArea } from './ui/scroll-area';
import { MessageCircle, Send, Users, Crown, Shield } from 'lucide-react';
import apiService from '../services/apiService';
import { useToast } from '../hooks/use-toast';

const ChatSystem = ({ player }) => {
  const [globalMessages, setGlobalMessages] = useState([]);
  const [privateMessages, setPrivateMessages] = useState([]);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [selectedPrivateUser, setSelectedPrivateUser] = useState(null);
  const [newPrivateMessage, setNewPrivateMessage] = useState('');
  const [loading, setLoading] = useState(false);
  
  const globalChatRef = useRef(null);
  const privateChatRef = useRef(null);
  const { toast } = useToast();

  // Fetch chat data
  const fetchChatData = async () => {
    try {
      const [globalData, privateData, usersData] = await Promise.all([
        apiService.getGlobalMessages(),
        apiService.getPrivateMessages(),
        apiService.getOnlineUsers()
      ]);
      
      setGlobalMessages(globalData.messages || []);
      setPrivateMessages(privateData.messages || []);
      setOnlineUsers(usersData.users || []);
    } catch (error) {
      console.error('Failed to fetch chat data:', error);
    }
  };

  // Initial load and periodic updates
  useEffect(() => {
    fetchChatData();
    
    const interval = setInterval(fetchChatData, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    if (globalChatRef.current) {
      globalChatRef.current.scrollTop = globalChatRef.current.scrollHeight;
    }
  }, [globalMessages]);

  useEffect(() => {
    if (privateChatRef.current) {
      privateChatRef.current.scrollTop = privateChatRef.current.scrollHeight;
    }
  }, [privateMessages]);

  const sendGlobalMessage = async (e) => {
    e.preventDefault();
    if (newMessage.trim() && !loading) {
      setLoading(true);
      try {
        await apiService.sendGlobalMessage(newMessage.trim());
        setNewMessage('');
        // Refresh messages
        const data = await apiService.getGlobalMessages();
        setGlobalMessages(data.messages || []);
      } catch (error) {
        toast({
          title: "Failed to send message",
          description: error.message,
          variant: "destructive"
        });
      } finally {
        setLoading(false);
      }
    }
  };

  const sendPrivateMessage = async (e) => {
    e.preventDefault();
    if (newPrivateMessage.trim() && selectedPrivateUser && !loading) {
      setLoading(true);
      try {
        await apiService.sendPrivateMessage(selectedPrivateUser.username, newPrivateMessage.trim());
        setNewPrivateMessage('');
        // Refresh private messages
        const data = await apiService.getPrivateMessages();
        setPrivateMessages(data.messages || []);
      } catch (error) {
        toast({
          title: "Failed to send private message",
          description: error.message,
          variant: "destructive"
        });
      } finally {
        setLoading(false);
      }
    }
  };

  const getUserRole = (username) => {
    if (username === 'admin') return 'admin';
    if (username.includes('King') || username.includes('Queen')) return 'vip';
    return 'player';
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'admin': return <Shield className="w-4 h-4 text-red-400" />;
      case 'vip': return <Crown className="w-4 h-4 text-amber-400" />;
      default: return null;
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin': return 'text-red-400';
      case 'vip': return 'text-amber-400';
      default: return 'text-slate-300';
    }
  };

  return (
    <div className="h-full">
      <Tabs defaultValue="global" className="h-full flex flex-col">
        <TabsList className="grid w-full grid-cols-3 bg-slate-800/50">
          <TabsTrigger value="global">Global Chat</TabsTrigger>
          <TabsTrigger value="private">Private Messages</TabsTrigger>
          <TabsTrigger value="online">Online Users</TabsTrigger>
        </TabsList>

        <TabsContent value="global" className="flex-1 flex flex-col space-y-4">
          <Card className="bg-slate-800/50 border-slate-700 flex-1 flex flex-col">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center space-x-2">
                <MessageCircle className="w-5 h-5 text-blue-400" />
                <span>Global Chat</span>
                <Badge variant="outline">{onlineUsers.length} online</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col p-0">
              <ScrollArea 
                ref={globalChatRef}
                className="flex-1 px-4 pb-4"
                style={{ maxHeight: '300px' }}
              >
                <div className="space-y-3">
                  {globalMessages.map((message) => {
                    const role = getUserRole(message.username);
                    return (
                      <div key={message.id} className="flex items-start space-x-3">
                        <div className="flex items-center space-x-2 min-w-0">
                          {getRoleIcon(role)}
                          <span className={`font-medium text-sm ${getRoleColor(role)}`}>
                            {message.username}
                          </span>
                          <Badge variant="secondary" className="text-xs">
                            {message.empire}
                          </Badge>
                          <span className="text-xs text-slate-500">
                            {formatTime(message.timestamp)}
                          </span>
                        </div>
                        <p className="text-sm text-slate-300 break-words flex-1">
                          {message.content}
                        </p>
                      </div>
                    );
                  })}
                </div>
              </ScrollArea>
              <div className="p-4 border-t border-slate-700">
                <form onSubmit={sendGlobalMessage} className="flex space-x-2">
                  <Input
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Type your message..."
                    className="bg-slate-700 border-slate-600"
                    maxLength={200}
                  />
                  <Button type="submit" size="sm" className="bg-blue-600 hover:bg-blue-700" disabled={loading}>
                    <Send className="w-4 h-4" />
                  </Button>
                </form>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="private" className="flex-1 flex flex-col space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 h-full">
            {/* User List */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">Select User</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <ScrollArea className="h-40">
                  <div className="space-y-2 p-4">
                    {onlineUsers
                      .filter(user => user.username !== player.username)
                      .map(user => {
                        const role = getUserRole(user.username);
                        return (
                          <div
                            key={user.username}
                            onClick={() => setSelectedPrivateUser(user)}
                            className={`p-2 rounded cursor-pointer transition-colors ${
                              selectedPrivateUser?.username === user.username
                                ? 'bg-blue-600/20 border border-blue-600'
                                : 'bg-slate-700/50 hover:bg-slate-700'
                            }`}
                          >
                            <div className="flex items-center space-x-2">
                              {getRoleIcon(role)}
                              <span className={`text-sm ${getRoleColor(role)}`}>
                                {user.username}
                              </span>
                            </div>
                            <p className="text-xs text-slate-400">{user.empire}</p>
                          </div>
                        );
                      })}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Private Chat */}
            <div className="md:col-span-2">
              <Card className="bg-slate-800/50 border-slate-700 h-full flex flex-col">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm">
                    {selectedPrivateUser 
                      ? `Chat with ${selectedPrivateUser.username}` 
                      : 'Select a user to chat'
                    }
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex-1 flex flex-col p-0">
                  {selectedPrivateUser ? (
                    <>
                      <ScrollArea 
                        ref={privateChatRef}
                        className="flex-1 px-4 pb-4"
                        style={{ maxHeight: '200px' }}
                      >
                        <div className="space-y-3">
                          {privateMessages
                            .filter(msg => 
                              (msg.sender === selectedPrivateUser.username && msg.receiver === player.username) ||
                              (msg.sender === player.username && msg.receiver === selectedPrivateUser.username)
                            )
                            .map(message => (
                              <div 
                                key={message.id} 
                                className={`flex ${message.sender === player.username ? 'justify-end' : 'justify-start'}`}
                              >
                                <div className={`max-w-xs p-3 rounded-lg ${
                                  message.sender === player.username 
                                    ? 'bg-blue-600 text-white' 
                                    : 'bg-slate-700 text-slate-300'
                                }`}>
                                  <p className="text-sm">{message.content}</p>
                                  <p className="text-xs opacity-70 mt-1">
                                    {formatTime(message.timestamp)}
                                  </p>
                                </div>
                              </div>
                            ))}
                        </div>
                      </ScrollArea>
                      <div className="p-4 border-t border-slate-700">
                        <form onSubmit={sendPrivateMessage} className="flex space-x-2">
                          <Input
                            value={newPrivateMessage}
                            onChange={(e) => setNewPrivateMessage(e.target.value)}
                            placeholder="Type private message..."
                            className="bg-slate-700 border-slate-600"
                            maxLength={200}
                          />
                          <Button type="submit" size="sm" className="bg-blue-600 hover:bg-blue-700">
                            <Send className="w-4 h-4" />
                          </Button>
                        </form>
                      </div>
                    </>
                  ) : (
                    <div className="flex-1 flex items-center justify-center text-slate-400">
                      Select a user to start private messaging
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="online" className="flex-1">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="w-5 h-5 text-green-400" />
                <span>Online Users ({onlineUsers.length})</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-64">
                <div className="space-y-3">
                  {onlineUsers.map(user => {
                    const role = getUserRole(user.username);
                    return (
                      <div key={user.username} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          {getRoleIcon(role)}
                          <div>
                            <p className={`font-medium ${getRoleColor(role)}`}>
                              {user.username}
                            </p>
                            <p className="text-sm text-slate-400">{user.kingdomName}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge variant="secondary">{user.empire}</Badge>
                          <p className="text-xs text-slate-400 mt-1">
                            Power: {user.power?.toLocaleString() || 'N/A'}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ChatSystem;