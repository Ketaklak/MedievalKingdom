import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import AuthScreen from "./components/AuthScreen";
import MultiplayerDashboard from "./components/MultiplayerDashboard";
import { Toaster } from "./components/ui/toaster";
import apiService from "./services/apiService";

function App() {
  const [currentPlayer, setCurrentPlayer] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const checkAuthStatus = async () => {
      const token = localStorage.getItem('authToken');
      if (token) {
        try {
          const userData = await apiService.getCurrentUser();
          setCurrentPlayer({
            username: userData.user.username,
            kingdomName: userData.user.kingdomName,
            empire: userData.user.empire,
            isAdmin: userData.user.isAdmin,
            ...userData.player
          });
        } catch (error) {
          console.error('Error checking auth status:', error);
          // Clear invalid token
          localStorage.removeItem('authToken');
          localStorage.removeItem('currentMedievalPlayer');
        }
      }
      setIsLoading(false);
    };

    checkAuthStatus();
  }, []);

  const handleLogin = async (playerData) => {
    try {
      let result;
      
      if (playerData.isRegistration) {
        // Registration
        result = await apiService.register({
          username: playerData.username,
          password: playerData.password,
          email: playerData.email || `${playerData.username}@medievalempires.com`,
          kingdomName: playerData.kingdomName,
          empire: playerData.empire
        });
      } else {
        // Login
        result = await apiService.login({
          username: playerData.username,
          password: playerData.password
        });
      }
      
      if (result.user) {
        // Get full player data
        const fullUserData = await apiService.getCurrentUser();
        const player = {
          username: result.user.username,
          kingdomName: result.user.kingdomName,
          empire: result.user.empire,
          isAdmin: result.user.isAdmin,
          ...fullUserData.player
        };
        
        setCurrentPlayer(player);
        localStorage.setItem('currentMedievalPlayer', JSON.stringify(player));
      }
    } catch (error) {
      console.error('Login/Registration failed:', error);
      throw error;
    }
  };

  const handleLogout = () => {
    apiService.logout();
    setCurrentPlayer(null);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading Medieval Empires...</div>
      </div>
    );
  }

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={
            currentPlayer ? 
              <MultiplayerDashboard player={currentPlayer} onLogout={handleLogout} /> : 
              <AuthScreen onLogin={handleLogin} />
          } />
        </Routes>
      </BrowserRouter>
      <Toaster />
    </div>
  );
}

export default App;