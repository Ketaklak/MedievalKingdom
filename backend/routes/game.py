from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict
from datetime import datetime, timedelta
import logging

from routes.auth import get_current_user
from database.mongodb import db
from game.buildings import BuildingSystem
from game.empire_bonuses import EmpireBonuses
from game.combat import CombatSystem
from models.user import PlayerModification

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/game", tags=["game"])

# Player Resources and Buildings
@router.get("/player/resources")
async def get_player_resources(current_user: dict = Depends(get_current_user)):
    """Get player's current resources"""
    try:
        player = current_user["player"]
        return {
            "resources": player["resources"],
            "empire_bonuses": EmpireBonuses.get_empire_bonuses(player["empire"])
        }
    except Exception as e:
        logger.error(f"Failed to get player resources: {e}")
        raise HTTPException(status_code=500, detail="Failed to get resources")

@router.get("/player/buildings")
async def get_player_buildings(current_user: dict = Depends(get_current_user)):
    """Get player's buildings"""
    try:
        player = current_user["player"]
        return {
            "buildings": player["buildings"],
            "resource_generation": BuildingSystem.calculate_resource_generation(
                player["buildings"], player["empire"]
            )
        }
    except Exception as e:
        logger.error(f"Failed to get player buildings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get buildings")

@router.post("/buildings/upgrade")
async def upgrade_building(
    building_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Start building upgrade"""
    try:
        player = current_user["player"]
        building_id = building_data.get("buildingId")
        
        # Find the building
        building = None
        for b in player["buildings"]:
            if b["id"] == building_id:
                building = b
                break
        
        if not building:
            raise HTTPException(status_code=404, detail="Building not found")
        
        if building["constructing"]:
            raise HTTPException(status_code=400, detail="Building is already being upgraded")
        
        target_level = building["level"] + 1
        building_type = building["type"]
        
        # Check if can afford
        cost = BuildingSystem.get_building_cost(building_type, target_level)
        if not BuildingSystem.can_afford_building(player["resources"], building_type, target_level):
            raise HTTPException(status_code=400, detail="Insufficient resources")
        
        # Deduct resources
        new_resources = BuildingSystem.deduct_building_cost(player["resources"], building_type, target_level)
        
        # Create construction queue item
        # Use userId field from player data, fallback to id
        player_id = player.get("userId") or player.get("id") or player.get("_id")
        if player_id:
            player_id = str(player_id)  # Ensure it's a string
        
        queue_item = BuildingSystem.create_construction_queue_item(
            player_id, building_id, building_type, target_level, player["empire"]
        )
        
        # Update database
        await db.add_construction_queue_item(queue_item)
        await db.update_player(player["username"], {
            "resources": new_resources,
            "buildings": [
                {**b, "constructing": True} if b["id"] == building_id else b
                for b in player["buildings"]
            ]
        })
        
        return {
            "success": True,
            "queue_item": {
                "id": queue_item["id"],
                "buildingType": queue_item["buildingType"],
                "targetLevel": queue_item["targetLevel"],
                "startTime": queue_item["startTime"].isoformat(),
                "completionTime": queue_item["completionTime"].isoformat(),
                "completed": queue_item["completed"]
            },
            "new_resources": new_resources
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upgrade building: {e}")
        raise HTTPException(status_code=500, detail="Failed to upgrade building")

@router.get("/construction/queue")
async def get_construction_queue(current_user: dict = Depends(get_current_user)):
    """Get player's construction queue"""
    try:
        player = current_user["player"]
        # Use userId field from player data
        player_id = player.get("userId") or player.get("id") or player.get("_id")
        if not player_id:
            return {"queue": []}
        
        queue = await db.get_construction_queue(str(player_id))
        return {"queue": queue}
    except Exception as e:
        logger.error(f"Failed to get construction queue: {e}")
        # Return empty queue instead of throwing error to prevent frontend crashes
        return {"queue": []}

# Army and Combat
@router.get("/player/army")
async def get_player_army(current_user: dict = Depends(get_current_user)):
    """Get player's army information"""
    try:
        player = current_user["player"]
        return {
            "army": player["army"],
            "total_army_size": sum(player["army"].values())
        }
    except Exception as e:
        logger.error(f"Failed to get player army: {e}")
        raise HTTPException(status_code=500, detail="Failed to get army")

@router.post("/army/recruit")
async def recruit_soldiers(
    recruit_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Recruit new soldiers"""
    try:
        player = current_user["player"]
        unit_type = recruit_data.get("unitType", "soldiers")
        quantity = recruit_data.get("quantity", 1)
        
        # Calculate cost
        unit_costs = {
            "soldiers": {"gold": 50, "food": 30},
            "archers": {"gold": 75, "wood": 25, "food": 20},
            "cavalry": {"gold": 150, "food": 50, "wood": 30}
        }
        
        if unit_type not in unit_costs:
            raise HTTPException(status_code=400, detail="Invalid unit type")
        
        total_cost = {resource: amount * quantity for resource, amount in unit_costs[unit_type].items()}
        
        # Check if can afford
        for resource, cost in total_cost.items():
            if player["resources"].get(resource, 0) < cost:
                raise HTTPException(status_code=400, detail=f"Insufficient {resource}")
        
        # Deduct resources and add units
        new_resources = player["resources"].copy()
        for resource, cost in total_cost.items():
            new_resources[resource] -= cost
        
        new_army = player["army"].copy()
        new_army[unit_type] = new_army.get(unit_type, 0) + quantity
        
        # Update database
        await db.update_player(player["username"], {
            "resources": new_resources,
            "army": new_army
        })
        
        return {
            "success": True,
            "new_resources": new_resources,
            "new_army": new_army
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to recruit soldiers: {e}")
        raise HTTPException(status_code=500, detail="Failed to recruit soldiers")

@router.post("/army/train")
async def train_army(
    training_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Train army to increase combat effectiveness"""
    try:
        player = current_user["player"]
        training_type = training_data.get("type", "basic")  # basic, advanced, elite
        
        # Training costs
        training_costs = {
            "basic": {"gold": 100, "food": 50},
            "advanced": {"gold": 250, "food": 150, "wood": 100},
            "elite": {"gold": 500, "food": 300, "stone": 200}
        }
        
        if training_type not in training_costs:
            raise HTTPException(status_code=400, detail="Invalid training type")
        
        cost = training_costs[training_type]
        
        # Check if player can afford
        for resource, amount in cost.items():
            if player["resources"].get(resource, 0) < amount:
                raise HTTPException(status_code=400, detail=f"Insufficient {resource}")
        
        # Check if player has army to train
        army_size = sum(player["army"].values())
        if army_size == 0:
            raise HTTPException(status_code=400, detail="No army to train")
        
        # Deduct resources
        new_resources = player["resources"].copy()
        for resource, amount in cost.items():
            new_resources[resource] -= amount
        
        # Add training experience/level to player (stored in a new field)
        current_training = player.get("armyTraining", {"level": 1, "experience": 0})
        
        # Add experience based on training type
        exp_gain = {"basic": 10, "advanced": 25, "elite": 50}[training_type]
        current_training["experience"] += exp_gain
        
        # Level up if enough experience
        exp_needed = current_training["level"] * 100
        while current_training["experience"] >= exp_needed:
            current_training["experience"] -= exp_needed
            current_training["level"] += 1
            exp_needed = current_training["level"] * 100
        
        # Update database
        await db.update_player(player["username"], {
            "resources": new_resources,
            "armyTraining": current_training
        })
        
        return {
            "success": True,
            "message": f"Army trained with {training_type} training",
            "new_resources": new_resources,
            "army_training": current_training,
            "experience_gained": exp_gain
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to train army: {e}")
        raise HTTPException(status_code=500, detail="Failed to train army")
async def launch_raid(
    raid_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Launch a raid against another player"""
    try:
        attacker = current_user["player"]
        target_username = raid_data.get("targetUsername")
        
        if not target_username:
            raise HTTPException(status_code=400, detail="Target username is required")
        
        # Get target player
        defender = await db.get_player_by_username(target_username)
        if not defender:
            raise HTTPException(status_code=404, detail="Target player not found")
        
        # Check if attacker has army
        attacker_army_size = sum(attacker["army"].values()) if attacker.get("army") else 0
        if attacker_army_size == 0:
            raise HTTPException(status_code=400, detail="No army available for raid")
        
        # Check if not attacking self
        if attacker["username"] == target_username:
            raise HTTPException(status_code=400, detail="Cannot raid yourself")
        
        # Simple raid calculation
        defender_army_size = sum(defender["army"].values()) if defender.get("army") else 0
        
        # Calculate success chance (attacker advantage)
        success_chance = min(0.8, max(0.2, attacker_army_size / (attacker_army_size + defender_army_size + 1)))
        success = __import__('random').random() < success_chance
        
        # Calculate casualties
        attacker_losses = max(1, int(attacker_army_size * 0.1))
        defender_losses = max(1, int(defender_army_size * 0.15)) if success else max(1, int(defender_army_size * 0.05))
        
        # Calculate stolen resources
        stolen_resources = {}
        if success:
            for resource in ["gold", "wood", "stone", "food"]:
                defender_amount = defender["resources"].get(resource, 0)
                steal_amount = int(defender_amount * __import__('random').uniform(0.05, 0.15))
                if steal_amount > 0:
                    stolen_resources[resource] = steal_amount
        
        # Update attacker
        new_attacker_resources = attacker["resources"].copy()
        for resource, amount in stolen_resources.items():
            new_attacker_resources[resource] += amount
        
        new_attacker_army = attacker["army"].copy()
        new_attacker_army["soldiers"] = max(0, new_attacker_army.get("soldiers", 0) - attacker_losses)
        
        # Update defender  
        new_defender_resources = defender["resources"].copy()
        for resource, amount in stolen_resources.items():
            new_defender_resources[resource] = max(0, new_defender_resources[resource] - amount)
        
        new_defender_army = defender["army"].copy()
        new_defender_army["soldiers"] = max(0, new_defender_army.get("soldiers", 0) - defender_losses)
        
        # Update database
        await db.update_player(attacker["username"], {
            "resources": new_attacker_resources,
            "army": new_attacker_army
        })
        await db.update_player(defender["username"], {
            "resources": new_defender_resources,
            "army": new_defender_army
        })
        
        # Create battle report
        battle_report = f"{'Successful' if success else 'Failed'} raid on {target_username}. "
        if success and stolen_resources:
            resource_list = [f"{amount} {resource}" for resource, amount in stolen_resources.items()]
            battle_report += f"Stolen: {', '.join(resource_list)}. "
        battle_report += f"Casualties - Attacker: {attacker_losses}, Defender: {defender_losses}"
        
        return {
            "success": True,
            "raid_result": {
                "success": success,
                "stolenResources": stolen_resources,
                "attackerLosses": attacker_losses,
                "defenderLosses": defender_losses,
                "battleReport": battle_report
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to launch raid: {e}")
        raise HTTPException(status_code=500, detail="Failed to launch raid")

@router.get("/combat/history")
async def get_combat_history(current_user: dict = Depends(get_current_user)):
    """Get player's combat history"""
    try:
        player = current_user["player"]
        history = await db.get_raid_history(player["username"])
        return {"history": history}
    except Exception as e:
        logger.error(f"Failed to get combat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get combat history")

# Leaderboards and Rankings
@router.get("/leaderboard")
async def get_leaderboard(limit: int = 50):
    """Get global leaderboard"""
    try:
        leaderboard = await db.get_leaderboard(limit)
        return {"leaderboard": leaderboard}
    except Exception as e:
        logger.error(f"Failed to get leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get leaderboard")

@router.get("/players/nearby")
async def get_nearby_players(current_user: dict = Depends(get_current_user)):
    """Get nearby players for raids/diplomacy"""
    try:
        player = current_user["player"]
        nearby = await db.get_nearby_players(player["username"])
        return {"players": nearby}
    except Exception as e:
        logger.error(f"Failed to get nearby players: {e}")
        raise HTTPException(status_code=500, detail="Failed to get nearby players")

# Player Profile
@router.get("/player/profile")
async def get_player_profile(current_user: dict = Depends(get_current_user)):
    """Get player's full profile"""
    try:
        player = current_user["player"]
        
        # Calculate additional stats
        total_army = sum(player["army"].values())
        building_power = BuildingSystem.calculate_power_from_buildings(player["buildings"])
        total_resources = sum(player["resources"].values())
        
        return {
            "profile": player,
            "stats": {
                "totalArmy": total_army,
                "buildingPower": building_power,
                "totalResources": total_resources,
                "totalPower": player["power"]
            }
        }
    except Exception as e:
        logger.error(f"Failed to get player profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get player profile")

@router.put("/player/profile")
async def update_player_profile(
    profile_data: PlayerModification,
    current_user: dict = Depends(get_current_user)
):
    """Update player profile"""
    try:
        player = current_user["player"]
        update_data = {}
        
        if profile_data.kingdomName:
            update_data["kingdomName"] = profile_data.kingdomName
        if profile_data.bio is not None:
            update_data["bio"] = profile_data.bio
        if profile_data.location is not None:
            update_data["location"] = profile_data.location
        if profile_data.motto is not None:
            update_data["motto"] = profile_data.motto
        
        # Empire change requires special items (race change scroll)
        if profile_data.empire and profile_data.empire != player.get("empire"):
            # Check if player has race change scroll in inventory
            player_inventory = player.get("inventory", {})
            race_change_scrolls = player_inventory.get("raceChangeScroll", 0)
            
            if race_change_scrolls <= 0:
                raise HTTPException(
                    status_code=400, 
                    detail="Race change requires a Race Change Scroll from the shop"
                )
            
            # Consume the scroll
            new_inventory = player_inventory.copy()
            new_inventory["raceChangeScroll"] = race_change_scrolls - 1
            update_data["inventory"] = new_inventory
            update_data["empire"] = profile_data.empire
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid updates provided")
        
        # Update database
        await db.update_player(player["username"], update_data)
        
        return {"success": True, "message": "Profile updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")

# Shop System
@router.get("/shop/items")
async def get_shop_items():
    """Get available shop items"""
    shop_items = [
        {
            "id": "raceChangeScroll",
            "name": "Race Change Scroll",
            "description": "Allows you to change your empire/race once",
            "price": {"gold": 5000},
            "category": "special",
            "icon": "scroll"
        },
        {
            "id": "resourcePack",
            "name": "Resource Pack",
            "description": "Contains 1000 of each resource",
            "price": {"gold": 2000},
            "category": "resources",
            "icon": "chest"
        },
        {
            "id": "armyBoost",
            "name": "Army Recruitment Boost",
            "description": "Instantly recruit 100 soldiers",
            "price": {"gold": 1500},
            "category": "military",
            "icon": "sword"
        },
        {
            "id": "buildingBoost",
            "name": "Construction Speed Boost",
            "description": "Complete current construction instantly",
            "price": {"gold": 1000},
            "category": "construction",
            "icon": "hammer"
        }
    ]
    
    return {"items": shop_items}

@router.post("/shop/buy/{item_id}")
async def buy_shop_item(
    item_id: str,
    purchase_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Buy an item from the shop"""
    try:
        player = current_user["player"]
        quantity = purchase_data.get("quantity", 1)
        
        # Get shop items
        shop_response = await get_shop_items()
        shop_items = {item["id"]: item for item in shop_response["items"]}
        
        if item_id not in shop_items:
            raise HTTPException(status_code=404, detail="Item not found")
        
        item = shop_items[item_id]
        total_cost = {}
        
        # Calculate total cost
        for resource, cost in item["price"].items():
            total_cost[resource] = cost * quantity
        
        # Check if player can afford
        for resource, cost in total_cost.items():
            if player["resources"].get(resource, 0) < cost:
                raise HTTPException(status_code=400, detail=f"Insufficient {resource}")
        
        # Deduct cost
        new_resources = player["resources"].copy()
        for resource, cost in total_cost.items():
            new_resources[resource] -= cost
        
        # Add item to inventory
        inventory = player.get("inventory", {})
        inventory[item_id] = inventory.get(item_id, 0) + quantity
        
        # Apply item effects immediately for some items
        if item_id == "resourcePack":
            new_resources["gold"] += 1000 * quantity
            new_resources["wood"] += 1000 * quantity
            new_resources["stone"] += 1000 * quantity
            new_resources["food"] += 1000 * quantity
            # Don't add to inventory for consumables
            inventory[item_id] = inventory.get(item_id, 0)
        elif item_id == "armyBoost":
            new_army = player["army"].copy()
            new_army["soldiers"] = new_army.get("soldiers", 0) + 100 * quantity
            await db.update_player(player["username"], {"army": new_army})
            inventory[item_id] = inventory.get(item_id, 0)
        
        # Update database
        await db.update_player(player["username"], {
            "resources": new_resources,
            "inventory": inventory
        })
        
        return {
            "success": True,
            "message": f"Purchased {quantity}x {item['name']}",
            "new_resources": new_resources,
            "inventory": inventory
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to buy shop item: {e}")
        raise HTTPException(status_code=500, detail="Failed to buy shop item")