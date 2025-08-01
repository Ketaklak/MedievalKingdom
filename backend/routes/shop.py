from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
import logging
import uuid
from datetime import datetime

from routes.auth import get_current_user
from database.mongodb import db
from models.shop import ShopItem, PurchaseRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/game/shop", tags=["shop"])

# Shop items configuration
SHOP_ITEMS = [
    {
        "id": "race_change_scroll",
        "name": "Race Change Scroll",
        "description": "Allows you to change your empire race once. Use wisely!",
        "category": "Special",
        "rarity": "legendary",
        "price": {"gold": 1000},
        "available": True
    },
    {
        "id": "resource_pack",
        "name": "Resource Pack",
        "description": "Contains 500 of each basic resource (Gold, Wood, Stone, Food)",
        "category": "Resources",
        "rarity": "common",
        "price": {"gold": 2000},
        "available": True
    },
    {
        "id": "army_boost",
        "name": "Army Training Boost",
        "description": "Instantly train 50 soldiers, 25 archers, and 10 cavalry",
        "category": "Military",
        "rarity": "rare",
        "price": {"gold": 1500, "food": 500},
        "available": True
    },
    {
        "id": "construction_boost",
        "name": "Construction Speed Boost",
        "description": "Complete one building upgrade instantly",
        "category": "Buildings",
        "rarity": "uncommon",
        "price": {"gold": 800, "wood": 200, "stone": 200},
        "available": True
    }
]

@router.get("/items")
async def get_shop_items():
    """Get all available shop items"""
    try:
        return {
            "success": True,
            "items": SHOP_ITEMS
        }
    except Exception as e:
        logger.error(f"Failed to get shop items: {e}")
        raise HTTPException(status_code=500, detail="Failed to get shop items")

@router.post("/buy/{item_id}")
async def buy_shop_item(
    item_id: str,
    purchase_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Purchase an item from the shop"""
    try:
        player = current_user["player"]
        
        # Find the item
        item = next((item for item in SHOP_ITEMS if item["id"] == item_id), None)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        if not item["available"]:
            raise HTTPException(status_code=400, detail="Item not available")
        
        quantity = purchase_data.get("quantity", 1)
        
        # Calculate total cost
        total_cost = {}
        for resource, cost in item["price"].items():
            total_cost[resource] = cost * quantity
        
        # Check if player can afford it
        for resource, cost in total_cost.items():
            if resource == "gems":
                player_amount = player.get("gems", 0)
            else:
                player_amount = player["resources"].get(resource, 0)
            
            if player_amount < cost:
                raise HTTPException(status_code=400, detail=f"Insufficient {resource}")
        
        # Deduct costs
        for resource, cost in total_cost.items():
            if resource == "gems":
                # Handle gems if implemented
                pass
            else:
                player["resources"][resource] -= cost
        
        # Apply item effects
        await apply_item_effects(player, item_id, quantity)
        
        # Update player in database
        await db.update_player(player["userId"], {
            "resources": player["resources"],
            "army": player.get("army", {}),
            "raceChangeScrolls": player.get("raceChangeScrolls", 0)
        })
        
        # Record purchase
        purchase = {
            "id": str(uuid.uuid4()),
            "playerId": player["userId"],
            "playerUsername": player["username"],
            "itemId": item_id,
            "itemName": item["name"],
            "quantity": quantity,
            "totalCost": total_cost,
            "purchaseDate": datetime.utcnow()
        }
        
        await db.db.shop_purchases.insert_one(purchase)
        
        return {
            "success": True,
            "message": f"Successfully purchased {item['name']}",
            "item": item,
            "quantity": quantity,
            "totalCost": total_cost,
            "player": player
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to purchase item: {e}")
        raise HTTPException(status_code=500, detail="Failed to purchase item")

async def apply_item_effects(player, item_id, quantity):
    """Apply the effects of purchased items"""
    try:
        if item_id == "race_change_scroll":
            # Add race change scrolls to player inventory
            current_scrolls = player.get("raceChangeScrolls", 0)
            player["raceChangeScrolls"] = current_scrolls + quantity
            
        elif item_id == "resource_pack":
            # Add 500 of each resource per pack
            resources_to_add = {
                "gold": 500 * quantity,
                "wood": 500 * quantity,
                "stone": 500 * quantity,
                "food": 500 * quantity
            }
            
            for resource, amount in resources_to_add.items():
                player["resources"][resource] = player["resources"].get(resource, 0) + amount
                
        elif item_id == "army_boost":
            # Add army units
            army_to_add = {
                "soldiers": 50 * quantity,
                "archers": 25 * quantity,
                "cavalry": 10 * quantity
            }
            
            if "army" not in player:
                player["army"] = {"soldiers": 0, "archers": 0, "cavalry": 0}
            
            for unit_type, amount in army_to_add.items():
                player["army"][unit_type] = player["army"].get(unit_type, 0) + amount
                
        elif item_id == "construction_boost":
            # This would need to be implemented with the construction queue system
            # For now, just add some resources as compensation
            player["resources"]["gold"] = player["resources"].get("gold", 0) + 200
            player["resources"]["wood"] = player["resources"].get("wood", 0) + 100
            player["resources"]["stone"] = player["resources"].get("stone", 0) + 100
            
    except Exception as e:
        logger.error(f"Failed to apply item effects: {e}")
        raise

@router.get("/purchases")
async def get_purchase_history(current_user: dict = Depends(get_current_user)):
    """Get player's purchase history"""
    try:
        player = current_user["player"]
        
        cursor = db.db.shop_purchases.find({
            "playerId": player["userId"]
        }).sort("purchaseDate", -1).limit(50)
        
        purchases = await cursor.to_list(length=50)
        
        # Convert ObjectId and datetime
        for purchase in purchases:
            purchase["id"] = str(purchase["_id"])
            del purchase["_id"]
            if "purchaseDate" in purchase and purchase["purchaseDate"]:
                purchase["purchaseDate"] = purchase["purchaseDate"].isoformat()
        
        return {
            "success": True,
            "purchases": purchases
        }
        
    except Exception as e:
        logger.error(f"Failed to get purchase history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get purchase history")

@router.get("/inventory")
async def get_player_inventory(current_user: dict = Depends(get_current_user)):
    """Get player's shop inventory/items"""
    try:
        player = current_user["player"]
        
        inventory = {
            "raceChangeScrolls": player.get("raceChangeScrolls", 0),
            # Add other inventory items as needed
        }
        
        return {
            "success": True,
            "inventory": inventory
        }
        
    except Exception as e:
        logger.error(f"Failed to get inventory: {e}")
        raise HTTPException(status_code=500, detail="Failed to get inventory")