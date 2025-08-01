from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from datetime import datetime, timedelta
import logging

from routes.auth import get_current_user
from database.mongodb import db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/diplomacy", tags=["diplomacy"])

# Trade System
@router.post("/trade/create")
async def create_trade_offer(
    trade_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create a trade offer"""
    try:
        player = current_user["player"]
        
        offering = trade_data.get("offering", {})
        requesting = trade_data.get("requesting", {})
        duration = trade_data.get("duration", 3600)  # 1 hour default
        
        if not offering or not requesting:
            raise HTTPException(status_code=400, detail="Must specify both offering and requesting resources")
        
        # Check if player has enough resources to offer
        for resource, amount in offering.items():
            if player["resources"].get(resource, 0) < amount:
                raise HTTPException(status_code=400, detail=f"Insufficient {resource}")
        
        # Create trade offer
        trade_offer = {
            "id": str(__import__('uuid').uuid4()),
            "creatorId": player["userId"],
            "creatorUsername": player["username"],
            "offering": offering,
            "requesting": requesting,
            "duration": duration,
            "createdAt": datetime.utcnow(),
            "expiresAt": datetime.utcnow() + timedelta(seconds=duration),
            "active": True,
            "acceptorId": None,
            "acceptorUsername": None
        }
        
        # Store in database
        result = await db.db.trade_offers.insert_one(trade_offer)
        
        # Prepare serializable response
        response_trade_offer = {
            "id": trade_offer["id"],
            "creatorUsername": trade_offer["creatorUsername"],
            "offering": trade_offer["offering"],
            "requesting": trade_offer["requesting"],
            "duration": trade_offer["duration"],
            "createdAt": trade_offer["createdAt"].isoformat(),
            "expiresAt": trade_offer["expiresAt"].isoformat(),
            "active": trade_offer["active"]
        }
        
        return {
            "success": True,
            "trade_offer": response_trade_offer
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create trade offer: {e}")
        raise HTTPException(status_code=500, detail="Failed to create trade offer")

@router.get("/trade/offers")
async def get_trade_offers(current_user: dict = Depends(get_current_user)):
    """Get all active trade offers"""
    try:
        # Get active trades not created by current user
        cursor = db.db.trade_offers.find({
            "active": True,
            "expiresAt": {"$gt": datetime.utcnow()},
            "creatorUsername": {"$ne": current_user["player"]["username"]}
        }).sort("createdAt", -1).limit(20)
        
        offers = await cursor.to_list(length=20)
        
        # Convert ObjectId to string
        for offer in offers:
            offer["id"] = str(offer["_id"])
            del offer["_id"]
        
        return {"offers": offers}
        
    except Exception as e:
        logger.error(f"Failed to get trade offers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get trade offers")

@router.get("/trade/my-offers")
async def get_my_trade_offers(current_user: dict = Depends(get_current_user)):
    """Get player's own trade offers"""
    try:
        cursor = db.db.trade_offers.find({
            "creatorUsername": current_user["player"]["username"]
        }).sort("createdAt", -1).limit(10)
        
        offers = await cursor.to_list(length=10)
        
        for offer in offers:
            offer["id"] = str(offer["_id"])
            del offer["_id"]
        
        return {"offers": offers}
        
    except Exception as e:
        logger.error(f"Failed to get my trade offers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get my trade offers")

@router.post("/trade/accept/{offer_id}")
async def accept_trade_offer(
    offer_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Accept a trade offer"""
    try:
        from bson import ObjectId
        player = current_user["player"]
        
        # Get trade offer
        trade_offer = await db.db.trade_offers.find_one({
            "_id": ObjectId(offer_id),
            "active": True,
            "expiresAt": {"$gt": datetime.utcnow()}
        })
        
        if not trade_offer:
            raise HTTPException(status_code=404, detail="Trade offer not found or expired")
        
        if trade_offer["creatorUsername"] == player["username"]:
            raise HTTPException(status_code=400, detail="Cannot accept your own trade offer")
        
        # Check if acceptor has required resources
        for resource, amount in trade_offer["requesting"].items():
            if player["resources"].get(resource, 0) < amount:
                raise HTTPException(status_code=400, detail=f"Insufficient {resource}")
        
        # Get creator player
        creator = await db.get_player_by_username(trade_offer["creatorUsername"])
        if not creator:
            raise HTTPException(status_code=404, detail="Trade creator not found")
        
        # Execute trade
        # Update acceptor resources
        acceptor_resources = player["resources"].copy()
        for resource, amount in trade_offer["requesting"].items():
            acceptor_resources[resource] -= amount
        for resource, amount in trade_offer["offering"].items():
            acceptor_resources[resource] += amount
        
        # Update creator resources
        creator_resources = creator["resources"].copy()
        for resource, amount in trade_offer["offering"].items():
            creator_resources[resource] -= amount
        for resource, amount in trade_offer["requesting"].items():
            creator_resources[resource] += amount
        
        # Update database
        await db.update_player(player["username"], {"resources": acceptor_resources})
        await db.update_player(creator["username"], {"resources": creator_resources})
        
        # Mark trade as completed
        await db.db.trade_offers.update_one(
            {"_id": ObjectId(offer_id)},
            {"$set": {
                "active": False,
                "acceptorId": player["userId"],
                "acceptorUsername": player["username"],
                "completedAt": datetime.utcnow()
            }}
        )
        
        return {
            "success": True,
            "message": "Trade completed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to accept trade offer: {e}")
        raise HTTPException(status_code=500, detail="Failed to accept trade offer")

# Alliance System
@router.post("/alliance/create")
async def create_alliance(
    alliance_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create a new alliance"""
    try:
        player = current_user["player"]
        
        name = alliance_data.get("name", "").strip()
        description = alliance_data.get("description", "").strip()
        
        if not name or len(name) < 3:
            raise HTTPException(status_code=400, detail="Alliance name must be at least 3 characters")
        
        # Check if alliance name already exists
        existing = await db.db.alliances.find_one({"name": name})
        if existing:
            raise HTTPException(status_code=400, detail="Alliance name already exists")
        
        # Check if player is already in an alliance
        player_alliance = await db.db.alliances.find_one({"members": player["username"]})
        if player_alliance:
            raise HTTPException(status_code=400, detail="Already in an alliance")
        
        # Create alliance
        alliance = {
            "id": str(__import__('uuid').uuid4()),
            "name": name,
            "description": description,
            "leaderId": player["userId"],
            "leaderUsername": player["username"],
            "members": [player["username"]],
            "createdAt": datetime.utcnow(),
            "maxMembers": 20,
            "level": 1,
            "experience": 0
        }
        
        await db.db.alliances.insert_one(alliance)
        
        return {
            "success": True,
            "alliance": alliance
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create alliance: {e}")
        raise HTTPException(status_code=500, detail="Failed to create alliance")

@router.get("/alliance/list")
async def get_alliances():
    """Get list of all alliances"""
    try:
        cursor = db.db.alliances.find({}).sort("createdAt", -1).limit(50)
        alliances = await cursor.to_list(length=50)
        
        for alliance in alliances:
            alliance["id"] = str(alliance["_id"])
            del alliance["_id"]
            alliance["memberCount"] = len(alliance.get("members", []))
            alliance["hasFlag"] = alliance["memberCount"] >= 10  # Flag if 10+ members
        
        return {"alliances": alliances}
        
    except Exception as e:
        logger.error(f"Failed to get alliances: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alliances")

@router.get("/alliance/my")
async def get_my_alliance(current_user: dict = Depends(get_current_user)):
    """Get player's alliance"""
    try:
        player = current_user["player"]
        
        alliance = await db.db.alliances.find_one({"members": player["username"]})
        
        if alliance:
            alliance["id"] = str(alliance["_id"])
            del alliance["_id"]
            alliance["memberCount"] = len(alliance.get("members", []))
            alliance["hasFlag"] = alliance["memberCount"] >= 10
        
        return {"alliance": alliance}
        
    except Exception as e:
        logger.error(f"Failed to get my alliance: {e}")
        raise HTTPException(status_code=500, detail="Failed to get my alliance")

@router.post("/alliance/invite")
async def invite_to_alliance(
    invite_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Invite a player to alliance"""
    try:
        player = current_user["player"]
        target_username = invite_data.get("username", "").strip()
        
        if not target_username:
            raise HTTPException(status_code=400, detail="Username is required")
        
        # Check if player is alliance leader
        alliance = await db.db.alliances.find_one({"leaderUsername": player["username"]})
        if not alliance:
            raise HTTPException(status_code=403, detail="Only alliance leaders can invite")
        
        # Check if target player exists
        target_player = await db.get_player_by_username(target_username)
        if not target_player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Check if target is already in an alliance
        target_alliance = await db.db.alliances.find_one({"members": target_username})
        if target_alliance:
            raise HTTPException(status_code=400, detail="Player already in an alliance")
        
        # Check alliance capacity
        if len(alliance.get("members", [])) >= alliance.get("maxMembers", 20):
            raise HTTPException(status_code=400, detail="Alliance is full")
        
        # Create invitation
        invitation = {
            "id": str(__import__('uuid').uuid4()),
            "allianceId": str(alliance["_id"]),
            "allianceName": alliance["name"],
            "fromUserId": player["userId"],
            "fromUsername": player["username"],
            "toUserId": target_player["userId"],
            "toUsername": target_username,
            "status": "pending",
            "createdAt": datetime.utcnow(),
            "expiresAt": datetime.utcnow() + timedelta(days=7)
        }
        
        await db.db.alliance_invites.insert_one(invitation)
        
        return {
            "success": True,
            "message": f"Invitation sent to {target_username}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send alliance invite: {e}")
        raise HTTPException(status_code=500, detail="Failed to send alliance invite")

@router.get("/alliance/invites")
async def get_alliance_invites(current_user: dict = Depends(get_current_user)):
    """Get player's alliance invitations"""
    try:
        player = current_user["player"]
        
        cursor = db.db.alliance_invites.find({
            "toUsername": player["username"],
            "status": "pending",
            "expiresAt": {"$gt": datetime.utcnow()}
        }).sort("createdAt", -1)
        
        invites = await cursor.to_list(length=None)
        
        for invite in invites:
            invite["id"] = str(invite["_id"])
            del invite["_id"]
        
        return {"invites": invites}
        
    except Exception as e:
        logger.error(f"Failed to get alliance invites: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alliance invites")

@router.post("/alliance/accept/{invite_id}")
async def accept_alliance_invite(
    invite_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Accept alliance invitation"""
    try:
        from bson import ObjectId
        player = current_user["player"]
        
        # Get invitation
        invite = await db.db.alliance_invites.find_one({
            "_id": ObjectId(invite_id),
            "toUsername": player["username"],
            "status": "pending",
            "expiresAt": {"$gt": datetime.utcnow()}
        })
        
        if not invite:
            raise HTTPException(status_code=404, detail="Invitation not found or expired")
        
        # Check if player is already in an alliance
        existing_alliance = await db.db.alliances.find_one({"members": player["username"]})
        if existing_alliance:
            raise HTTPException(status_code=400, detail="Already in an alliance")
        
        # Get alliance
        alliance = await db.db.alliances.find_one({"_id": ObjectId(invite["allianceId"])})
        if not alliance:
            raise HTTPException(status_code=404, detail="Alliance not found")
        
        # Check capacity
        if len(alliance.get("members", [])) >= alliance.get("maxMembers", 20):
            raise HTTPException(status_code=400, detail="Alliance is full")
        
        # Add player to alliance
        await db.db.alliances.update_one(
            {"_id": ObjectId(invite["allianceId"])},
            {"$push": {"members": player["username"]}}
        )
        
        # Mark invitation as accepted
        await db.db.alliance_invites.update_one(
            {"_id": ObjectId(invite_id)},
            {"$set": {"status": "accepted", "acceptedAt": datetime.utcnow()}}
        )
        
        return {
            "success": True,
            "message": f"Joined alliance {alliance['name']}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to accept alliance invite: {e}")
        raise HTTPException(status_code=500, detail="Failed to accept alliance invite")

@router.get("/alliance/map")
async def get_alliance_map():
    """Get alliance map with flags for alliances with 10+ members"""
    try:
        # Get all alliances with their member counts
        cursor = db.db.alliances.find({})
        alliances = await cursor.to_list(length=None)
        
        alliance_map = []
        
        for alliance in alliances:
            member_count = len(alliance.get("members", []))
            
            # Only show alliances with 10+ members on the map
            if member_count >= 10:
                # Generate random coordinates for the map
                import random
                
                alliance_data = {
                    "id": str(alliance["_id"]),
                    "name": alliance["name"],
                    "memberCount": member_count,
                    "level": alliance.get("level", 1),
                    "leaderUsername": alliance["leaderUsername"],
                    "coordinates": {
                        "x": random.randint(100, 900),
                        "y": random.randint(100, 700)
                    },
                    "flag": {
                        "color": random.choice(["red", "blue", "green", "purple", "gold", "silver"]),
                        "symbol": random.choice(["crown", "sword", "shield", "dragon", "eagle", "lion"]),
                        "pattern": random.choice(["solid", "stripes", "cross", "diagonal"])
                    },
                    "influence": min(100, member_count * 3),  # Influence radius on map
                    "description": alliance.get("description", "")
                }
                
                alliance_map.append(alliance_data)
        
        return {
            "alliances": alliance_map,
            "mapSize": {"width": 1000, "height": 800},
            "totalAlliances": len(alliance_map)
        }
        
    except Exception as e:
        logger.error(f"Failed to get alliance map: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alliance map")
async def leave_alliance(current_user: dict = Depends(get_current_user)):
    """Leave current alliance"""
    try:
        player = current_user["player"]
        
        alliance = await db.db.alliances.find_one({"members": player["username"]})
        if not alliance:
            raise HTTPException(status_code=400, detail="Not in an alliance")
        
        # If leader, transfer leadership or disband
        if alliance["leaderUsername"] == player["username"]:
            remaining_members = [m for m in alliance["members"] if m != player["username"]]
            if remaining_members:
                # Transfer leadership to first remaining member
                new_leader = remaining_members[0]
                new_leader_data = await db.get_player_by_username(new_leader)
                
                await db.db.alliances.update_one(
                    {"_id": alliance["_id"]},
                    {"$set": {
                        "leaderUsername": new_leader,
                        "leaderId": new_leader_data["userId"]
                    },
                    "$pull": {"members": player["username"]}}
                )
            else:
                # Disband alliance if no members left
                await db.db.alliances.delete_one({"_id": alliance["_id"]})
        else:
            # Just remove from members
            await db.db.alliances.update_one(
                {"_id": alliance["_id"]},
                {"$pull": {"members": player["username"]}}
            )
        
        return {
            "success": True,
            "message": "Left alliance successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to leave alliance: {e}")
        raise HTTPException(status_code=500, detail="Failed to leave alliance")