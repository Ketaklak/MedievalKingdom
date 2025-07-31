from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, List
from datetime import datetime
import uuid

# User Authentication Models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=6)
    email: Optional[EmailStr] = None
    kingdomName: str = Field(..., min_length=3, max_length=50)
    empire: str = Field(..., regex=r'^(norman|viking|saxon|celtic|frankish)$')

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[str]
    kingdomName: str
    empire: str
    bio: Optional[str] = ""
    location: Optional[str] = ""
    motto: Optional[str] = ""
    power: int = 0
    joinDate: datetime
    lastActive: datetime
    isAdmin: bool = False

# Player Game Data Models
class Resources(BaseModel):
    gold: int = 1500
    wood: int = 800
    stone: int = 600
    food: int = 400

class Building(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    level: int = 1
    constructing: bool = False
    description: str
    production: Dict[str, int] = {}

class Army(BaseModel):
    soldiers: int = 25
    archers: int = 0
    cavalry: int = 0

class ConstructionQueueItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    buildingId: str
    buildingType: str
    targetLevel: int
    startTime: datetime
    completionTime: datetime
    completed: bool = False

class PlayerProfile(BaseModel):
    userId: str
    username: str
    kingdomName: str
    empire: str
    bio: Optional[str] = ""
    location: Optional[str] = ""
    motto: Optional[str] = ""
    resources: Resources = Field(default_factory=Resources)
    buildings: List[Building] = []
    army: Army = Field(default_factory=Army)
    power: int = 0
    coordinates: Dict[str, int] = {"x": 0, "y": 0}
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    lastActive: datetime = Field(default_factory=datetime.utcnow)

# Chat Models
class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    content: str = Field(..., max_length=500)
    empire: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    messageType: str = "global"  # global, private, system

class PrivateMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str
    receiver: str
    content: str = Field(..., max_length=500)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    read: bool = False

# Combat Models
class RaidResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    attackerId: str
    defenderId: str
    attackerUsername: str
    defenderUsername: str
    armySize: int
    success: bool
    stolenResources: Dict[str, int]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    battleReport: str

# Trading Models
class TradeOffer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    creatorId: str
    creatorUsername: str
    offering: Dict[str, int]
    requesting: Dict[str, int]
    duration: int = 3600  # seconds
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    expiresAt: datetime
    active: bool = True

class TradeAccept(BaseModel):
    offerId: str
    acceptorId: str

# Alliance Models
class Alliance(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field(default="", max_length=500)
    leaderId: str
    leaderUsername: str
    members: List[str] = []
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    maxMembers: int = 20

class AllianceInvite(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    allianceId: str
    fromUserId: str
    toUserId: str
    toUsername: str
    status: str = "pending"  # pending, accepted, rejected
    createdAt: datetime = Field(default_factory=datetime.utcnow)

# Admin Models
class AdminAction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    adminId: str
    adminUsername: str
    action: str  # ban_player, delete_message, reset_data, etc.
    targetId: Optional[str] = None
    targetUsername: Optional[str] = None
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PlayerModification(BaseModel):
    username: str
    kingdomName: Optional[str] = None
    empire: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    motto: Optional[str] = None
    resources: Optional[Resources] = None
    army: Optional[Army] = None

# Response Models
class LeaderboardEntry(BaseModel):
    username: str
    kingdomName: str
    empire: str
    power: int
    rank: int

class OnlineUser(BaseModel):
    username: str
    kingdomName: str
    empire: str
    power: int
    lastSeen: datetime

class GameStats(BaseModel):
    totalPlayers: int
    activePlayers: int
    totalMessages: int
    totalPower: int
    topEmpire: str