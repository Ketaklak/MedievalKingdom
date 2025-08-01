from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
import logging

from routes.auth import get_current_user
from database.mongodb import db
from models.user import ChatMessage, PrivateMessage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/global", response_model=dict)
async def send_global_message(
    message_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Send a global chat message"""
    try:
        player = current_user["player"]
        content = message_data.get("content", "").strip()
        
        if not content:
            raise HTTPException(status_code=400, detail="Message content is required")
        
        if len(content) > 500:
            raise HTTPException(status_code=400, detail="Message too long")
        
        # Create message
        message = {
            "username": player["username"],
            "content": content,
            "empire": player["empire"],
            "messageType": "global"
        }
        
        message_id = await db.add_chat_message(message)
        
        # Return response with proper string serialization
        return {
            "success": True,
            "message_id": str(message_id),  # Ensure it's a string
            "content": content,
            "username": player["username"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send global message: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@router.get("/global", response_model=dict)
async def get_global_messages(limit: int = 100):
    """Get recent global chat messages"""
    try:
        messages = await db.get_recent_chat_messages(limit)
        return {"messages": messages}
    except Exception as e:
        logger.error(f"Failed to get global messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get messages")

@router.post("/private", response_model=dict)
async def send_private_message(
    message_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Send a private message"""
    try:
        player = current_user["player"]
        receiver = message_data.get("receiver", "").strip()
        content = message_data.get("content", "").strip()
        
        if not receiver:
            raise HTTPException(status_code=400, detail="Receiver is required")
        
        if not content:
            raise HTTPException(status_code=400, detail="Message content is required")
        
        if len(content) > 500:
            raise HTTPException(status_code=400, detail="Message too long")
        
        # Check if receiver exists
        target_player = await db.get_player_by_username(receiver)
        if not target_player:
            raise HTTPException(status_code=404, detail="Receiver not found")
        
        # Create private message
        message = {
            "sender": player["username"],
            "receiver": receiver,
            "content": content,
            "read": False
        }
        
        message_id = await db.add_private_message(message)
        
        return {
            "success": True,
            "message_id": message_id,
            "message": message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send private message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send private message")

@router.get("/private", response_model=dict)
async def get_private_messages(
    current_user: dict = Depends(get_current_user),
    limit: int = 100
):
    """Get private messages for current user"""
    try:
        player = current_user["player"]
        messages = await db.get_private_messages(player["username"], limit)
        return {"messages": messages}
    except Exception as e:
        logger.error(f"Failed to get private messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get private messages")

@router.get("/online-users", response_model=dict)
async def get_online_users():
    """Get list of recently active users"""
    try:
        # Get players active in last 30 minutes
        from datetime import datetime, timedelta
        recent_time = datetime.utcnow() - timedelta(minutes=30)
        
        # For now, get top 20 players by power as "online" users
        players = await db.get_leaderboard(20)
        
        online_users = []
        for player in players:
            online_users.append({
                "username": player["username"],
                "kingdomName": player["kingdomName"],
                "empire": player["empire"],
                "power": player["power"],
                "lastSeen": player.get("lastActive", datetime.utcnow())
            })
        
        return {"users": online_users}
        
    except Exception as e:
        logger.error(f"Failed to get online users: {e}")
        raise HTTPException(status_code=500, detail="Failed to get online users")

@router.delete("/message/{message_id}")
async def delete_message(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a chat message (admin only)"""
    try:
        if not current_user.get("isAdmin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        await db.delete_chat_message(message_id)
        
        return {"success": True, "message": "Message deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete message: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete message")

@router.post("/system-message", response_model=dict)
async def send_system_message(
    message_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Send a system message (admin only)"""
    try:
        if not current_user.get("isAdmin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        content = message_data.get("content", "").strip()
        
        if not content:
            raise HTTPException(status_code=400, detail="Message content is required")
        
        # Create system message
        message = {
            "username": "SYSTEM",
            "content": content,
            "empire": "system",
            "messageType": "system"
        }
        
        message_id = await db.add_chat_message(message)
        
        return {
            "success": True,
            "message_id": message_id,
            "message": message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send system message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send system message")