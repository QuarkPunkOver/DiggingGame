import pygame
from constants import TILE_SIZE, COLORS

class Building:
    def __init__(self, x, y, btype):
        self.x = x
        self.y = y
        self.type = btype
        self.rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def interact(self, player):
        if self.type == 'fuel':
            return "fuel_menu"
        elif self.type == 'shop':
            return "shop_menu"
        elif self.type == 'tech':
            return "tech_menu"
        elif self.type == 'save':
            return "save_menu"
        return None