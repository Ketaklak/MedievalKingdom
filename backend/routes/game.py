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
        queue_item = BuildingSystem.create_construction_queue_item(
            player["id"], building_id, building_type, target_level, player["empire"]
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
            "queue_item": queue_item,
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

@router.post("/combat/raid")
async def launch_raid(
    raid_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Launch a raid against another player"""
    try:
        attacker = current_user["player"]
        target_username = raid_data.get("targetUsername")
        
        # Get target player
        defender = await db.get_player_by_username(target_username)
        if not defender:
            raise HTTPException(status_code=404, detail="Target player not found")
        
        # Prepare combat data
        attacker_data = {
            "userId": attacker["userId"],
            "username": attacker["username"],
            "empire": attacker["empire"],
            "army": sum(attacker["army"].values()),
            "buildings": attacker["buildings"],
            "resources": attacker["resources"]
        }
        
        defender_data = {
            "userId": defender["userId"],
            "username": defender["username"],
            "empire": defender["empire"],
            "army": sum(defender["army"].values()),
            "buildings": defender["buildings"],
            "resources": defender["resources"]
        }
        
        # Check if raid is allowed
        can_raid, reason = CombatSystem.can_raid_target(attacker_data, defender_data)
        if not can_raid:
            raise HTTPException(status_code=400, detail=reason)
        
        # Calculate raid result
        raid_result = CombatSystem.calculate_raid_result(attacker_data, defender_data)
        
        # Apply results to both players
        new_attacker_data, new_defender_data = CombatSystem.apply_raid_results(
            attacker_data, defender_data, raid_result
        )
        
        # Update database
        await db.add_raid_result(raid_result)
        await db.update_player(attacker["username"], {
            "resources": new_attacker_data["resources"],
            "army": {"soldiers": new_attacker_data["army"], "archers": 0, "cavalry": 0}
        })
        await db.update_player(defender["username"], {
            "resources": new_defender_data["resources"],
            "army": {"soldiers": new_defender_data["army"], "archers": 0, "cavalry": 0},
            "lastRaidTime": datetime.utcnow()
        })
        
        return {
            "success": True,
            "raid_result": raid_result
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
        if profile_data.empire:
            update_data["empire"] = profile_data.empire
        
        # Update database
        await db.update_player(player["username"], update_data)
        
        return {"success": True, "message": "Profile updated successfully"}
        
    except Exception as e:
        logger.error(f"Failed to update profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")