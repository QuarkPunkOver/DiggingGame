from constants import TILE_TYPES

class Tile:
    def __init__(self, tile_type):
        self.type = tile_type
        self.hardness = TILE_TYPES[tile_type]['hardness']
        self.resource = TILE_TYPES[tile_type]['resource']
        self.color = TILE_TYPES[tile_type]['color']
        self.dug = False
        self.progress = 0.0

    def is_solid(self):
        return not self.dug