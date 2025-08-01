from typing import Dict, List
from datetime import datetime, timedelta
import uuid

class BuildingSystem:
    """Building system with costs, production, and construction times"""
    
    BUILDING_DATA = {
        "castle": {
            "name": "Castle",
            "description": "The heart of your kingdom. Increases population capacity.",
            "base_cost": {"gold": 100, "wood": 80, "stone": 120},
            "base_time": 120,  # seconds
            "production": {"gold": 2},
            "max_level": 20
        },
        "farm": {
            "name": "Farm",
            "description": "Produces food to feed your population.",
            "base_cost": {"gold": 50, "wood": 60, "stone": 30},
            "base_time": 60,
            "production": {"food": 3},
            "max_level": 25
        },
        "lumbermill": {
            "name": "Lumbermill",
            "description": "Harvests wood from the nearby forests.",
            "base_cost": {"gold": 40, "wood": 30, "stone": 50},
            "base_time": 45,
            "production": {"wood": 2},
            "max_level": 25
        },
        "mine": {
            "name": "Mine",
            "description": "Extracts stone and precious metals.",
            "base_cost": {"gold": 80, "wood": 40, "stone": 60},
            "base_time": 90,
            "production": {"stone": 2, "gold": 1},
            "max_level": 25
        },
        "barracks": {
            "name": "Barracks",
            "description": "Trains soldiers to defend your kingdom.",
            "base_cost": {"gold": 120, "wood": 100, "stone": 80},
            "base_time": 100,
            "production": {},
            "max_level": 15
        },
        "blacksmith": {
            "name": "Blacksmith",
            "description": "Crafts weapons and tools for your kingdom.",
            "base_cost": {"gold": 90, "wood": 70, "stone": 50},
            "base_time": 75,
            "production": {"gold": 1},
            "max_level": 20
        }
    }

    @classmethod
    def get_default_buildings(cls) -> List[Dict]:
        """Get default buildings for new players"""
        buildings = []
        for building_type, data in cls.BUILDING_DATA.items():
            building = {
                "id": str(uuid.uuid4()),
                "type": building_type,
                "level": 1,
                "constructing": False,
                "description": data["description"],
                "production": data["production"].copy()
            }
            buildings.append(building)
        return buildings

    @classmethod
    def get_building_cost(cls, building_type: str, level: int) -> Dict[str, int]:
        """Calculate building upgrade cost"""
        if building_type not in cls.BUILDING_DATA:
            return {}
        
        base_cost = cls.BUILDING_DATA[building_type]["base_cost"]
        multiplier = 1.5 ** (level - 1)
        
        cost = {}
        for resource, amount in base_cost.items():
            cost[resource] = int(amount * multiplier)
        
        return cost

    @classmethod
    def get_building_time(cls, building_type: str, level: int, empire: str = "norman") -> int:
        """Calculate building construction time in seconds"""
        if building_type not in cls.BUILDING_DATA:
            return 60
        
        base_time = cls.BUILDING_DATA[building_type]["base_time"]
        multiplier = 1.3 ** (level - 1)
        
        # Apply empire bonuses
        from game.empire_bonuses import EmpireBonuses
        time_multiplier = EmpireBonuses.get_construction_time_multiplier(empire, building_type)
        
        return int(base_time * multiplier * time_multiplier)

    @classmethod
    def calculate_resource_generation(cls, buildings: List[Dict], empire: str) -> Dict[str, float]:
        """Calculate total resource generation per second"""
        from game.empire_bonuses import EmpireBonuses
        
        generation = {"gold": 0, "wood": 0, "stone": 0, "food": 0}
        
        for building in buildings:
            if "production" in building and building["production"]:
                level = building.get("level", 1)
                for resource, base_amount in building["production"].items():
                    # Base production scaled by level
                    production = base_amount * level
                    
                    # Apply empire bonuses
                    final_production = EmpireBonuses.apply_resource_bonus(empire, resource, production)
                    generation[resource] += final_production
        
        return generation

    @classmethod
    def can_afford_building(cls, resources: Dict[str, int], building_type: str, level: int) -> bool:
        """Check if player can afford building upgrade"""
        cost = cls.get_building_cost(building_type, level)
        
        for resource, amount in cost.items():
            if resources.get(resource, 0) < amount:
                return False
        
        return True

    @classmethod
    def deduct_building_cost(cls, resources: Dict[str, int], building_type: str, level: int) -> Dict[str, int]:
        """Deduct building cost from resources"""
        cost = cls.get_building_cost(building_type, level)
        new_resources = resources.copy()
        
        for resource, amount in cost.items():
            new_resources[resource] = max(0, new_resources[resource] - amount)
        
        return new_resources

    @classmethod
    def calculate_power_from_buildings(cls, buildings: List[Dict]) -> int:
        """Calculate power contribution from buildings"""
        total_power = 0
        for building in buildings:
            level = building.get("level", 1)
            building_type = building.get("type", "")
            
            # Different building types contribute different power amounts
            base_power = {
                "castle": 150,
                "barracks": 120,
                "blacksmith": 100,
                "mine": 80,
                "farm": 60,
                "lumbermill": 60
            }
            
            power_per_level = base_power.get(building_type, 50)
            total_power += power_per_level * level
        
        return total_power

    @classmethod
    def create_construction_queue_item(cls, player_id: str, building_id: str, building_type: str, target_level: int, empire: str) -> Dict:
        """Create a construction queue item"""
        construction_time = cls.get_building_time(building_type, target_level, empire)
        start_time = datetime.utcnow()
        completion_time = start_time + timedelta(seconds=construction_time)
        
        return {
            "id": str(uuid.uuid4()),
            "playerId": player_id,
            "buildingId": building_id,
            "buildingType": building_type,
            "targetLevel": target_level,
            "startTime": start_time,
            "completionTime": completion_time,
            "completed": False
        }