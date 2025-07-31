from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
import logging

from ..routes.auth import get_current_user
from ..database.mongodb import db
from ..models.user import PlayerModification, AdminAction

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])

def require_admin(current_user: dict = Depends(get_current_user)):
    """Dependency to require admin access"""
    if not current_user.get("isAdmin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@router.get("/stats", response_model=dict)
async def get_admin_stats(current_user: dict = Depends(require_admin)):
    """Get admin dashboard statistics"""
    try:
        stats = await db.get_game_stats()
        return {"stats": stats}
    except Exception as e:
        logger.error(f"Failed to get admin stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

@router.get("/players", response_model=dict)
async def get_all_players(
    current_user: dict = Depends(require_admin),
    limit: int = 100
):
    """Get all players for admin management"""
    try:
        players = await db.get_leaderboard(limit)
        
        # Add additional admin info
        for player in players:
            # Add last login, status, etc.
            user_data = await db.get_user_by_username(player["username"])
            if user_data:
                player["lastLogin"] = user_data.get("lastActive")
                player["joinDate"] = user_data.get("joinDate")
                player["email"] = user_data.get("email")
        
        return {"players": players}
        
    except Exception as e:
        logger.error(f"Failed to get all players: {e}")
        raise HTTPException(status_code=500, detail="Failed to get players")

@router.put("/player/{username}", response_model=dict)
async def modify_player(
    username: str,
    modifications: PlayerModification,
    current_user: dict = Depends(require_admin)
):
    """Modify a player's data (admin only)"""
    try:
        # Get existing player
        player = await db.get_player_by_username(username)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Prepare update data
        update_data = {}
        if modifications.kingdomName:
            update_data["kingdomName"] = modifications.kingdomName
        if modifications.empire:
            update_data["empire"] = modifications.empire
        if modifications.bio is not None:
            update_data["bio"] = modifications.bio
        if modifications.location is not None:
            update_data["location"] = modifications.location
        if modifications.motto is not None:
            update_data["motto"] = modifications.motto
        if modifications.resources:
            update_data["resources"] = modifications.resources.dict()
        if modifications.army:
            update_data["army"] = modifications.army.dict()
        
        # Update player
        await db.update_player(username, update_data)
        
        # Log admin action
        admin_action = {
            "adminId": current_user["user_id"],
            "adminUsername": current_user["username"],
            "action": "modify_player",
            "targetId": player["userId"],
            "targetUsername": username,
            "details": f"Modified player data: {list(update_data.keys())}"
        }
        
        return {
            "success": True,
            "message": f"Player {username} modified successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to modify player: {e}")
        raise HTTPException(status_code=500, detail="Failed to modify player")

@router.delete("/player/{username}")
async def delete_player(
    username: str,
    current_user: dict = Depends(require_admin)
):
    """Delete a player account (admin only)"""
    try:
        # Get player data
        player = await db.get_player_by_username(username)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Get user data
        user = await db.get_user_by_id(player["userId"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Delete player and user records
        from bson import ObjectId
        await db.db.players.delete_one({"username": username})
        await db.db.users.delete_one({"_id": ObjectId(user["id"])})
        
        # Clean up related data
        await db.db.construction_queue.delete_many({"playerId": player["id"]})
        await db.db.raids.delete_many({
            "$or": [
                {"attackerUsername": username},
                {"defenderUsername": username}
            ]
        })
        await db.db.chat_messages.delete_many({"username": username})
        await db.db.private_messages.delete_many({
            "$or": [
                {"sender": username},
                {"receiver": username}
            ]
        })
        
        return {
            "success": True,
            "message": f"Player {username} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete player: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete player")

@router.post("/ban-player/{username}")
async def ban_player(
    username: str,
    ban_data: dict,
    current_user: dict = Depends(require_admin)
):
    """Ban a player (admin only)"""
    try:
        # Get user
        user = await db.get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        reason = ban_data.get("reason", "No reason provided")
        duration = ban_data.get("duration", 0)  # 0 = permanent
        
        # Update user with ban status
        ban_data = {
            "banned": True,
            "banReason": reason,
            "banDuration": duration,
            "bannedAt": datetime.utcnow(),
            "bannedBy": current_user["username"]
        }
        
        from bson import ObjectId
        await db.db.users.update_one(
            {"_id": ObjectId(user["id"])},
            {"$set": ban_data}
        )
        
        return {
            "success": True,
            "message": f"Player {username} banned successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to ban player: {e}")
        raise HTTPException(status_code=500, detail="Failed to ban player")

@router.post("/unban-player/{username}")
async def unban_player(
    username: str,
    current_user: dict = Depends(require_admin)
):
    """Unban a player (admin only)"""
    try:
        # Get user
        user = await db.get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Remove ban status
        from bson import ObjectId
        await db.db.users.update_one(
            {"_id": ObjectId(user["id"])},
            {"$unset": {
                "banned": "",
                "banReason": "",
                "banDuration": "",
                "bannedAt": "",
                "bannedBy": ""
            }}
        )
        
        return {
            "success": True,
            "message": f"Player {username} unbanned successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to unban player: {e}")
        raise HTTPException(status_code=500, detail="Failed to unban player")

@router.get("/chat-messages", response_model=dict)
async def get_all_chat_messages(
    current_user: dict = Depends(require_admin),
    limit: int = 200
):
    """Get all chat messages for moderation"""
    try:
        messages = await db.get_recent_chat_messages(limit)
        return {"messages": messages}
    except Exception as e:
        logger.error(f"Failed to get chat messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat messages")

@router.post("/reset-game-data")
async def reset_game_data(
    reset_data: dict,
    current_user: dict = Depends(require_admin)
):
    """Reset game data (admin only)"""
    try:
        reset_type = reset_data.get("type", "all")
        
        if reset_type == "all":
            # Reset all player data but keep users
            await db.db.players.update_many({}, {
                "$set": {
                    "resources": {"gold": 1500, "wood": 800, "stone": 600, "food": 400},
                    "power": 1000,
                    "army": {"soldiers": 25, "archers": 0, "cavalry": 0}
                }
            })
            await db.db.construction_queue.delete_many({})
            await db.db.raids.delete_many({})
            
        elif reset_type == "chat":
            await db.db.chat_messages.delete_many({})
            await db.db.private_messages.delete_many({})
            
        elif reset_type == "combat":
            await db.db.raids.delete_many({})
            await db.db.players.update_many({}, {
                "$set": {"army": {"soldiers": 25, "archers": 0, "cavalry": 0}}
            })
        
        return {
            "success": True,
            "message": f"Game data reset: {reset_type}"
        }
        
    except Exception as e:
        logger.error(f"Failed to reset game data: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset game data")

@router.get("/system-info", response_model=dict)
async def get_system_info(current_user: dict = Depends(require_admin)):
    """Get system information"""
    try:
        import os
        import psutil
        from datetime import datetime
        
        # Get system stats
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get database stats
        db_stats = await db.get_game_stats()
        
        return {
            "system": {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "memory_total": memory.total,
                "memory_available": memory.available,
                "disk_usage": disk.percent,
                "disk_total": disk.total,
                "disk_free": disk.free
            },
            "database": db_stats,
            "server_time": datetime.utcnow(),
            "uptime": "N/A"  # Could track actual uptime
        }
        
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system info")