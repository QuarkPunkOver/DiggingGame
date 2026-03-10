import json
import random
from constants import INITIAL_FUEL, REPAIR_COST, MOVE_FUEL_COST, DIG_FUEL_COST, WORLD_WIDTH, SAVE_FILE
from sound import sound_manager

class Player:
    def __init__(self, x, y, load_saved=False, player_data=None):
        self.x = x
        self.y = y
        self.facing = 0
        self.fuel = INITIAL_FUEL
        self.max_fuel = INITIAL_FUEL
        self.money = 0
        self.inventory = {}
        
        self.hull_level = 1
        self.hull_strength = 200
        self.max_hull = 200
        self.temp_resistance = 200
        
        self.drill_level = 1
        self.fuel_level = 1
        self.efficiency_level = 1
        
        self.base_drill_power = 1.0
        self.drill_power = 1.0
        self.fuel_efficiency = 1.0
        
        self.digging_target = None
        self.digging_active = False
        self.auto_dig_direction = None
        self.was_digging = False
        
        self.keys_pressed = set()
        self.last_move_time = 0
        self.move_delay = 150
        
        self.continue_digging = False
        self.game_completed = False
        
        self.show_inventory = False
        self.show_stats = False
        
        if load_saved and player_data:
            self.load(player_data)
        
        self.update_stats()
    
    def update_stats(self):
        self.drill_power = self.base_drill_power * (1.0 + (self.drill_level - 1) * 0.5)
        self.max_fuel = 200 + (self.fuel_level - 1) * 75
        self.fuel_efficiency = max(0.1, 1.0 - (self.efficiency_level - 1) * 0.1)
        self.max_hull = 200 + (self.hull_level - 1) * 200
        self.temp_resistance = 200 + (self.hull_level - 1) * 700
        self.hull_strength = self.max_hull
    
    def repair(self):
        if self.money >= REPAIR_COST and self.hull_strength < self.max_hull:
            self.money -= REPAIR_COST
            self.hull_strength = self.max_hull
            return True
        return False
    
    def can_dig_tile(self, tile):
        if not tile:
            return False
        
        hardness_map = {
            'surface': 1, 'soil': 1,
            'dense_earth': 1, 'silicon': 1, 'coal': 1,
            'gravel': 2, 'copper': 2, 'tin': 2, 'soft_stone': 2,
            'stone': 3, 'iron': 3,
            'dense_stone': 4, 'andesite': 4,
            'granite': 5, 'gold': 5,
            'platinum': 6, 'tungsten': 6,
            'soft_matter': 7, 'dense_matter': 8,
            'diamond': 7, 'magma': 9,
            'core': 10, 'core_fragment': 1
        }
        
        required_level = hardness_map.get(tile.type, 10)
        return self.drill_level >= required_level
    
    def get_dig_speed(self, tile):
        if not tile:
            return 1.0
        
        speed_map = {
            'surface': 1.2, 'soil': 1.1,
            'dense_earth': 0.9, 'silicon': 0.9, 'coal': 0.9,
            'gravel': 0.7, 'copper': 0.7, 'tin': 0.7, 'soft_stone': 0.7,
            'stone': 0.5, 'iron': 0.5,
            'dense_stone': 0.4, 'andesite': 0.4,
            'granite': 0.3, 'gold': 0.3,
            'platinum': 0.25, 'tungsten': 0.25,
            'soft_matter': 0.2, 'dense_matter': 0.15,
            'diamond': 0.2, 'magma': 0.1,
            'core': 0.08, 'core_fragment': 0.08
        }
        
        base_speed = speed_map.get(tile.type, 0.5)
        level_bonus = 1.0 + (self.drill_level - 1) * 0.15
        return base_speed * level_bonus
    
    def take_damage(self, world):
        if self.y <= 0:
            return False
        
        temp = world.get_temperature(self.y)
        
        if temp > self.temp_resistance:
            damage = (temp - self.temp_resistance) / 80
            self.hull_strength -= max(1, int(damage))
            
            if self.hull_strength <= 0:
                return True
        return False
    
    def move(self, dx, dy, world):
        if self.y > 0 and self.fuel < MOVE_FUEL_COST:
            return False
        
        new_x, new_y = self.x + dx, self.y + dy
        tile = world.get_tile(new_x, new_y)
        if tile and tile.dug:
            if self.y > 0:
                self.fuel -= MOVE_FUEL_COST
                sound_manager.play('move')
            self.x, self.y = new_x, new_y
            if dx > 0: self.facing = 3
            elif dx < 0: self.facing = 2
            elif dy > 0: self.facing = 0
            elif dy < 0: self.facing = 1
            return True
        return False
    
    def try_move_or_dig(self, dx, dy, world):
        if self.move(dx, dy, world):
            self.auto_dig_direction = None
            self.continue_digging = False
            return True
        else:
            if dx > 0: self.facing = 3
            elif dx < 0: self.facing = 2
            elif dy > 0: self.facing = 0
            elif dy < 0: self.facing = 1
            
            tx, ty = self.x, self.y
            if self.facing == 0: ty += 1
            elif self.facing == 1: ty -= 1
            elif self.facing == 2: tx -= 1
            elif self.facing == 3: tx += 1
            
            tile = world.get_tile(tx, ty)
            if tile and tile.is_solid() and self.fuel > 0 and self.hull_strength > 0:
                if self.can_dig_tile(tile):
                    if not self.digging_active:
                        self.start_digging(world)
                        if self.digging_active:
                            self.auto_dig_direction = (dx, dy)
                            self.continue_digging = True
            return False
    
    def start_digging(self, world):
        tx, ty = self.x, self.y
        if self.facing == 0: ty += 1
        elif self.facing == 1: ty -= 1
        elif self.facing == 2: tx -= 1
        elif self.facing == 3: tx += 1

        tile = world.get_tile(tx, ty)
        if tile and tile.is_solid() and self.fuel > 0 and self.hull_strength > 0:
            if self.can_dig_tile(tile):
                self.digging_target = (tx, ty)
                self.digging_active = True
                self.was_digging = True
                sound_manager.play('dig')
            else:
                self.digging_active = False
                self.digging_target = None
                self.was_digging = False
        else:
            self.digging_active = False
            self.digging_target = None
            self.was_digging = False
    
    def stop_digging(self):
        self.digging_active = False
        self.digging_target = None
        self.auto_dig_direction = None
        self.continue_digging = False
        self.was_digging = False
    
    def update_digging(self, world):
        if not self.digging_active or not self.digging_target:
            if self.was_digging:
                self.was_digging = False
            return None

        tx, ty = self.digging_target
        dx, dy = tx - self.x, ty - self.y
        
        if abs(dx) + abs(dy) != 1:
            self.stop_digging()
            return None

        if (dx == 1 and self.facing != 3) or (dx == -1 and self.facing != 2) or \
           (dy == 1 and self.facing != 0) or (dy == -1 and self.facing != 1):
            self.stop_digging()
            return None

        if self.fuel <= 0 or self.hull_strength <= 0:
            self.stop_digging()
            return None

        tile = world.get_tile(tx, ty)
        if not tile or not tile.is_solid():
            if self.auto_dig_direction:
                adx, ady = self.auto_dig_direction
                if (adx, ady) == (dx, dy):
                    if self.move(adx, ady, world):
                        self.auto_dig_direction = None
                        self.digging_active = False
                        self.digging_target = None
                        if self.continue_digging and self.keys_pressed:
                            self.try_move_or_dig(adx, ady, world)
            else:
                self.stop_digging()
            return None

        speed_multiplier = self.get_dig_speed(tile)
        effective_power = self.drill_power * speed_multiplier
        
        self.fuel -= DIG_FUEL_COST * self.fuel_efficiency
        if self.fuel < 0:
            self.fuel = 0

        if random.random() < 0.1:
            temp = world.get_temperature(self.y)
            if temp > self.temp_resistance:
                damage = (temp - self.temp_resistance) / 50
                self.hull_strength -= max(1, int(damage))

        resource = world.dig(tx, ty, effective_power)
        if resource:
            self.inventory[resource] = self.inventory.get(resource, 0) + 1
            sound_manager.play('collect')
            
            if self.auto_dig_direction:
                adx, ady = self.auto_dig_direction
                if (adx, ady) == (dx, dy):
                    if self.move(adx, ady, world):
                        self.auto_dig_direction = None
                        self.digging_active = False
                        self.digging_target = None
                        if self.continue_digging and self.keys_pressed:
                            self.try_move_or_dig(adx, ady, world)
                        return resource
            self.stop_digging()
            return resource
        return None
    
    def evacuate(self):
        self.inventory.clear()
        self.money = 0
        self.x = WORLD_WIDTH // 2
        self.y = 0
        self.fuel = self.max_fuel
        self.hull_strength = self.max_hull
        self.stop_digging()
        sound_manager.play('evacuation')
        return True
    
    def get_save_data(self):
        return {
            'x': self.x,
            'y': self.y,
            'facing': self.facing,
            'fuel': self.fuel,
            'max_fuel': self.max_fuel,
            'money': self.money,
            'inventory': self.inventory,
            'hull_level': self.hull_level,
            'hull_strength': self.hull_strength,
            'max_hull': self.max_hull,
            'temp_resistance': self.temp_resistance,
            'drill_level': self.drill_level,
            'fuel_level': self.fuel_level,
            'efficiency_level': self.efficiency_level,
            'drill_power': self.drill_power,
            'fuel_efficiency': self.fuel_efficiency,
            'game_completed': self.game_completed
        }
    
    def load(self, data):
        self.x = data['x']
        self.y = data['y']
        self.facing = data['facing']
        self.fuel = data['fuel']
        self.max_fuel = data['max_fuel']
        self.money = data['money']
        self.inventory = data['inventory']
        self.hull_level = data['hull_level']
        self.hull_strength = data['hull_strength']
        self.max_hull = data['max_hull']
        self.temp_resistance = data['temp_resistance']
        self.drill_level = data['drill_level']
        self.fuel_level = data['fuel_level']
        self.efficiency_level = data['efficiency_level']
        self.drill_power = data['drill_power']
        self.fuel_efficiency = data['fuel_efficiency']
        self.game_completed = data.get('game_completed', False)
    
    def save_game(self, world):
        save_data = {
            'player': self.get_save_data(),
            'world': world.get_save_data()
        }
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump(save_data, f)
            sound_manager.play('save')
            return True
        except:
            return False
    
    def load_game(self):
        try:
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)
            return data
        except:
            return None