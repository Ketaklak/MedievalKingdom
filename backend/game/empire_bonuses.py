from typing import Dict

class EmpireBonuses:
    """Empire bonuses and special abilities"""
    
    EMPIRE_DATA = {
        "norman": {
            "name": "Norman Empire",
            "bonuses": {
                "gold": 25,
                "stone": 20
            },
            "special_abilities": [
                "Castle construction 25% faster",
                "Additional defense bonus in sieges"
            ],
            "starting_resources": {
                "gold": 1875,  # 1500 * 1.25
                "wood": 800,
                "stone": 720,   # 600 * 1.20
                "food": 400
            }
        },
        "viking": {
            "name": "Viking Kingdom", 
            "bonuses": {
                "wood": 30,
                "food": 15
            },
            "special_abilities": [
                "Raid damage +30%",
                "Ship building available",
                "Coastal bonuses"
            ],
            "starting_resources": {
                "gold": 1500,
                "wood": 1040,  # 800 * 1.30
                "stone": 600,
                "food": 460    # 400 * 1.15
            }
        },
        "saxon": {
            "name": "Saxon Realm",
            "bonuses": {
                "food": 25,
                "gold": 15
            },
            "special_abilities": [
                "Farm production +25%",
                "Defensive structures +20% effectiveness",
                "Militia recruitment bonus"
            ],
            "starting_resources": {
                "gold": 1725,  # 1500 * 1.15
                "wood": 800,
                "stone": 600,
                "food": 500    # 400 * 1.25
            }
        },
        "celtic": {
            "name": "Celtic Clans",
            "bonuses": {
                "wood": 20,
                "stone": 20
            },
            "special_abilities": [
                "Druid buildings available",
                "Forest bonuses",
                "Mystical research options"
            ],
            "starting_resources": {
                "gold": 1500,
                "wood": 960,   # 800 * 1.20
                "stone": 720,  # 600 * 1.20
                "food": 400
            }
        },
        "frankish": {
            "name": "Frankish Empire",
            "bonuses": {
                "gold": 20,
                "food": 20
            },
            "special_abilities": [
                "Trade routes +20% profit",
                "Cavalry units +25% strength",
                "Diplomatic bonuses"
            ],
            "starting_resources": {
                "gold": 1800,  # 1500 * 1.20
                "wood": 800,
                "stone": 600,
                "food": 480    # 400 * 1.20
            }
        }
    }

    @classmethod
    def get_empire_info(cls, empire: str) -> Dict:
        """Get complete empire information"""
        return cls.EMPIRE_DATA.get(empire, cls.EMPIRE_DATA["norman"])

    @classmethod
    def get_empire_bonuses(cls, empire: str) -> Dict[str, int]:
        """Get resource bonuses for an empire"""
        empire_data = cls.get_empire_info(empire)
        return empire_data.get("bonuses", {})

    @classmethod
    def get_starting_resources(cls, empire: str) -> Dict[str, int]:
        """Get starting resources for an empire"""
        empire_data = cls.get_empire_info(empire)
        return empire_data.get("starting_resources", {
            "gold": 1500,
            "wood": 800,
            "stone": 600,
            "food": 400
        })

    @classmethod
    def apply_resource_bonus(cls, empire: str, resource: str, base_amount: int) -> int:
        """Apply empire bonus to resource production"""
        bonuses = cls.get_empire_bonuses(empire)
        bonus_percentage = bonuses.get(resource, 0)
        return int(base_amount * (1 + bonus_percentage / 100))

    @classmethod
    def get_construction_time_multiplier(cls, empire: str, building_type: str) -> float:
        """Get construction time multiplier for empire bonuses"""
        if empire == "norman" and building_type == "castle":
            return 0.75  # 25% faster
        return 1.0

    @classmethod
    def get_raid_damage_multiplier(cls, empire: str) -> float:
        """Get raid damage multiplier"""
        if empire == "viking":
            return 1.30  # 30% more damage
        return 1.0

    @classmethod
    def get_defense_bonus(cls, empire: str) -> float:
        """Get defensive bonus"""
        if empire == "saxon":
            return 1.20  # 20% defense bonus
        if empire == "norman":
            return 1.10  # 10% defense bonus
        return 1.0