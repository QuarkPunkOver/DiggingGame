import json
import os

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "sound_enabled": True,
    "sound_volume": 0.7,
    "music_enabled": True,
    "music_volume": 0.5
}

class Settings:
    def __init__(self):
        self.sound_enabled = DEFAULT_SETTINGS["sound_enabled"]
        self.sound_volume = DEFAULT_SETTINGS["sound_volume"]
        self.music_enabled = DEFAULT_SETTINGS["music_enabled"]
        self.music_volume = DEFAULT_SETTINGS["music_volume"]
        self.load()
    
    def load(self):
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r') as f:
                    data = json.load(f)
                    self.sound_enabled = data.get("sound_enabled", DEFAULT_SETTINGS["sound_enabled"])
                    self.sound_volume = data.get("sound_volume", DEFAULT_SETTINGS["sound_volume"])
                    self.music_enabled = data.get("music_enabled", DEFAULT_SETTINGS["music_enabled"])
                    self.music_volume = data.get("music_volume", DEFAULT_SETTINGS["music_volume"])
        except:
            pass
    
    def save(self):
        data = {
            "sound_enabled": self.sound_enabled,
            "sound_volume": self.sound_volume,
            "music_enabled": self.music_enabled,
            "music_volume": self.music_volume
        }
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(data, f)
        except:
            pass

settings = Settings()