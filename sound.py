import pygame
import math
import os
from settings import settings

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.load_sounds()
    
    def load_sounds(self):
        sound_folder = "sounds"
        sound_files = {
            'dig': 'dig.wav',
            'move': 'move.wav',
            'collect': 'collect.wav',
            'upgrade': 'upgrade.wav',
            'repair': 'repair.wav',
            'fuel': 'fuel.wav',
            'evacuation': 'evacuation.wav',
            'victory': 'victory.wav',
            'save': 'save.wav',
            'menu_click': 'menu_click.wav'
        }
        
        for name, filename in sound_files.items():
            filepath = os.path.join(sound_folder, filename)
            if os.path.exists(filepath):
                try:
                    self.sounds[name] = pygame.mixer.Sound(filepath)
                except:
                    self.sounds[name] = self.create_dummy_sound()
            else:
                self.sounds[name] = self.create_dummy_sound()
    
    def create_dummy_sound(self):
        class DummySound:
            def play(self):
                pass
            def set_volume(self, vol):
                pass
        return DummySound()
    
    def play(self, sound_name):
        if settings.sound_enabled and sound_name in self.sounds:
            try:
                self.sounds[sound_name].set_volume(settings.sound_volume)
                self.sounds[sound_name].play()
            except:
                pass
    
    def set_volume(self, volume):
        for sound in self.sounds.values():
            try:
                sound.set_volume(volume)
            except:
                pass

sound_manager = SoundManager()