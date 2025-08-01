import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Coins, Scroll, Package, Sword, Hammer } from 'lucide-react';
import apiService from '../services/apiService';
import { useToast } from '../hooks/use-toast';

const ShopModal = ({ isOpen, onClose, player, onUpdate }) => {
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const shopItems = [
    {
      id: 'race_change_scroll',
      name: 'Race Change Scroll',
      description: 'Allows you to change your empire race once. Use wisely!',
      icon: Scroll,
      price: { gold: 1000, gems: 50 },
      category: 'Special',
      rarity: 'legendary'
    },
    {
      id: 'resource_pack',
      name: 'Resource Pack',
      description: 'Contains 500 of each basic resource (Gold, Wood, Stone, Food)',
      icon: Package,
      price: { gold: 2000 },
      category: 'Resources',
      rarity: 'common'
    },
    {
      id: 'army_boost',
      name: 'Army Training Boost',
      description: 'Instantly train 50 soldiers, 25 archers, and 10 cavalry',
      icon: Sword,
      price: { gold: 1500, food: 500 },
      category: 'Military',
      rarity: 'rare'
    },
    {
      id: 'construction_boost',
      name: 'Construction Speed Boost',
      description: 'Complete one building upgrade instantly',
      icon: Hammer,
      price: { gold: 800, wood: 200, stone: 200 },
      category: 'Buildings',
      rarity: 'uncommon'
    }
  ];

  const getRarityColor = (rarity) => {
    const colors = {
      common: 'text-gray-400 border-gray-600',
      uncommon: 'text-green-400 border-green-600',
      rare: 'text-blue-400 border-blue-600',
      epic: 'text-purple-400 border-purple-600',
      legendary: 'text-amber-400 border-amber-600'
    };
    return colors[rarity] || colors.common;
  };

  const canAfford = (item) => {
    if (!player?.resources) return false;
    
    return Object.entries(item.price).every(([resource, cost]) => {
      if (resource === 'gems') {
        return (player.gems || 0) >= cost;
      }
      return (player.resources[resource] || 0) >= cost;
    });
  };

  const formatPrice = (price) => {
    return Object.entries(price).map(([resource, amount]) => {
      const resourceIcons = {
        gold: '🪙',
        wood: '🪵',
        stone: '🪨',
        food: '🌾',
        gems: '💎'
      };
      return `${resourceIcons[resource] || '•'} ${amount.toLocaleString()}`;
    }).join(' ');
  };

  const handlePurchase = async (item) => {
    if (!canAfford(item)) {
      toast({
        title: "Insufficient Resources",
        description: "You don't have enough resources to purchase this item",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const result = await apiService.purchaseShopItem(item.id);
      if (result.success) {
        toast({
          title: "Purchase Successful!",
          description: `You have purchased: ${item.name}`,
        });
        
        // Update player data if provided
        if (onUpdate && result.player) {
          onUpdate(result.player);
        }
      }
    } catch (error) {
      toast({
        title: "Purchase Failed",
        description: error.message,
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-slate-800 border-slate-700 max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Coins className="w-6 h-6 text-amber-400" />
            <span>Kingdom Shop</span>
          </DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          {shopItems.map((item) => {
            const IconComponent = item.icon;
            const affordable = canAfford(item);
            
            return (
              <Card 
                key={item.id} 
                className={`bg-slate-700/50 border-slate-600 ${getRarityColor(item.rarity)} ${!affordable ? 'opacity-60' : ''}`}
              >
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-slate-600 rounded-lg">
                        <IconComponent className="w-6 h-6 text-amber-400" />
                      </div>
                      <div>
                        <h3 className="font-semibold">{item.name}</h3>
                        <Badge variant="outline" className={`text-xs ${getRarityColor(item.rarity)}`}>
                          {item.rarity}
                        </Badge>
                      </div>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-slate-300">{item.description}</p>
                  
                  <div className="space-y-2">
                    <p className="text-xs text-slate-400">Price:</p>
                    <p className="text-sm font-mono">{formatPrice(item.price)}</p>
                  </div>

                  <Button
                    onClick={() => handlePurchase(item)}
                    disabled={!affordable || loading}
                    className={`w-full ${affordable ? 'bg-amber-600 hover:bg-amber-700' : 'bg-slate-600'}`}
                  >
                    {loading ? 'Purchasing...' : affordable ? 'Purchase' : 'Insufficient Resources'}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        <div className="mt-6 text-center">
          <Button variant="outline" onClick={onClose}>
            Close Shop
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ShopModal;