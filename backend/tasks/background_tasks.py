import asyncio
import logging
from datetime import datetime, timedelta
from ..database.mongodb import db
from ..game.buildings import BuildingSystem

logger = logging.getLogger(__name__)

class BackgroundTasks:
    """Background tasks for game maintenance"""
    
    def __init__(self):
        self.running = False
        self.tasks = []

    async def start_all_tasks(self):
        """Start all background tasks"""
        if self.running:
            return
        
        self.running = True
        logger.info("Starting background tasks...")
        
        # Start individual tasks
        self.tasks = [
            asyncio.create_task(self.resource_generation_task()),
            asyncio.create_task(self.construction_completion_task()),
            asyncio.create_task(self.cleanup_expired_data_task()),
            asyncio.create_task(self.update_player_power_task())
        ]
        
        logger.info("Background tasks started")

    async def stop_all_tasks(self):
        """Stop all background tasks"""
        self.running = False
        
        for task in self.tasks:
            task.cancel()
        
        await asyncio.gather(*self.tasks, return_exceptions=True)
        logger.info("Background tasks stopped")

    async def resource_generation_task(self):
        """Generate resources for all players every 10 seconds"""
        while self.running:
            try:
                await self.generate_resources_for_all_players()
                await asyncio.sleep(10)  # Run every 10 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Resource generation task error: {e}")
                await asyncio.sleep(30)  # Wait longer if error

    async def construction_completion_task(self):
        """Check for completed constructions every 5 seconds"""
        while self.running:
            try:
                await self.complete_finished_constructions()
                await asyncio.sleep(5)  # Run every 5 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Construction completion task error: {e}")
                await asyncio.sleep(30)

    async def cleanup_expired_data_task(self):
        """Clean up expired data every hour"""
        while self.running:
            try:
                await self.cleanup_expired_data()
                await asyncio.sleep(3600)  # Run every hour
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
                await asyncio.sleep(3600)

    async def update_player_power_task(self):
        """Update player power rankings every 30 seconds"""
        while self.running:
            try:
                await self.update_all_player_power()
                await asyncio.sleep(30)  # Run every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Power update task error: {e}")
                await asyncio.sleep(60)

    async def generate_resources_for_all_players(self):
        """Generate resources for all active players"""
        try:
            # Get all players active in last 24 hours
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            cursor = db.db.players.find({
                "lastActive": {"$gte": cutoff_time}
            })
            
            active_players = await cursor.to_list(length=None)
            
            for player in active_players:
                try:
                    # Calculate resource generation
                    generation = BuildingSystem.calculate_resource_generation(
                        player["buildings"], player["empire"]
                    )
                    
                    # Apply generation (10 seconds worth)
                    new_resources = player["resources"].copy()
                    for resource, rate in generation.items():
                        new_resources[resource] += int(rate * 10)  # 10 seconds
                    
                    # Update player resources
                    await db.db.players.update_one(
                        {"_id": player["_id"]},
                        {"$set": {"resources": new_resources}}
                    )
                    
                except Exception as e:
                    logger.error(f"Error generating resources for {player['username']}: {e}")
            
            logger.debug(f"Generated resources for {len(active_players)} active players")
            
        except Exception as e:
            logger.error(f"Resource generation error: {e}")

    async def complete_finished_constructions(self):
        """Complete finished construction items"""
        try:
            # Find completed constructions
            now = datetime.utcnow()
            
            cursor = db.db.construction_queue.find({
                "completed": False,
                "completionTime": {"$lte": now}
            })
            
            completed_items = await cursor.to_list(length=None)
            
            for item in completed_items:
                try:
                    # Get player
                    player = await db.db.players.find_one({"_id": item["playerId"]})
                    if not player:
                        continue
                    
                    # Update building level
                    updated_buildings = []
                    for building in player["buildings"]:
                        if building["id"] == item["buildingId"]:
                            building["level"] = item["targetLevel"]
                            building["constructing"] = False
                        updated_buildings.append(building)
                    
                    # Update player
                    await db.db.players.update_one(
                        {"_id": player["_id"]},
                        {"$set": {"buildings": updated_buildings}}
                    )
                    
                    # Mark construction as completed
                    await db.db.construction_queue.update_one(
                        {"_id": item["_id"]},
                        {"$set": {"completed": True}}
                    )
                    
                    logger.info(f"Completed construction: {item['buildingType']} level {item['targetLevel']} for {player['username']}")
                    
                except Exception as e:
                    logger.error(f"Error completing construction {item['_id']}: {e}")
            
        except Exception as e:
            logger.error(f"Construction completion error: {e}")

    async def cleanup_expired_data(self):
        """Clean up old/expired data"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=30)
            
            # Clean up old chat messages (keep last 1000)
            message_count = await db.db.chat_messages.count_documents({})
            if message_count > 1000:
                # Get oldest messages to delete
                oldest_messages = await db.db.chat_messages.find({}).sort("timestamp", 1).limit(message_count - 1000).to_list(length=None)
                message_ids = [msg["_id"] for msg in oldest_messages]
                await db.db.chat_messages.delete_many({"_id": {"$in": message_ids}})
                logger.info(f"Cleaned up {len(message_ids)} old chat messages")
            
            # Clean up old private messages (older than 30 days)
            result = await db.db.private_messages.delete_many({
                "timestamp": {"$lt": cutoff_time}
            })
            if result.deleted_count > 0:
                logger.info(f"Cleaned up {result.deleted_count} old private messages")
            
            # Clean up completed constructions (older than 7 days)
            construction_cutoff = datetime.utcnow() - timedelta(days=7)
            result = await db.db.construction_queue.delete_many({
                "completed": True,
                "completionTime": {"$lt": construction_cutoff}
            })
            if result.deleted_count > 0:
                logger.info(f"Cleaned up {result.deleted_count} old construction records")
            
            # Clean up old raid records (older than 30 days)
            result = await db.db.raids.delete_many({
                "timestamp": {"$lt": cutoff_time}
            })
            if result.deleted_count > 0:
                logger.info(f"Cleaned up {result.deleted_count} old raid records")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    async def update_all_player_power(self):
        """Recalculate power for all players"""
        try:
            cursor = db.db.players.find({})
            players = await cursor.to_list(length=None)
            
            for player in players:
                try:
                    # Calculate building power
                    building_power = BuildingSystem.calculate_power_from_buildings(player["buildings"])
                    
                    # Calculate army power
                    army_power = sum(player["army"].values()) * 50
                    
                    # Calculate resource power (1 power per 100 resources)
                    resource_power = sum(player["resources"].values()) // 100
                    
                    # Total power
                    total_power = building_power + army_power + resource_power
                    
                    # Update player power
                    await db.db.players.update_one(
                        {"_id": player["_id"]},
                        {"$set": {"power": total_power}}
                    )
                    
                except Exception as e:
                    logger.error(f"Error updating power for {player['username']}: {e}")
            
            logger.debug(f"Updated power for {len(players)} players")
            
        except Exception as e:
            logger.error(f"Power update error: {e}")

    async def simulate_ai_activity(self):
        """Simulate AI player activity"""
        try:
            # Get AI players (those with specific usernames)
            ai_usernames = ['KingArthur', 'VikingRagnar', 'SaxonEdward', 'CelticBoudica', 'FrankishCharles', 'QueenEleanor', 'VikingErik', 'SaxonAlfred']
            
            cursor = db.db.players.find({"username": {"$in": ai_usernames}})
            ai_players = await cursor.to_list(length=None)
            
            for player in ai_players:
                try:
                    # Randomly upgrade buildings
                    if len(player["buildings"]) > 0 and random.random() < 0.1:  # 10% chance
                        import random
                        building = random.choice(player["buildings"])
                        if not building["constructing"] and building["level"] < 10:
                            building["level"] += 1
                            
                            await db.db.players.update_one(
                                {"_id": player["_id"]},
                                {"$set": {"buildings": player["buildings"]}}
                            )
                    
                    # Randomly recruit army
                    if random.random() < 0.05:  # 5% chance
                        current_army = sum(player["army"].values())
                        if current_army < 200:
                            player["army"]["soldiers"] += random.randint(5, 15)
                            
                            await db.db.players.update_one(
                                {"_id": player["_id"]},
                                {"$set": {"army": player["army"]}}
                            )
                    
                    # Update last active to keep them "online"
                    await db.db.players.update_one(
                        {"_id": player["_id"]},
                        {"$set": {"lastActive": datetime.utcnow()}}
                    )
                    
                except Exception as e:
                    logger.error(f"Error simulating AI activity for {player['username']}: {e}")
            
        except Exception as e:
            logger.error(f"AI simulation error: {e}")

# Global background tasks instance
background_tasks = BackgroundTasks()