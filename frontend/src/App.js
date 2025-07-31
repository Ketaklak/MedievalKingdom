import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import AuthScreen from "./components/AuthScreen";
import MultiplayerDashboard from "./components/MultiplayerDashboard";
import { Toaster } from "./components/ui/toaster";
import { mockMultiplayerData } from "./utils/mockMultiplayerData";

function App() {
  const [currentPlayer, setCurrentPlayer] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const savedPlayer = localStorage.getItem('currentMedievalPlayer');
    if (savedPlayer) {
      try {
        const playerData = JSON.parse(savedPlayer);
        setCurrentPlayer(playerData);
      } catch (error) {
        console.error('Error loading saved player:', error);
        localStorage.removeItem('currentMedievalPlayer');
      }
    }
    setIsLoading(false);
  }, []);

  const handleLogin = (playerData) => {
    // Register or login player
    const player = mockMultiplayerData.registerPlayer(playerData);
    setCurrentPlayer(player);
    localStorage.setItem('currentMedievalPlayer', JSON.stringify(player));
  };

  const handleLogout = () => {
    setCurrentPlayer(null);
    localStorage.removeItem('currentMedievalPlayer');
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