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
        self.drill_width_max = 1
        self.drill_width_current = 1
        self.fuel_level = 1
        self.efficiency_level = 1
        
        self.speed_level = 1
        self.max_speed_level = 10
        self.speed_multiplier = 1.0
        
        self.diamond_coating = False
        self.electric_upgrade = False
        self.uranium_engine = False
        self.titanium_drill = False
        self.plasma_cutter = False
        self.neutronium_core = False
        
        self.base_drill_power = 1.0
        self.drill_power = 1.0
        self.fuel_efficiency = 1.0
        
        self.digging_targets = []
        self.digging_active = False
        self.auto_dig_direction = None
        self.was_digging = False
        self.target_progress = {}
        
        self.keys_pressed = set()
        self.last_move_time = 0
        self.move_delay = 150
        self.empty_move_delay = 50
        self.min_move_delay = 30
        
        self.continue_digging = False
        self.game_completed = False
        
        self.show_inventory = False
        self.show_stats = False
        
        self.current_direction = (0, 1)
        
        self.width_minus_btn = None
        self.width_plus_btn = None
        
        self.view_range = 5
        self.max_view_range = 25
        self.explored_tiles = set()
        
        self.inventory_scroll = 0
        self.inventory_items_per_page = 8
        self.max_inventory_scroll = 0
        
        if load_saved and player_data:
            self.load(player_data)
        
        self.update_stats()
        print(f"[INIT] Drill width: {self.drill_width_current}, Max: {self.drill_width_max}")
    
    def update_stats(self):
        self.drill_power = self.base_drill_power * (1.0 + (self.drill_level - 1) * 0.5)
        self.max_fuel = 200 + (self.fuel_level - 1) * 75
        self.fuel_efficiency = max(0.1, 1.0 - (self.efficiency_level - 1) * 0.1)
        self.max_hull = 200 + (self.hull_level - 1) * 200
        self.temp_resistance = 200 + (self.hull_level - 1) * 700
        self.hull_strength = self.max_hull
        
        self.speed_multiplier = 1.0 + (self.speed_level - 1) * 0.15
        
        if self.diamond_coating:
            self.drill_power *= 1.66
        
        if self.electric_upgrade:
            self.drill_power *= 1.1
            self.fuel_efficiency *= 0.9
            self.speed_multiplier *= 1.1
        
        if self.uranium_engine:
            self.drill_power *= 1.5
            self.fuel_efficiency *= 0.8
            self.speed_multiplier *= 1.15
        
        if self.titanium_drill:
            self.drill_power *= 1.3
            self.fuel_efficiency *= 0.85
            self.speed_multiplier *= 1.1
        
        if self.plasma_cutter:
            self.drill_power *= 2.0
            self.fuel_efficiency *= 0.7
            self.temp_resistance += 500
            self.speed_multiplier *= 1.2
        
        if self.neutronium_core:
            self.drill_power *= 3.0
            self.fuel_efficiency *= 0.5
            self.max_fuel *= 1.5
            self.temp_resistance += 1000
            self.speed_multiplier *= 1.3
        
        if self.drill_width_max > 11:
            self.drill_width_max = 11
        
        if self.drill_width_current > self.drill_width_max:
            self.drill_width_current = self.drill_width_max
        
        print(f"[STATS] Drill power: {self.drill_power:.2f}, Speed mult: {self.speed_multiplier:.2f}")
    
    def cheat_rocketman(self):
        cheat_items = {
            'copper': 100, 'iron': 80, 'gold': 50, 'coal': 100,
            'diamond': 30, 'platinum': 40, 'tungsten': 50,
            'uranium': 60, 'uranium_isotope': 30, 'core_fragment': 10,
            'dense_matter': 20, 'soft_matter': 20, 'silicon': 50,
            'tin': 50, 'gravel': 100, 'stone': 100, 'granite': 50
        }
        
        for item, count in cheat_items.items():
            self.inventory[item] = self.inventory.get(item, 0) + count
        
        self.money += 50000
        self.hull_strength = self.max_hull
        self.fuel = self.max_fuel
        self.update_stats()
        print("[CHEAT] ROCKETMAN activated! All resources added!")
        return True
    
    def upgrade_speed(self):
        if self.speed_level < self.max_speed_level:
            cost = self.get_speed_upgrade_cost()
            if self.money >= cost:
                self.money -= cost
                self.speed_level += 1
                self.update_stats()
                sound_manager.play('upgrade')
                return True
        return False
    
    def get_speed_upgrade_cost(self):
        if self.speed_level == 1:
            return 300
        elif self.speed_level == 2:
            return 500
        elif self.speed_level == 3:
            return 800
        elif self.speed_level == 4:
            return 1200
        elif self.speed_level == 5:
            return 1800
        elif self.speed_level == 6:
            return 2500
        elif self.speed_level == 7:
            return 3500
        elif self.speed_level == 8:
            return 5000
        elif self.speed_level == 9:
            return 7000
        return 0
    
    def can_upgrade_speed(self):
        return self.speed_level < self.max_speed_level
    
    def upgrade_view_range(self):
        if self.view_range < self.max_view_range:
            self.view_range = min(self.view_range + 5, self.max_view_range)
            return True
        return False
    
    def get_view_range_cost(self):
        if self.view_range == 5:
            return 500
        elif self.view_range == 10:
            return 1000
        elif self.view_range == 15:
            return 2000
        elif self.view_range == 20:
            return 3000
        return 0
    
    def can_upgrade_view_range(self):
        return self.view_range < self.max_view_range
    
    def apply_diamond_coating(self):
        if not self.diamond_coating and self.inventory.get('diamond', 0) >= 10 and self.money >= 1000:
            self.inventory['diamond'] -= 10
            self.money -= 1000
            self.diamond_coating = True
            self.update_stats()
            sound_manager.play('upgrade')
            return True
        return False
    
    def apply_electric_upgrade(self):
        if not self.electric_upgrade and self.inventory.get('gold', 0) >= 20 and self.money >= 500:
            self.inventory['gold'] -= 20
            self.money -= 500
            self.electric_upgrade = True
            self.update_stats()
            sound_manager.play('upgrade')
            return True
        return False
    
    def apply_uranium_engine(self):
        if not self.uranium_engine and self.inventory.get('uranium', 0) >= 50 and self.inventory.get('tungsten', 0) >= 30 and self.money >= 5000:
            self.inventory['uranium'] -= 50
            self.inventory['tungsten'] -= 30
            self.money -= 5000
            self.uranium_engine = True
            self.update_stats()
            sound_manager.play('upgrade')
            return True
        return False
    
    def apply_titanium_drill(self):
        if not self.titanium_drill and self.inventory.get('tungsten', 0) >= 40 and self.inventory.get('platinum', 0) >= 20 and self.money >= 8000:
            self.inventory['tungsten'] -= 40
            self.inventory['platinum'] -= 20
            self.money -= 8000
            self.titanium_drill = True
            self.update_stats()
            sound_manager.play('upgrade')
            return True
        return False
    
    def apply_plasma_cutter(self):
        if not self.plasma_cutter and self.inventory.get('uranium_isotope', 0) >= 30 and self.inventory.get('diamond', 0) >= 25 and self.money >= 15000:
            self.inventory['uranium_isotope'] -= 30
            self.inventory['diamond'] -= 25
            self.money -= 15000
            self.plasma_cutter = True
            self.update_stats()
            sound_manager.play('upgrade')
            return True
        return False
    
    def apply_neutronium_core(self):
        if not self.neutronium_core and self.inventory.get('core_fragment', 0) >= 5 and self.inventory.get('dense_matter', 0) >= 50 and self.money >= 50000:
            self.inventory['core_fragment'] -= 5
            self.inventory['dense_matter'] -= 50
            self.money -= 50000
            self.neutronium_core = True
            self.update_stats()
            sound_manager.play('upgrade')
            return True
        return False
    
    def decrease_width(self):
        if self.drill_width_current > 1:
            self.drill_width_current -= 2
            sound_manager.play('menu_click')
            print(f"[WIDTH] Decreased to: {self.drill_width_current}")
            return True
        return False
    
    def increase_width(self):
        if self.drill_width_current < self.drill_width_max:
            self.drill_width_current += 2
            sound_manager.play('menu_click')
            print(f"[WIDTH] Increased to: {self.drill_width_current}")
            return True
        return False
    
    def can_upgrade_width(self):
        return self.drill_width_max < 11
    
    def get_width_cost(self):
        if self.drill_width_max == 1:
            return 500
        elif self.drill_width_max == 3:
            return 1000
        elif self.drill_width_max == 5:
            return 2000
        elif self.drill_width_max == 7:
            return 3000
        elif self.drill_width_max == 9:
            return 5000
        return 0
    
    def upgrade_width(self):
        cost = self.get_width_cost()
        if self.can_upgrade_width() and self.money >= cost:
            self.money -= cost
            self.drill_width_max += 2
            if self.drill_width_max > 11:
                self.drill_width_max = 11
            self.drill_width_current = self.drill_width_max
            print(f"[UPGRADE] Width upgraded to max: {self.drill_width_max}")
            return True
        return False
    
    def get_dig_positions(self):
        dx, dy = self.current_direction
        positions = []
        half = self.drill_width_current // 2
        
        if dx == 0 and dy == 1:
            for offset in range(-half, half + 1):
                positions.append((self.x + offset, self.y + 1))
        elif dx == 0 and dy == -1:
            for offset in range(-half, half + 1):
                positions.append((self.x + offset, self.y - 1))
        elif dx == -1 and dy == 0:
            for offset in range(-half, half + 1):
                positions.append((self.x - 1, self.y + offset))
        elif dx == 1 and dy == 0:
            for offset in range(-half, half + 1):
                positions.append((self.x + 1, self.y + offset))
        
        return positions
    
    def get_current_move_delay(self, world):
        if self.digging_active:
            base_delay = self.move_delay
        else:
            dx, dy = self.current_direction
            tx, ty = self.x + dx, self.y + dy
            tile = world.get_tile(tx, ty)
            
            if not tile or tile.dug or tx < 0 or tx >= world.width or ty < 0 or ty >= world.depth:
                base_delay = self.empty_move_delay
            else:
                base_delay = self.move_delay
        
        adjusted_delay = base_delay / self.speed_multiplier
        return max(self.min_move_delay, int(adjusted_delay))
    
    def set_direction(self, dx, dy):
        self.current_direction = (dx, dy)
        if dx > 0:
            self.facing = 3
        elif dx < 0:
            self.facing = 2
        elif dy > 0:
            self.facing = 0
        elif dy < 0:
            self.facing = 1
    
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
            'surface': 1, 'soil': 1, 'dense_earth': 1, 'silicon': 1, 'coal': 1,
            'gravel': 1, 'copper': 1, 'tin': 1, 'soft_stone': 1,
            'stone': 2, 'iron': 2, 'dense_stone': 2, 'andesite': 2,
            'granite': 2, 'gold': 2, 'platinum': 3, 'tungsten': 3,
            'diamond': 3, 'uranium': 4, 'uranium_isotope': 5,
            'soft_matter': 4, 'dense_matter': 5, 'magma': 6,
            'core': 10, 'core_fragment': 1
        }
        
        required_level = hardness_map.get(tile.type, 10)
        return self.drill_level >= required_level
    
    def get_dig_speed(self, tile):
        if not tile:
            return 1.0
        
        speed_map = {
            'surface': 1.2, 'soil': 1.2, 'dense_earth': 1.1, 'silicon': 1.1, 'coal': 1.1,
            'gravel': 1.1, 'copper': 1.1, 'tin': 1.1, 'soft_stone': 1.1,
            'stone': 0.9, 'iron': 0.9, 'dense_stone': 0.9, 'andesite': 0.9,
            'granite': 0.9, 'gold': 0.9, 'platinum': 0.7, 'tungsten': 0.7,
            'diamond': 0.7, 'uranium': 0.5, 'uranium_isotope': 0.4,
            'soft_matter': 0.5, 'dense_matter': 0.4, 'magma': 0.2,
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
            
            for y_offset in range(-self.view_range, self.view_range + 1):
                for x_offset in range(-self.view_range, self.view_range + 1):
                    ex, ey = self.x + x_offset, self.y + y_offset
                    if 0 <= ex < world.width and 0 <= ey < world.depth:
                        self.explored_tiles.add((ex, ey))
            
            return True
        return False
    
    def try_move_or_dig(self, dx, dy, world):
        self.set_direction(dx, dy)
        
        if self.move(dx, dy, world):
            self.auto_dig_direction = None
            self.continue_digging = False
            if self.digging_active:
                self.stop_digging()
            return True
        else:
            if not self.digging_active:
                self.start_digging(world)
                if self.digging_active:
                    self.auto_dig_direction = (dx, dy)
                    self.continue_digging = True
            return False
    
    def start_digging(self, world):
        positions = self.get_dig_positions()
        self.digging_targets = []
        self.target_progress = {}
        
        for tx, ty in positions:
            if tx < 0 or tx >= world.width or ty < 0 or ty >= world.depth:
                continue
            
            tile = world.get_tile(tx, ty)
            if tile and tile.is_solid():
                if self.can_dig_tile(tile):
                    self.digging_targets.append((tx, ty))
                    self.target_progress[(tx, ty)] = 0
        
        if self.digging_targets:
            self.digging_active = True
            self.was_digging = True
            sound_manager.play('dig')
        else:
            self.digging_active = False
            self.was_digging = False
    
    def stop_digging(self):
        self.digging_active = False
        self.digging_targets = []
        self.target_progress = {}
        self.auto_dig_direction = None
        self.continue_digging = False
        self.was_digging = False
    
    def update_digging(self, world):
        if not self.digging_active:
            return None

        if self.fuel <= 0 or self.hull_strength <= 0:
            self.stop_digging()
            return None

        current_positions = self.get_dig_positions()
        
        all_targets_in_zone = []
        for tx, ty in current_positions:
            if tx < 0 or tx >= world.width or ty < 0 or ty >= world.depth:
                continue
                
            tile = world.get_tile(tx, ty)
            if tile and tile.is_solid() and not tile.dug:
                if self.can_dig_tile(tile):
                    all_targets_in_zone.append((tx, ty))
        
        if not all_targets_in_zone:
            self.stop_digging()
            return None
        
        old_targets = self.digging_targets.copy()
        self.digging_targets = all_targets_in_zone
        
        for target in self.digging_targets:
            if target not in self.target_progress:
                self.target_progress[target] = 0
        
        targets_to_remove = []
        for target in self.target_progress:
            if target not in self.digging_targets:
                targets_to_remove.append(target)
        
        for target in targets_to_remove:
            del self.target_progress[target]
        
        resources_collected = []
        fuel_consumed = 0
        
        total_progress_needed = 0
        tile_data = {}
        for tx, ty in self.digging_targets:
            tile = world.get_tile(tx, ty)
            if tile:
                needed = tile.hardness * 10 - self.target_progress.get((tx, ty), 0)
                if needed > 0:
                    total_progress_needed += needed
                    tile_data[(tx, ty)] = tile
        
        if total_progress_needed <= 0:
            self.stop_digging()
            return None
        
        for tx, ty in self.digging_targets:
            if (tx, ty) not in tile_data:
                continue
                
            tile = tile_data[(tx, ty)]
            
            needed = tile.hardness * 10 - self.target_progress.get((tx, ty), 0)
            if needed <= 0:
                continue
            
            progress_share = needed / total_progress_needed
            
            power = self.drill_power * self.get_dig_speed(tile)
            
            progress_added = power * progress_share
            
            self.target_progress[(tx, ty)] = self.target_progress.get((tx, ty), 0) + progress_added
            
            tile.progress = self.target_progress[(tx, ty)]
            
            fuel_consumed += (DIG_FUEL_COST * self.fuel_efficiency) * progress_share
        
        self.fuel -= fuel_consumed
        if self.fuel < 0:
            self.fuel = 0
        
        targets_to_dig = list(tile_data.keys())
        for tx, ty in targets_to_dig:
            tile = world.get_tile(tx, ty)
            if tile and self.target_progress.get((tx, ty), 0) >= tile.hardness * 10:
                tile.dug = True
                if tile.resource:
                    self.inventory[tile.resource] = self.inventory.get(tile.resource, 0) + 1
                    resources_collected.append(tile.resource)
                
                self.explored_tiles.add((tx, ty))
                
                if (tx, ty) in self.digging_targets:
                    self.digging_targets.remove((tx, ty))
                if (tx, ty) in self.target_progress:
                    del self.target_progress[(tx, ty)]
        
        if random.random() < 0.1 * len(targets_to_dig):
            temp = world.get_temperature(self.y)
            if temp > self.temp_resistance:
                damage = (temp - self.temp_resistance) / 50
                self.hull_strength -= max(1, int(damage))
        
        if resources_collected:
            sound_manager.play('collect')
        
        if not self.digging_targets:
            self.stop_digging()
        
        return resources_collected if resources_collected else None
    
    def scroll_inventory(self, direction):
        items = list(self.inventory.items())
        if not items:
            return
        
        self.max_inventory_scroll = max(0, len(items) - self.inventory_items_per_page)
        self.inventory_scroll += direction
        
        if self.inventory_scroll < 0:
            self.inventory_scroll = 0
        elif self.inventory_scroll > self.max_inventory_scroll:
            self.inventory_scroll = self.max_inventory_scroll
        
        sound_manager.play('menu_click')
    
    def get_visible_inventory(self):
        items = list(self.inventory.items())
        start = self.inventory_scroll
        end = start + self.inventory_items_per_page
        return items[start:end]
    
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
            'current_direction': self.current_direction,
            'fuel': self.fuel,
            'max_fuel': self.max_fuel,
            'money': self.money,
            'inventory': self.inventory,
            'hull_level': self.hull_level,
            'hull_strength': self.hull_strength,
            'max_hull': self.max_hull,
            'temp_resistance': self.temp_resistance,
            'drill_level': self.drill_level,
            'drill_width_max': self.drill_width_max,
            'drill_width_current': self.drill_width_current,
            'fuel_level': self.fuel_level,
            'efficiency_level': self.efficiency_level,
            'drill_power': self.drill_power,
            'fuel_efficiency': self.fuel_efficiency,
            'game_completed': self.game_completed,
            'diamond_coating': self.diamond_coating,
            'electric_upgrade': self.electric_upgrade,
            'uranium_engine': self.uranium_engine,
            'titanium_drill': self.titanium_drill,
            'plasma_cutter': self.plasma_cutter,
            'neutronium_core': self.neutronium_core,
            'view_range': self.view_range,
            'explored_tiles': list(self.explored_tiles),
            'speed_level': self.speed_level
        }
    
    def load(self, data):
        self.x = data['x']
        self.y = data['y']
        self.facing = data['facing']
        self.current_direction = data.get('current_direction', (0, 1))
        self.fuel = data['fuel']
        self.max_fuel = data['max_fuel']
        self.money = data['money']
        self.inventory = data['inventory']
        self.hull_level = data['hull_level']
        self.hull_strength = data['hull_strength']
        self.max_hull = data['max_hull']
        self.temp_resistance = data['temp_resistance']
        self.drill_level = data['drill_level']
        self.drill_width_max = data.get('drill_width_max', 1)
        self.drill_width_current = data.get('drill_width_current', self.drill_width_max)
        self.fuel_level = data['fuel_level']
        self.efficiency_level = data['efficiency_level']
        self.drill_power = data['drill_power']
        self.fuel_efficiency = data['fuel_efficiency']
        self.game_completed = data.get('game_completed', False)
        self.diamond_coating = data.get('diamond_coating', False)
        self.electric_upgrade = data.get('electric_upgrade', False)
        self.uranium_engine = data.get('uranium_engine', False)
        self.titanium_drill = data.get('titanium_drill', False)
        self.plasma_cutter = data.get('plasma_cutter', False)
        self.neutronium_core = data.get('neutronium_core', False)
        self.view_range = data.get('view_range', 5)
        explored = data.get('explored_tiles', [])
        self.explored_tiles = set(tuple(coord) for coord in explored)
        self.speed_level = data.get('speed_level', 1)
    
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