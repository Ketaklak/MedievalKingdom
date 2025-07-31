from typing import Dict, Tuple
import random
import uuid
from datetime import datetime

class CombatSystem:
    """Combat and raid system"""
    
    @classmethod
    def calculate_raid_result(cls, attacker_data: Dict, defender_data: Dict) -> Dict:
        """Calculate the result of a raid"""
        attacker_power = cls.calculate_battle_power(attacker_data)
        defender_power = cls.calculate_battle_power(defender_data)
        
        # Apply empire bonuses
        from .empire_bonuses import EmpireBonuses
        attacker_empire = attacker_data.get("empire", "norman")
        defender_empire = defender_data.get("empire", "norman")
        
        attacker_power *= EmpireBonuses.get_raid_damage_multiplier(attacker_empire)
        defender_power *= EmpireBonuses.get_defense_bonus(defender_empire)
        
        # Calculate win probability
        total_power = attacker_power + defender_power
        attacker_win_chance = attacker_power / total_power if total_power > 0 else 0.5
        
        # Add some randomness
        attacker_win_chance = min(0.9, max(0.1, attacker_win_chance + random.uniform(-0.2, 0.2)))
        
        success = random.random() < attacker_win_chance
        
        # Calculate stolen resources
        stolen_resources = {}
        if success:
            defender_resources = defender_data.get("resources", {})
            max_steal_percentage = min(0.3, attacker_power / (defender_power + 1) * 0.5)
            
            for resource, amount in defender_resources.items():
                steal_percentage = random.uniform(0.05, max_steal_percentage)
                stolen_amount = int(amount * steal_percentage)
                if stolen_amount > 0:
                    stolen_resources[resource] = stolen_amount
        
        # Calculate casualties
        attacker_losses = cls.calculate_casualties(attacker_data["army"], success, is_attacker=True)
        defender_losses = cls.calculate_casualties(defender_data["army"], success, is_attacker=False)
        
        # Generate battle report
        battle_report = cls.generate_battle_report(
            attacker_data["username"], 
            defender_data["username"],
            success, 
            stolen_resources, 
            attacker_losses, 
            defender_losses
        )
        
        return {
            "id": str(uuid.uuid4()),
            "attackerId": attacker_data["userId"],
            "defenderId": defender_data["userId"],
            "attackerUsername": attacker_data["username"],
            "defenderUsername": defender_data["username"],
            "armySize": attacker_data["army"],
            "success": success,
            "stolenResources": stolen_resources,
            "attackerLosses": attacker_losses,
            "defenderLosses": defender_losses,
            "timestamp": datetime.utcnow(),
            "battleReport": battle_report
        }

    @classmethod
    def calculate_battle_power(cls, player_data: Dict) -> float:
        """Calculate battle power of a player"""
        army_size = player_data.get("army", 0)
        buildings = player_data.get("buildings", [])
        
        # Base army power
        army_power = army_size * 10
        
        # Building bonuses
        building_power = 0
        for building in buildings:
            if building["type"] == "barracks":
                building_power += building["level"] * 20
            elif building["type"] == "blacksmith":
                building_power += building["level"] * 15
            elif building["type"] == "castle":
                building_power += building["level"] * 10
        
        return army_power + building_power

    @classmethod
    def calculate_casualties(cls, army_size: int, battle_won: bool, is_attacker: bool) -> int:
        """Calculate army casualties from battle"""
        if army_size == 0:
            return 0
        
        base_loss_rate = 0.1 if battle_won else 0.2
        if is_attacker:
            base_loss_rate += 0.05  # Attackers generally lose more
        
        # Add randomness
        loss_rate = base_loss_rate + random.uniform(-0.05, 0.1)
        loss_rate = max(0.05, min(0.4, loss_rate))
        
        casualties = int(army_size * loss_rate)
        return min(casualties, army_size)

    @classmethod
    def generate_battle_report(cls, attacker: str, defender: str, success: bool, 
                             stolen_resources: Dict, attacker_losses: int, defender_losses: int) -> str:
        """Generate a battle report description"""
        if success:
            report = f"{attacker}'s forces successfully raided {defender}'s kingdom! "
            if stolen_resources:
                resource_list = []
                for resource, amount in stolen_resources.items():
                    resource_list.append(f"{amount} {resource}")
                report += f"Stolen: {', '.join(resource_list)}. "
            else:
                report += "However, no significant resources were captured. "
        else:
            report = f"{attacker}'s raid on {defender}'s kingdom was repelled! "
        
        report += f"Casualties - Attacker: {attacker_losses}, Defender: {defender_losses}"
        
        return report

    @classmethod
    def can_raid_target(cls, attacker_data: Dict, defender_data: Dict) -> Tuple[bool, str]:
        """Check if attacker can raid the target"""
        if attacker_data["army"] <= 0:
            return False, "No army available for raid"
        
        if attacker_data["username"] == defender_data["username"]:
            return False, "Cannot raid yourself"
        
        # Check if target has protection (new players, recently raided, etc.)
        last_raid_time = defender_data.get("lastRaidTime")
        if last_raid_time:
            from datetime import timedelta
            protection_time = timedelta(hours=1)  # 1 hour protection after being raided
            if datetime.utcnow() - last_raid_time < protection_time:
                return False, "Target is under protection"
        
        return True, "Raid allowed"

    @classmethod
    def apply_raid_results(cls, attacker_data: Dict, defender_data: Dict, raid_result: Dict) -> Tuple[Dict, Dict]:
        """Apply raid results to both players"""
        # Update attacker
        new_attacker_data = attacker_data.copy()
        if raid_result["success"] and raid_result["stolenResources"]:
            for resource, amount in raid_result["stolenResources"].items():
                new_attacker_data["resources"][resource] += amount
        
        # Reduce attacker army
        new_attacker_data["army"] = max(0, new_attacker_data["army"] - raid_result["attackerLosses"])
        
        # Update defender
        new_defender_data = defender_data.copy()
        if raid_result["success"] and raid_result["stolenResources"]:
            for resource, amount in raid_result["stolenResources"].items():
                new_defender_data["resources"][resource] = max(0, new_defender_data["resources"][resource] - amount)
        
        # Reduce defender army
        new_defender_data["army"] = max(0, new_defender_data["army"] - raid_result["defenderLosses"])
        new_defender_data["lastRaidTime"] = datetime.utcnow()
        
        return new_attacker_data, new_defender_data