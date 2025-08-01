from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime

class ShopItem(BaseModel):
    id: str = Field(..., description="Unique item ID")
    name: str = Field(..., description="Item name")
    description: str = Field(..., description="Item description")
    category: str = Field(..., description="Item category")
    rarity: str = Field(..., description="Item rarity")
    price: Dict[str, int] = Field(..., description="Resource costs")
    available: bool = Field(default=True, description="Item availability")

class PurchaseRequest(BaseModel):
    itemId: str = Field(..., description="ID of item to purchase")
    quantity: int = Field(default=1, description="Quantity to purchase")

class Purchase(BaseModel):
    id: str = Field(..., description="Purchase ID")
    playerId: str = Field(..., description="Player ID")
    itemId: str = Field(..., description="Item ID")
    quantity: int = Field(..., description="Quantity purchased")
    totalCost: Dict[str, int] = Field(..., description="Total cost paid")
    purchaseDate: datetime = Field(default_factory=datetime.utcnow, description="Purchase timestamp")

class PlayerInventory(BaseModel):
    playerId: str = Field(..., description="Player ID")
    items: Dict[str, int] = Field(default_factory=dict, description="Item quantities")
    raceChangeScrolls: int = Field(default=0, description="Race change scrolls owned")
    
class ShopItemEffect(BaseModel):
    type: str = Field(..., description="Effect type (resources, army, construction, etc.)")
    values: Dict[str, int] = Field(..., description="Effect values")