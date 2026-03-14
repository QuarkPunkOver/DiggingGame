import json
import os

class Settings:
    def __init__(self):
        self.sound_enabled = True
        self.music_enabled = True
        self.sound_volume = 0.7
        self.music_volume = 0.5
        self.screen_width = 1024
        self.screen_height = 768
        self.fullscreen = False
        self.language = 'en'
        self.load()
    
    def load(self):
        try:
            with open('settings.json', 'r') as f:
                data = json.load(f)
                self.sound_enabled = data.get('sound_enabled', True)
                self.music_enabled = data.get('music_enabled', True)
                self.sound_volume = data.get('sound_volume', 0.7)
                self.music_volume = data.get('music_volume', 0.5)
                self.screen_width = data.get('screen_width', 1024)
                self.screen_height = data.get('screen_height', 768)
                self.fullscreen = data.get('fullscreen', False)
                self.language = data.get('language', 'en')
        except:
            pass
    
    def save(self):
        data = {
            'sound_enabled': self.sound_enabled,
            'music_enabled': self.music_enabled,
            'sound_volume': self.sound_volume,
            'music_volume': self.music_volume,
            'screen_width': self.screen_width,
            'screen_height': self.screen_height,
            'fullscreen': self.fullscreen,
            'language': self.language
        }
        try:
            with open('settings.json', 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    def get_save_path(self, filename):
        return os.path.join(os.path.dirname(__file__), filename)

settings = Settings()