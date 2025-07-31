// Mock chat data for the medieval empire game
class MockChatData {
  constructor() {
    this.initializeData();
  }

  initializeData() {
    // Load from localStorage or use defaults
    const savedData = localStorage.getItem('medievalChatData');
    if (savedData) {
      const data = JSON.parse(savedData);
      this.globalMessages = data.globalMessages || this.generateInitialMessages();
      this.privateMessages = data.privateMessages || [];
      this.onlineUsers = data.onlineUsers || this.generateOnlineUsers();
    } else {
      this.globalMessages = this.generateInitialMessages();
      this.privateMessages = [];
      this.onlineUsers = this.generateOnlineUsers();
    }
  }

  generateInitialMessages() {
    const messages = [
      {
        id: 1,
        username: 'admin',
        content: 'Welcome to Medieval Empires! Build your kingdom and conquer your enemies!',
        timestamp: Date.now() - 3600000,
        empire: 'system'
      },
      {
        id: 2,
        username: 'KingArthur',
        content: 'Greetings fellow rulers! May your kingdoms prosper!',
        timestamp: Date.now() - 3000000,
        empire: 'norman'
      },
      {
        id: 3,
        username: 'VikingRagnar',
        content: 'The seas belong to the Vikings! Who dares challenge us?',
        timestamp: Date.now() - 2400000,
        empire: 'viking'
      },
      {
        id: 4,
        username: 'QueenEleanor',
        content: 'Trade routes are open! Looking for stone and wood.',
        timestamp: Date.now() - 1800000,
        empire: 'norman'
      },
      {
        id: 5,
        username: 'SaxonAlfred',
        content: 'Our farms are flourishing this season. Food for all!',
        timestamp: Date.now() - 1200000,
        empire: 'saxon'
      }
    ];

    return messages;
  }

  generateOnlineUsers() {
    return [
      { username: 'admin', kingdomName: 'System Admin', empire: 'system', power: 999999 },
      { username: 'KingArthur', kingdomName: "Arthur's Camelot", empire: 'norman', power: 5420 },
      { username: 'VikingRagnar', kingdomName: 'Ragnar\'s Hold', empire: 'viking', power: 4890 },
      { username: 'SaxonEdward', kingdomName: 'Edward\'s Realm', empire: 'saxon', power: 4560 },
      { username: 'CelticBoudica', kingdomName: 'Boudica\'s Lands', empire: 'celtic', power: 4200 },
      { username: 'FrankishCharles', kingdomName: 'Charles\' Empire', empire: 'frankish', power: 3980 },
      { username: 'QueenEleanor', kingdomName: 'Eleanor\'s Kingdom', empire: 'norman', power: 3750 },
      { username: 'VikingErik', kingdomName: 'Erik\'s Stronghold', empire: 'viking', power: 3400 },
      { username: 'SaxonAlfred', kingdomName: 'Alfred\'s Domain', empire: 'saxon', power: 3200 }
    ];
  }

  getGlobalMessages() {
    return [...this.globalMessages].sort((a, b) => a.timestamp - b.timestamp);
  }

  addGlobalMessage(username, content, empire) {
    const newMessage = {
      id: Date.now() + Math.random(),
      username,
      content,
      timestamp: Date.now(),
      empire
    };

    this.globalMessages.push(newMessage);
    
    // Keep only last 100 messages
    if (this.globalMessages.length > 100) {
      this.globalMessages = this.globalMessages.slice(-100);
    }

    this.saveData();
    return newMessage;
  }

  getPrivateMessages(username) {
    return this.privateMessages.filter(msg => 
      msg.sender === username || msg.receiver === username
    ).sort((a, b) => a.timestamp - b.timestamp);
  }

  addPrivateMessage(sender, receiver, content) {
    const newMessage = {
      id: Date.now() + Math.random(),
      sender,
      receiver,
      content,
      timestamp: Date.now()
    };

    this.privateMessages.push(newMessage);
    
    // Keep only last 500 private messages
    if (this.privateMessages.length > 500) {
      this.privateMessages = this.privateMessages.slice(-500);
    }

    this.saveData();
    return newMessage;
  }

  getOnlineUsers() {
    // Simulate users going online/offline
    return this.onlineUsers.map(user => ({
      ...user,
      lastSeen: Date.now() - Math.floor(Math.random() * 300000) // Last seen within 5 minutes
    }));
  }

  addOnlineUser(userData) {
    const existingIndex = this.onlineUsers.findIndex(user => user.username === userData.username);
    if (existingIndex >= 0) {
      this.onlineUsers[existingIndex] = { ...this.onlineUsers[existingIndex], ...userData };
    } else {
      this.onlineUsers.push(userData);
    }
    this.saveData();
  }

  removeOnlineUser(username) {
    this.onlineUsers = this.onlineUsers.filter(user => user.username !== username);
    this.saveData();
  }

  deleteMessage(messageId) {
    this.globalMessages = this.globalMessages.filter(msg => msg.id !== messageId);
    this.saveData();
  }

  clearMessages() {
    this.globalMessages = [];
    this.privateMessages = [];
    this.saveData();
  }

  // Simulate AI chat activity
  simulateActivity() {
    const aiUsers = ['KingArthur', 'VikingRagnar', 'SaxonEdward', 'CelticBoudica', 'QueenEleanor'];
    const messages = [
      'My castle grows stronger each day!',
      'Looking for allies in the northern regions.',
      'The harvest was bountiful this season.',
      'Beware, raiders approach from the east!',
      'Trade caravans welcome in our lands.',
      'Our blacksmiths forge the finest weapons.',
      'The winter preparations are complete.',
      'Who wishes to form an alliance?',
      'My armies are ready for battle!'
    ];

    if (Math.random() < 0.3) { // 30% chance every call
      const randomUser = aiUsers[Math.floor(Math.random() * aiUsers.length)];
      const randomMessage = messages[Math.floor(Math.random() * messages.length)];
      const userEmpire = this.onlineUsers.find(u => u.username === randomUser)?.empire || 'norman';
      
      this.addGlobalMessage(randomUser, randomMessage, userEmpire);
    }
  }

  saveData() {
    const dataToSave = {
      globalMessages: this.globalMessages,
      privateMessages: this.privateMessages,
      onlineUsers: this.onlineUsers
    };
    localStorage.setItem('medievalChatData', JSON.stringify(dataToSave));
  }

  resetData() {
    localStorage.removeItem('medievalChatData');
    this.initializeData();
  }
}

export const mockChatData = new MockChatData();

// Simulate AI chat activity every 30 seconds
setInterval(() => {
  mockChatData.simulateActivity();
}, 30000);