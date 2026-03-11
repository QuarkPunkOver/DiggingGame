import pygame
import os
import sys
from settings import settings

pygame.init()
pygame.mixer.init()

if settings.fullscreen:
    SCREEN = pygame.display.set_mode((settings.screen_width, settings.screen_height), pygame.FULLSCREEN)
else:
    SCREEN = pygame.display.set_mode((settings.screen_width, settings.screen_height))

pygame.display.set_caption("Digging Game - Core of the Earth")
CLOCK = pygame.time.Clock()
FONT = pygame.font.Font(None, 36)
SMALL_FONT = pygame.font.Font(None, 24)
TITLE_FONT = pygame.font.Font(None, 72)

TILE_SIZE = 16
WORLD_WIDTH = 255
WORLD_DEPTH = 255
SCREEN_WIDTH, SCREEN_HEIGHT = settings.screen_width, settings.screen_height
MOVE_FUEL_COST = 0.1
DIG_FUEL_COST = 0.1
INITIAL_FUEL = 200
EVACUATION_FUEL = 200
REPAIR_COST = 25

from settings import settings
SAVE_FILE = settings.get_save_path("savegame.json")

SURFACE_TEMP = 20
CORE_TEMP = 5000

COLORS = {
    'surface': (34, 139, 34),
    'soil': (139, 69, 19),
    'dense_earth': (160, 82, 45),
    'gravel': (128, 128, 128),
    'soft_stone': (169, 169, 169),
    'stone': (139, 90, 43),
    'dense_stone': (101, 67, 33),
    'andesite': (128, 128, 128),
    'granite': (200, 200, 200),
    'soft_matter': (150, 100, 150),
    'dense_matter': (100, 50, 100),
    'core': (255, 69, 0),
    'magma': (255, 140, 0),
    'coal': (20, 20, 20),
    'silicon': (100, 100, 150),
    'copper': (184, 115, 51),
    'tin': (192, 192, 192),
    'iron': (139, 69, 19),
    'gold': (255, 215, 0),
    'platinum': (229, 228, 226),
    'tungsten': (80, 80, 80),
    'diamond': (185, 242, 255),
    'uranium': (57, 255, 20),
    'uranium_isotope': (0, 255, 0),
    'core_fragment': (255, 100, 100),
    'air': (255, 255, 255),
    'player': (255, 0, 0),
    'fuel_station': (0, 255, 0),
    'shop': (0, 0, 255),
    'tech_service': (255, 255, 0),
    'save_point': (255, 255, 255),
}

TILE_TYPES = {
    'surface': {'hardness': 0.5, 'resource': 'surface', 'color': COLORS['surface']},
    'soil': {'hardness': 1, 'resource': 'soil', 'color': COLORS['soil']},
    'dense_earth': {'hardness': 2, 'resource': 'dense_earth', 'color': COLORS['dense_earth']},
    'gravel': {'hardness': 3, 'resource': 'gravel', 'color': COLORS['gravel']},
    'soft_stone': {'hardness': 4, 'resource': 'soft_stone', 'color': COLORS['soft_stone']},
    'stone': {'hardness': 5, 'resource': 'stone', 'color': COLORS['stone']},
    'dense_stone': {'hardness': 6, 'resource': 'dense_stone', 'color': COLORS['dense_stone']},
    'andesite': {'hardness': 7, 'resource': 'andesite', 'color': COLORS['andesite']},
    'granite': {'hardness': 8, 'resource': 'granite', 'color': COLORS['granite']},
    'soft_matter': {'hardness': 9, 'resource': 'soft_matter', 'color': COLORS['soft_matter']},
    'dense_matter': {'hardness': 10, 'resource': 'dense_matter', 'color': COLORS['dense_matter']},
    'magma': {'hardness': 15, 'resource': 'magma', 'color': COLORS['magma']},
    'core': {'hardness': 30, 'resource': None, 'color': COLORS['core']},
    'coal': {'hardness': 2, 'resource': 'coal', 'color': COLORS['coal']},
    'silicon': {'hardness': 2, 'resource': 'silicon', 'color': COLORS['silicon']},
    'copper': {'hardness': 4, 'resource': 'copper', 'color': COLORS['copper']},
    'tin': {'hardness': 4, 'resource': 'tin', 'color': COLORS['tin']},
    'iron': {'hardness': 6, 'resource': 'iron', 'color': COLORS['iron']},
    'gold': {'hardness': 7, 'resource': 'gold', 'color': COLORS['gold']},
    'platinum': {'hardness': 8, 'resource': 'platinum', 'color': COLORS['platinum']},
    'tungsten': {'hardness': 8, 'resource': 'tungsten', 'color': COLORS['tungsten']},
    'diamond': {'hardness': 9, 'resource': 'diamond', 'color': COLORS['diamond']},
    'uranium': {'hardness': 8, 'resource': 'uranium', 'color': COLORS['uranium']},
    'uranium_isotope': {'hardness': 9, 'resource': 'uranium_isotope', 'color': COLORS['uranium_isotope']},
    'core_fragment': {'hardness': 1, 'resource': 'core_fragment', 'color': COLORS['core_fragment']},
}

LAYERS = [
    (0, 1, 'surface', None, 0),
    (1, 5, 'soil', None, 0),
    (5, 20, 'dense_earth', 'silicon', 0.3),
    (20, 40, 'gravel', 'gravel', 0.2),
    (40, 60, 'soft_stone', 'soft_stone', 0.15),
    (60, 80, 'stone', 'stone', 0.12),
    (80, 100, 'dense_stone', 'dense_stone', 0.1),
    (100, 120, 'andesite', 'andesite', 0.08),
    (120, 140, 'granite', 'granite', 0.05),
    (140, 160, 'soft_matter', 'soft_matter', 0.03),
    (160, 180, 'dense_matter', 'dense_matter', 0.02),
    (180, 220, 'magma', 'magma', 0.5),
    (220, 254, 'magma', 'magma', 0.3),
    (254, 255, 'core', None, 0),
]

buildings = []

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)