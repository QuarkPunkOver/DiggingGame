import pygame
import math
import os
import sys
from settings import settings

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_volume = settings.music_volume
        self.current_music = None
        self.music_position = 0
        self.in_transition = False
        self.transition_start_time = 0
        self.transition_duration = 10000
        self.fadeout_active = False
        self.fadeout_start_time = 0
        self.fadeout_duration = 5000
        self.last_depth = 0
        self.music_stopped_at_depth = False
        self.last_played_music = None
        self.upper_boundary = 125
        self.lower_boundary = 125
        self.transition_zone = 10
        self.load_sounds()
    
    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def load_sounds(self):
        sound_folder = self.resource_path("sounds")
        sound_files = {
            'dig': 'dig.mp3',
            'move': 'move.mp3',
            'collect': 'collect.mp3',
            'upgrade': 'upgrade.mp3',
            'repair': 'repair.mp3',
            'fuel': 'fuel.mp3',
            'evacuation': 'evacuation.mp3',
            'victory': 'victory.mp3',
            'save': 'save.mp3',
            'menu_click': 'menu_click.mp3',
            'ost_upper': 'ost_upper.mp3',
            'ost_lower': 'ost_lower.mp3',
            'ost_transition': 'ost_transition.mp3',
            'ost_complete': 'ost_complete.mp3'
        }
        
        for name, filename in sound_files.items():
            filepath = os.path.join(sound_folder, filename)
            if os.path.exists(filepath):
                try:
                    if name.startswith('ost_'):
                        self.sounds[name] = filepath
                    else:
                        self.sounds[name] = pygame.mixer.Sound(filepath)
                        self.sounds[name].set_volume(settings.sound_volume)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
                    if name.startswith('ost_'):
                        self.sounds[name] = filepath
                    else:
                        self.sounds[name] = self.create_dummy_sound()
            else:
                print(f"File not found: {filepath}")
                if name.startswith('ost_'):
                    self.sounds[name] = filepath
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
                if isinstance(self.sounds[sound_name], pygame.mixer.Sound):
                    self.sounds[sound_name].play()
            except:
                pass
    
    def set_sound_volume(self, volume):
        for sound in self.sounds.values():
            try:
                if isinstance(sound, pygame.mixer.Sound):
                    sound.set_volume(volume)
            except:
                pass
    
    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        if not self.fadeout_active:
            pygame.mixer.music.set_volume(self.music_volume)
    
    def update_music(self, player_y, world_depth):
        if not settings.music_enabled:
            return
        
        self.last_depth = player_y
        
        if player_y < self.upper_boundary - self.transition_zone:
            zone = "upper"
        elif player_y > self.lower_boundary + self.transition_zone:
            zone = "lower"
        elif player_y >= self.upper_boundary - self.transition_zone and player_y <= self.lower_boundary + self.transition_zone:
            zone = "transition"
        else:
            zone = "unknown"
        
        if zone == "upper":
            if self.music_stopped_at_depth:
                self.resume_music('ost_upper')
            elif self.fadeout_active:
                self.stop_fadeout()
            else:
                self.start_music_transition('ost_upper')
        
        elif zone == "lower":
            if self.music_stopped_at_depth:
                self.resume_music('ost_lower')
            elif self.fadeout_active:
                self.stop_fadeout()
            else:
                self.start_music_transition('ost_lower')
        
        elif zone == "transition":
            if self.music_stopped_at_depth:
                self.resume_music('ost_complete')
            elif self.fadeout_active:
                self.stop_fadeout()
            else:
                self.start_music_transition('ost_complete')
    
    def start_music_transition(self, new_music):
        if new_music not in self.sounds:
            return
        
        if new_music == self.current_music and not self.music_stopped_at_depth:
            return
        
        self.last_played_music = new_music

        if pygame.mixer.music.get_busy():
            self.music_position = pygame.mixer.music.get_pos()
            pygame.mixer.music.fadeout(self.transition_duration)
        else:
            self.music_position = 0

        self.in_transition = True
        self.transition_start_time = pygame.time.get_ticks()
        self.current_music = new_music
        self.music_stopped_at_depth = False
        self.fadeout_active = False

        pygame.time.set_timer(pygame.USEREVENT + 1, self.transition_duration, True)
    
    def start_fadeout(self):
        pass
    
    def stop_fadeout(self):
        if not self.fadeout_active:
            return
        
        self.fadeout_active = False
        
        if self.current_music and self.current_music in self.sounds:
            music_file = self.sounds[self.current_music]
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)
            except Exception as e:
                pass
    
    def resume_music(self, music_to_play=None):
        if music_to_play:
            self.last_played_music = music_to_play
        elif not self.last_played_music:
            self.last_played_music = 'ost_upper'
        
        music = self.last_played_music
        
        if music in self.sounds:
            music_file = self.sounds[music]
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)
                self.current_music = music
                self.music_stopped_at_depth = False
                self.fadeout_active = False
            except Exception as e:
                pass
    
    def finish_transition(self):
        if self.current_music and self.current_music in self.sounds:
            music_file = self.sounds[self.current_music]
            try:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(self.music_volume)
                start_pos = self.music_position / 1000.0
                pygame.mixer.music.play(-1, start_pos)
            except Exception as e:
                pass
        self.in_transition = False
    
    def play_music(self, music_name):
        if music_name in self.sounds:
            music_file = self.sounds[music_name]
            try:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)
                self.current_music = music_name
                self.last_played_music = music_name
                self.fadeout_active = False
                self.music_stopped_at_depth = False
            except Exception as e:
                pass
    
    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_music = None
        self.fadeout_active = False
        self.music_stopped_at_depth = False
    
    def pause_music(self):
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        pygame.mixer.music.unpause()
    
    def update(self, current_time):
        pass

sound_manager = SoundManager()