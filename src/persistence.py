import json
import os

SAVE_FILE = "save_game.json"

class PersistenceManager:
    def __init__(self):
        self.data = self._get_default_data()

    def _get_default_data(self):
        return {
            "xp": 0,
            "unlocked_levels": [0], # 0-based index for Level 1
            "current_level": 0
        }

    def load_data(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r') as f:
                    loaded = json.load(f)
                    
                    # Migration: Coins -> XP
                    if "coins" in loaded and "xp" not in loaded:
                        loaded["xp"] = loaded.pop("coins")
                        
                    # Merge with default to ensure all keys exist
                    default = self._get_default_data()
                    
                    if "unlocked_levels" not in loaded:
                        loaded["unlocked_levels"] = [0]
                    if "xp" not in loaded:
                        loaded["xp"] = 0
                    
                    self.data = loaded
                    print(f"Loaded data: {self.data}")
            except Exception as e:
                print(f"Error loading save: {e}")
                self.data = self._get_default_data()
        else:
            print("No save file found, using defaults.")
            self.data = self._get_default_data()
            self.save_data() # Create file
        
        return self.data

    def save_data(self):
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump(self.data, f, indent=4)
            print("Game Saved.")
        except Exception as e:
            print(f"Error saving game: {e}")

    def get_xp(self):
        return self.data.get("xp", 0)

    def add_xp(self, amount):
        self.data["xp"] = self.data.get("xp", 0) + amount
        self.save_data()

    def spend_xp(self, amount):
        if self.data.get("xp", 0) >= amount:
            self.data["xp"] -= amount
            self.save_data()
            return True
        return False

    def unlock_level(self, level_index):
        if level_index not in self.data["unlocked_levels"]:
            self.data["unlocked_levels"].append(level_index)
            self.save_data()

    def is_level_unlocked(self, level_index):
        return level_index in self.data["unlocked_levels"]
