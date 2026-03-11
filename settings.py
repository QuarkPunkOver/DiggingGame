import json
import os
from pathlib import Path

class Settings:
    def __init__(self):
        self.sound_enabled = True
        self.music_enabled = True
        self.sound_volume = 0.5
        self.music_volume = 0.3
        self.screen_width = 800
        self.screen_height = 600
        self.fullscreen = False
        
        self.documents_path = str(Path.home() / "Documents" / "DiggingGame")
        self.settings_file = os.path.join(self.documents_path, "settings.json")
        
        if not os.path.exists(self.documents_path):
            os.makedirs(self.documents_path)
        
        self.load()
    
    def save(self):
        data = {
            'sound_enabled': self.sound_enabled,
            'music_enabled': self.music_enabled,
            'sound_volume': self.sound_volume,
            'music_volume': self.music_volume,
            'screen_width': self.screen_width,
            'screen_height': self.screen_height,
            'fullscreen': self.fullscreen
        }
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    def load(self):
        try:
            with open(self.settings_file, 'r') as f:
                data = json.load(f)
                self.sound_enabled = data.get('sound_enabled', True)
                self.music_enabled = data.get('music_enabled', True)
                self.sound_volume = data.get('sound_volume', 0.5)
                self.music_volume = data.get('music_volume', 0.3)
                self.screen_width = data.get('screen_width', 800)
                self.screen_height = data.get('screen_height', 600)
                self.fullscreen = data.get('fullscreen', False)
        except:
            pass
    
    def get_save_path(self, filename):
        return os.path.join(self.documents_path, filename)

settings = Settings()