from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
import logging

from models.user import UserCreate, UserLogin, UserResponse
from auth.jwt_handler import create_access_token, verify_token
from auth.password import hash_password, verify_password
from database.mongodb import db
from game.empire_bonuses import EmpireBonuses
from game.buildings import BuildingSystem

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

@router.post("/register", response_model=dict)
async def register_user(user_data: UserCreate):
    """Register a new user and create their kingdom"""
    try:
        # Check if username already exists
        existing_user = await db.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Create user account
        hashed_password = hash_password(user_data.password)
        user_doc = {
            "username": user_data.username,
            "email": user_data.email,
            "passwordHash": hashed_password,
            "isAdmin": user_data.username == "admin",
            "joinDate": datetime.utcnow(),
            "lastActive": datetime.utcnow()
        }
        
        user_id = await db.create_user(user_doc)
        
        # Create player profile
        starting_resources = EmpireBonuses.get_starting_resources(user_data.empire)
        default_buildings = BuildingSystem.get_default_buildings()
        
        player_doc = {
            "userId": user_id,
            "username": user_data.username,
            "kingdomName": user_data.kingdomName,
            "empire": user_data.empire,
            "bio": "",
            "location": "",
            "motto": "",
            "resources": starting_resources,
            "buildings": default_buildings,
            "army": {"soldiers": 25, "archers": 0, "cavalry": 0},
            "power": BuildingSystem.calculate_power_from_buildings(default_buildings) + 250,  # Base army power
            "coordinates": {"x": 0, "y": 0},
            "createdAt": datetime.utcnow(),
            "lastActive": datetime.utcnow()
        }
        
        await db.create_player(player_doc)
        
        # Create access token
        token_data = {"sub": user_data.username, "user_id": user_id}
        access_token = create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "username": user_data.username,
                "kingdomName": user_data.kingdomName,
                "empire": user_data.empire,
                "isAdmin": user_doc["isAdmin"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=dict)
async def login_user(user_data: UserLogin):
    """Authenticate user and return access token"""
    try:
        # Get user by username
        user = await db.get_user_by_username(user_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Verify password
        if not verify_password(user_data.password, user["passwordHash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Update last active
        await db.update_user_last_active(user["id"])
        
        # Get player profile
        player = await db.get_player_by_user_id(user["id"])
        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player profile not found"
            )
        
        # Create access token
        token_data = {"sub": user["username"], "user_id": user["id"]}
        access_token = create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "username": user["username"],
                "kingdomName": player["kingdomName"],
                "empire": player["empire"],
                "isAdmin": user.get("isAdmin", False)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        username = payload["username"]
        user_id = payload["user_id"]
        
        # Get user from database
        user = await db.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Get player profile
        player = await db.get_player_by_user_id(user_id)
        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player profile not found"
            )
        
        return {
            "user_id": user_id,
            "username": username,
            "isAdmin": user.get("isAdmin", False),
            "player": player
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    try:
        return {
            "user": {
                "username": current_user["username"],
                "kingdomName": current_user["player"]["kingdomName"],
                "empire": current_user["player"]["empire"],
                "isAdmin": current_user["isAdmin"]
            },
            "player": current_user["player"]
        }
    except Exception as e:
        logger.error(f"Failed to get user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )