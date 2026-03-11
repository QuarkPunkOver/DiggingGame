import random
import json
from tile import Tile
from constants import LAYERS, WORLD_WIDTH, WORLD_DEPTH, SURFACE_TEMP, CORE_TEMP

class World:
    def __init__(self, width, depth, load_saved=False, world_data=None):
        self.width = width
        self.depth = depth
        self.tiles = [[None for _ in range(width)] for _ in range(depth)]
        
        if load_saved and world_data:
            self.load(world_data)
        else:
            self.generate()
    
    def generate(self):
        for y in range(self.depth):
            for x in range(self.width):
                tile_type = None
                for start, end, base, ore, chance in LAYERS:
                    if start <= y < end:
                        if ore and random.random() < chance:
                            if base == 'dense_earth':
                                r = random.random()
                                if r < 0.25:
                                    tile_type = 'coal'
                                elif r < 0.60:
                                    tile_type = 'silicon'
                                else:
                                    tile_type = base
                            elif base == 'gravel':
                                r = random.random()
                                if r < 0.20:
                                    tile_type = 'coal'
                                elif r < 0.55:
                                    tile_type = 'silicon'
                                elif r < 0.80:
                                    tile_type = 'copper'
                                else:
                                    tile_type = base
                            elif base == 'soft_stone':
                                r = random.random()
                                if r < 0.40:
                                    tile_type = 'copper'
                                elif r < 0.70:
                                    tile_type = 'tin'
                                elif r < 0.80:
                                    tile_type = 'coal'
                                else:
                                    tile_type = base
                            elif base == 'stone':
                                r = random.random()
                                if r < 0.30:
                                    tile_type = 'iron'
                                elif r < 0.50:
                                    tile_type = 'copper'
                                elif r < 0.70:
                                    tile_type = 'tin'
                                elif r < 0.85:
                                    tile_type = 'coal'
                                elif r < 0.95:
                                    if random.random() < 0.1:
                                        tile_type = 'uranium'
                                    else:
                                        tile_type = base
                                else:
                                    tile_type = base
                            elif base == 'dense_stone':
                                r = random.random()
                                if r < 0.40:
                                    tile_type = 'iron'
                                elif r < 0.65:
                                    tile_type = 'gold'
                                elif r < 0.80:
                                    tile_type = 'coal'
                                elif r < 0.95:
                                    if random.random() < 0.15: 
                                        tile_type = 'uranium'
                                    else:
                                        tile_type = base
                                else:
                                    tile_type = base
                            elif base == 'andesite':
                                r = random.random()
                                if r < 0.30:
                                    tile_type = 'gold'
                                elif r < 0.55:
                                    tile_type = 'platinum'
                                elif r < 0.75:
                                    tile_type = 'tungsten'
                                elif r < 0.85:
                                    tile_type = 'coal'
                                elif r < 0.97:
                                    if random.random() < 0.5:
                                        tile_type = 'uranium'
                                    else:
                                        tile_type = 'uranium_isotope'
                                else:
                                    tile_type = base
                            elif base == 'granite':
                                r = random.random()
                                if r < 0.30:
                                    tile_type = 'tungsten'
                                elif r < 0.55:
                                    tile_type = 'platinum'
                                elif r < 0.75:
                                    tile_type = 'diamond'
                                elif r < 0.85:
                                    tile_type = 'coal'
                                elif r < 0.97:
                                    if random.random() < 0.3:
                                        tile_type = 'uranium'
                                    else:
                                        tile_type = 'uranium_isotope'
                                else:
                                    tile_type = base
                            elif base == 'soft_matter':
                                tile_type = 'soft_matter'
                            elif base == 'dense_matter':
                                tile_type = 'dense_matter'
                            elif base == 'magma':
                                tile_type = 'magma'
                            else:
                                tile_type = ore
                        else:
                            tile_type = base
                        break
                if tile_type is None:
                    tile_type = 'dense_matter'
                self.tiles[y][x] = Tile(tile_type)
        
        for x in range(self.width):
            self.tiles[0][x].dug = True
    
    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.depth:
            return self.tiles[y][x]
        return None
    
    def dig(self, x, y, power):
        tile = self.get_tile(x, y)
        if tile and tile.is_solid():
            tile.progress += power
            if tile.progress >= tile.hardness * 10:
                tile.dug = True
                return tile.resource
        return None
    
    def get_temperature(self, y):
        if y <= 0:
            return SURFACE_TEMP
        progress = y / (self.depth - 1)
        temp = SURFACE_TEMP + (CORE_TEMP - SURFACE_TEMP) * (progress ** 1.5)
        return temp
    
    def get_save_data(self):
        world_data = []
        for y in range(self.depth):
            row = []
            for x in range(self.width):
                tile = self.tiles[y][x]
                row.append({
                    'type': tile.type,
                    'dug': tile.dug,
                    'progress': tile.progress
                })
            world_data.append(row)
        return world_data
    
    def load(self, world_data):
        for y in range(self.depth):
            for x in range(self.width):
                tile_data = world_data[y][x]
                self.tiles[y][x] = Tile(tile_data['type'])
                self.tiles[y][x].dug = tile_data['dug']
                self.tiles[y][x].progress = tile_data['progress']