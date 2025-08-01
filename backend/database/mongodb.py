from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import os
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect_to_mongo(self):
        """Create database connection"""
        try:
            self.client = AsyncIOMotorClient(os.environ['MONGO_URL'])
            self.db = self.client[os.environ.get('DB_NAME', 'medieval_empires')]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("Connected to MongoDB successfully")
            
            # Create indexes
            await self.create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def close_mongo_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    async def create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Users collection indexes
            await self.db.users.create_index("username", unique=True)
            await self.db.users.create_index("email", unique=True, sparse=True)
            
            # Players collection indexes
            await self.db.players.create_index("userId", unique=True)
            await self.db.players.create_index("username", unique=True)
            await self.db.players.create_index("power", background=True)
            await self.db.players.create_index("empire", background=True)
            await self.db.players.create_index("lastActive", background=True)
            
            # Chat messages indexes
            await self.db.chat_messages.create_index("timestamp", background=True)
            await self.db.chat_messages.create_index("username", background=True)
            await self.db.private_messages.create_index([("sender", 1), ("receiver", 1)], background=True)
            await self.db.private_messages.create_index("timestamp", background=True)
            
            # Construction queue indexes
            await self.db.construction_queue.create_index("playerId", background=True)
            await self.db.construction_queue.create_index("completionTime", background=True)
            await self.db.construction_queue.create_index("completed", background=True)
            
            # Raids indexes
            await self.db.raids.create_index("attackerId", background=True)
            await self.db.raids.create_index("defenderId", background=True)
            await self.db.raids.create_index("timestamp", background=True)
            
            # Trade offers indexes
            await self.db.trade_offers.create_index("creatorId", background=True)
            await self.db.trade_offers.create_index("active", background=True)
            await self.db.trade_offers.create_index("expiresAt", background=True)
            
            # Alliances indexes
            await self.db.alliances.create_index("leaderId", background=True)
            await self.db.alliances.create_index("name", unique=True)
            await self.db.alliance_invites.create_index("toUserId", background=True)
            await self.db.alliance_invites.create_index("status", background=True)
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")

    # User Management
    async def create_user(self, user_data: dict) -> str:
        """Create a new user"""
        try:
            result = await self.db.users.insert_one(user_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise

    async def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username"""
        try:
            user = await self.db.users.find_one({"username": username})
            if user:
                user['id'] = str(user['_id'])
                # Remove the _id field to avoid serialization issues
                del user['_id']
            return user
        except Exception as e:
            logger.error(f"Failed to get user by username: {e}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        try:
            from bson import ObjectId
            user = await self.db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                user['id'] = str(user['_id'])
                # Remove the _id field to avoid serialization issues
                del user['_id']
            return user
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None

    async def update_user_last_active(self, user_id: str):
        """Update user's last active timestamp"""
        try:
            from bson import ObjectId
            await self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"lastActive": datetime.utcnow()}}
            )
        except Exception as e:
            logger.error(f"Failed to update user last active: {e}")

    # Player Management
    async def create_player(self, player_data: dict) -> str:
        """Create a new player profile"""
        try:
            result = await self.db.players.insert_one(player_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to create player: {e}")
            raise

    async def get_player_by_username(self, username: str) -> Optional[dict]:
        """Get player by username"""
        try:
            player = await self.db.players.find_one({"username": username})
            if player:
                player['id'] = str(player['_id'])
                # Remove the _id field to avoid serialization issues
                del player['_id']
            return player
        except Exception as e:
            logger.error(f"Failed to get player by username: {e}")
            return None

    async def get_player_by_user_id(self, user_id: str) -> Optional[dict]:
        """Get player by user ID"""
        try:
            player = await self.db.players.find_one({"userId": user_id})
            if player:
                player['id'] = str(player['_id'])
                # Remove the _id field to avoid serialization issues
                del player['_id']
            return player
        except Exception as e:
            logger.error(f"Failed to get player by user ID: {e}")
            return None

    async def update_player(self, username: str, update_data: dict):
        """Update player data"""
        try:
            update_data['lastActive'] = datetime.utcnow()
            await self.db.players.update_one(
                {"username": username},
                {"$set": update_data}
            )
        except Exception as e:
            logger.error(f"Failed to update player: {e}")
            raise

    async def get_leaderboard(self, limit: int = 50) -> List[dict]:
        """Get top players by power"""
        try:
            cursor = self.db.players.find({}).sort("power", -1).limit(limit)
            players = await cursor.to_list(length=limit)
            for i, player in enumerate(players):
                player['id'] = str(player['_id'])
                # Remove the _id field to avoid serialization issues
                del player['_id']
                player['rank'] = i + 1
            return players
        except Exception as e:
            logger.error(f"Failed to get leaderboard: {e}")
            return []

    async def get_players_by_empire(self, empire: str, limit: int = 20) -> List[dict]:
        """Get players by empire"""
        try:
            cursor = self.db.players.find({"empire": empire}).sort("power", -1).limit(limit)
            players = await cursor.to_list(length=limit)
            for player in players:
                player['id'] = str(player['_id'])
            return players
        except Exception as e:
            logger.error(f"Failed to get players by empire: {e}")
            return []

    async def get_nearby_players(self, username: str, limit: int = 10) -> List[dict]:
        """Get nearby players for raids/diplomacy"""
        try:
            # For now, just get random players excluding the current user
            cursor = self.db.players.find({"username": {"$ne": username}}).limit(limit * 2)
            players = await cursor.to_list(length=limit * 2)
            
            # Randomize and return subset
            import random
            random.shuffle(players)
            players = players[:limit]
            
            for player in players:
                player['id'] = str(player['_id'])
                # Remove the _id field to avoid serialization issues
                del player['_id']
            return players
        except Exception as e:
            logger.error(f"Failed to get nearby players: {e}")
            return []

    # Chat System
    async def add_chat_message(self, message_data: dict) -> str:
        """Add a chat message"""
        try:
            message_data['timestamp'] = datetime.utcnow()
            result = await self.db.chat_messages.insert_one(message_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to add chat message: {e}")
            raise

    async def get_recent_chat_messages(self, limit: int = 100) -> List[dict]:
        """Get recent global chat messages"""
        try:
            cursor = self.db.chat_messages.find({}).sort("timestamp", -1).limit(limit)
            messages = await cursor.to_list(length=limit)
            for message in messages:
                message['id'] = str(message['_id'])
                # Remove the _id field to avoid serialization issues
                del message['_id']
            # Return in chronological order
            return list(reversed(messages))
        except Exception as e:
            logger.error(f"Failed to get chat messages: {e}")
            return []

    async def add_private_message(self, message_data: dict) -> str:
        """Add a private message"""
        try:
            message_data['timestamp'] = datetime.utcnow()
            result = await self.db.private_messages.insert_one(message_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to add private message: {e}")
            raise

    async def get_private_messages(self, username: str, limit: int = 100) -> List[dict]:
        """Get private messages for a user"""
        try:
            cursor = self.db.private_messages.find({
                "$or": [{"sender": username}, {"receiver": username}]
            }).sort("timestamp", 1).limit(limit)
            messages = await cursor.to_list(length=limit)
            for message in messages:
                message['id'] = str(message['_id'])
            return messages
        except Exception as e:
            logger.error(f"Failed to get private messages: {e}")
            return []

    async def delete_chat_message(self, message_id: str):
        """Delete a chat message (admin only)"""
        try:
            from bson import ObjectId
            await self.db.chat_messages.delete_one({"_id": ObjectId(message_id)})
        except Exception as e:
            logger.error(f"Failed to delete chat message: {e}")
            raise

    # Combat System
    async def add_raid_result(self, raid_data: dict) -> str:
        """Add a raid result"""
        try:
            raid_data['timestamp'] = datetime.utcnow()
            result = await self.db.raids.insert_one(raid_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to add raid result: {e}")
            raise

    async def get_raid_history(self, username: str, limit: int = 20) -> List[dict]:
        """Get raid history for a player"""
        try:
            cursor = self.db.raids.find({
                "$or": [{"attackerUsername": username}, {"defenderUsername": username}]
            }).sort("timestamp", -1).limit(limit)
            raids = await cursor.to_list(length=limit)
            for raid in raids:
                raid['id'] = str(raid['_id'])
            return raids
        except Exception as e:
            logger.error(f"Failed to get raid history: {e}")
            return []

    # Construction System
    async def add_construction_queue_item(self, queue_item: dict) -> str:
        """Add item to construction queue"""
        try:
            result = await self.db.construction_queue.insert_one(queue_item)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to add construction queue item: {e}")
            raise

    async def get_construction_queue(self, player_id: str) -> List[dict]:
        """Get construction queue for a player"""
        try:
            cursor = self.db.construction_queue.find({"playerId": player_id, "completed": False}).sort("startTime", 1)
            queue = await cursor.to_list(length=None)
            for item in queue:
                item['id'] = str(item['_id'])
                # Remove the _id field to avoid serialization issues
                del item['_id']
                # Convert datetime objects to ISO format strings
                if 'startTime' in item and hasattr(item['startTime'], 'isoformat'):
                    item['startTime'] = item['startTime'].isoformat()
                if 'completionTime' in item and hasattr(item['completionTime'], 'isoformat'):
                    item['completionTime'] = item['completionTime'].isoformat()
            return queue
        except Exception as e:
            logger.error(f"Failed to get construction queue: {e}")
            return []

    async def complete_construction_item(self, item_id: str):
        """Mark construction item as completed"""
        try:
            from bson import ObjectId
            await self.db.construction_queue.update_one(
                {"_id": ObjectId(item_id)},
                {"$set": {"completed": True}}
            )
        except Exception as e:
            logger.error(f"Failed to complete construction item: {e}")
            raise

    # Statistics
    async def create_admin_user(self, username: str, password: str, email: str = None):
        """Create an admin user"""
        try:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            # Hash password
            hashed_password = pwd_context.hash(password)
            
            # Create user document
            user_doc = {
                "username": username,
                "password": hashed_password,
                "email": email or f"{username}@admin.com",
                "isAdmin": True,
                "joinDate": datetime.utcnow(),
                "lastActive": datetime.utcnow()
            }
            
            # Create player document
            player_doc = {
                "username": username,
                "kingdomName": f"{username}'s Admin Kingdom",
                "empire": "frankish",
                "resources": {
                    "gold": 10000,
                    "wood": 10000,
                    "stone": 10000,
                    "food": 10000
                },
                "buildings": {
                    "castle": {"level": 5},
                    "farm": {"level": 5},
                    "lumbermill": {"level": 5},
                    "mine": {"level": 5},
                    "barracks": {"level": 5},
                    "blacksmith": {"level": 5}
                },
                "army": {
                    "soldiers": 100,
                    "archers": 50,
                    "cavalry": 25
                },
                "inventory": {
                    "Race Change Scroll": 10
                },
                "constructionQueue": [],
                "power": 1000,
                "lastActive": datetime.utcnow(),
                "createdAt": datetime.utcnow(),
                "isAdmin": True
            }
            
            # Insert user and player
            user_result = await self.db.users.insert_one(user_doc)
            player_doc["userId"] = str(user_result.inserted_id)
            await self.db.players.insert_one(player_doc)
            
            logger.info(f"Admin user '{username}' created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create admin user: {e}")
            return False

    async def get_game_stats(self) -> dict:
        """Get overall game statistics"""
        try:
            total_players = await self.db.players.count_documents({})
            active_players = await self.db.players.count_documents({
                "lastActive": {"$gte": datetime.utcnow() - timedelta(hours=24)}
            })
            total_messages = await self.db.chat_messages.count_documents({})
            
            # Get total power
            pipeline = [{"$group": {"_id": None, "totalPower": {"$sum": "$power"}}}]
            result = await self.db.players.aggregate(pipeline).to_list(length=1)
            total_power = result[0]['totalPower'] if result else 0
            
            # Get top empire
            pipeline = [
                {"$group": {"_id": "$empire", "totalPower": {"$sum": "$power"}}},
                {"$sort": {"totalPower": -1}},
                {"$limit": 1}
            ]
            result = await self.db.players.aggregate(pipeline).to_list(length=1)
            top_empire = result[0]['_id'] if result else "norman"
            
            return {
                "totalPlayers": total_players,
                "activePlayers": active_players,
                "totalMessages": total_messages,
                "totalPower": total_power,
                "topEmpire": top_empire
            }
        except Exception as e:
            logger.error(f"Failed to get game stats: {e}")
            return {
                "totalPlayers": 0,
                "activePlayers": 0,
                "totalMessages": 0,
                "totalPower": 0,
                "topEmpire": "norman"
            }

# Global database instance
db = MongoDB()