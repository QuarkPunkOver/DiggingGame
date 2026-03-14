import pygame
from constants import SCREEN, SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, FONT, SMALL_FONT
from language import lang

def get_resource_color(resource):
    color_map = {
        'uranium': (57, 255, 20),
        'uranium_isotope': (0, 255, 0),
        'core': (255, 100, 100),
        'core_fragment': (255, 100, 100),
        'diamond': (185, 242, 255),
        'gold': (255, 215, 0),
        'platinum': (229, 228, 226),
        'copper': (184, 115, 51),
        'tin': (192, 192, 192),
        'iron': (139, 69, 19),
        'coal': (20, 20, 20),
        'tungsten': (80, 80, 80),
        'silicon': (100, 100, 150),
        'gravel': (128, 128, 128),
        'stone': (139, 90, 43),
        'granite': (200, 200, 200),
        'soft_matter': (150, 100, 150),
        'dense_matter': (100, 50, 100),
        'magma': (255, 140, 0),
        'surface': (34, 139, 34),
        'soil': (139, 69, 19),
        'dense_earth': (160, 82, 45),
        'soft_stone': (169, 169, 169),
        'dense_stone': (101, 67, 33),
        'andesite': (128, 128, 128),
    }
    
    for key, color in color_map.items():
        if key in resource.lower():
            return color
    
    return (255, 255, 255)

def draw_rounded_rect(surface, color, rect, radius=10):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_rounded_rect_with_border(surface, color, rect, radius=10, border_color=(100, 100, 100), border_width=2):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    pygame.draw.rect(surface, border_color, rect, border_width, border_radius=radius)

def draw_world(screen, world, player, camera_x, camera_y, buildings):
    start_x = max(0, camera_x // 16)
    start_y = max(0, camera_y // 16)
    end_x = min(world.width, (camera_x + SCREEN_WIDTH) // 16 + 1)
    end_y = min(world.depth, (camera_y + SCREEN_HEIGHT) // 16 + 1)

    darkness_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    darkness_surface.fill((0, 0, 0, 0))

    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            tile = world.get_tile(x, y)
            if tile:
                screen_x = x*16 - camera_x
                screen_y = y*16 - camera_y
                
                distance = max(abs(x - player.x), abs(y - player.y))
                in_view_range = distance <= player.view_range
                
                if in_view_range or (x, y) in player.explored_tiles:
                    if tile.dug:
                        depth_factor = y / world.depth
                        
                        if y < 100:
                            blue_value = int(200 + 55 * (y / 100))
                            color = (135, 206, min(250, blue_value))
                        elif y < 200:
                            progress = (y - 100) / 100
                            r = int(100 * progress)
                            g = int(100 * progress)
                            b = 250 - int(50 * progress)
                            color = (r, g, b)
                        else:
                            surrounding_color = get_surrounding_rock_color(world, x, y)
                            if surrounding_color:
                                color = tuple(int(c * 0.3) for c in surrounding_color)
                            else:
                                color = (10, 10, 20)
                    else:
                        color = tile.color
                    
                    rect = pygame.Rect(screen_x, screen_y, 16, 16)
                    pygame.draw.rect(screen, color, rect)
                    
                    if distance > player.view_range:
                        dark_alpha = min(200, (distance - player.view_range) * 40)
                        dark_rect = pygame.Rect(screen_x, screen_y, 16, 16)
                        pygame.draw.rect(darkness_surface, (0, 0, 0, dark_alpha), dark_rect)
                    
                    if player.digging_active and hasattr(player, 'digging_targets') and player.digging_targets:
                        for tx, ty in player.digging_targets:
                            if tx == x and ty == y:
                                progress = tile.progress / (tile.hardness * 10)
                                bar_width = 16 * progress
                                bar_rect = pygame.Rect(screen_x, screen_y, bar_width, 3)
                                pygame.draw.rect(screen, (255,255,0), bar_rect)
                    
                    if in_view_range and (x, y) not in player.explored_tiles:
                        player.explored_tiles.add((x, y))
                else:
                    dark_rect = pygame.Rect(screen_x, screen_y, 16, 16)
                    pygame.draw.rect(darkness_surface, (0, 0, 0, 255), dark_rect)

    screen.blit(darkness_surface, (0, 0))

    for building in buildings:
        if 0 <= building.x < world.width and 0 <= building.y < world.depth:
            distance = max(abs(building.x - player.x), abs(building.y - player.y))
            if distance <= player.view_range or (building.x, building.y) in player.explored_tiles:
                if building.type == 'fuel':
                    color = COLORS['fuel_station']
                elif building.type == 'shop':
                    color = COLORS['shop']
                elif building.type == 'tech':
                    color = COLORS['tech_service']
                else:
                    color = COLORS['save_point']
                
                rect = pygame.Rect(building.x*16 - camera_x, building.y*16 - camera_y, 16, 16)
                pygame.draw.rect(screen, color, rect)
                
                if building.type == 'fuel':
                    pygame.draw.circle(screen, (0,0,0), rect.center, 3)
                elif building.type == 'shop':
                    pygame.draw.rect(screen, (0,0,0), rect.inflate(-4, -4), 1)
                elif building.type == 'tech':
                    pygame.draw.line(screen, (0,0,0), rect.topleft, rect.bottomright, 2)
                    pygame.draw.line(screen, (0,0,0), rect.topright, rect.bottomleft, 2)
                elif building.type == 'save':
                    pygame.draw.rect(screen, (0,0,0), rect.inflate(-4, -4), 2)

    player_rect = pygame.Rect(player.x*16 - camera_x, player.y*16 - camera_y, 16, 16)
    
    health_percent = player.hull_strength / player.max_hull
    if health_percent > 0.5:
        color = COLORS['player']
    elif health_percent > 0.2:
        color = (255, 165, 0)
    else:
        color = (255, 0, 0)
        
    pygame.draw.rect(screen, color, player_rect)
    center = player_rect.center
    
    if player.drill_width_max > 1:
        width_indicator = player.drill_width_current * 2
        
        if player.facing == 0 or player.facing == 1:
            for i in range(-(player.drill_width_current // 2), (player.drill_width_current // 2) + 1):
                if i == 0:
                    line_color = (255, 255, 255)
                    line_width = 3
                else:
                    line_color = (200, 200, 100)
                    line_width = 1
                
                x_offset = i * 16
                start_point = (center[0] + x_offset - 8, center[1])
                end_point = (center[0] + x_offset + 8, center[1])
                pygame.draw.line(screen, line_color, start_point, end_point, line_width)
            
            for i in range(-(player.drill_width_current // 2), (player.drill_width_current // 2) + 1):
                if i == 0:
                    circle_color = (255, 255, 255)
                    circle_radius = 4
                else:
                    circle_color = (200, 200, 100)
                    circle_radius = 3
                
                x_pos = center[0] + i * 16
                pygame.draw.circle(screen, circle_color, (x_pos, center[1]), circle_radius)
                pygame.draw.circle(screen, (100, 100, 100), (x_pos, center[1]), circle_radius, 1)
        else:
            for i in range(-(player.drill_width_current // 2), (player.drill_width_current // 2) + 1):
                if i == 0:
                    line_color = (255, 255, 255)
                    line_width = 3
                else:
                    line_color = (200, 200, 100)
                    line_width = 1
                
                y_offset = i * 16
                start_point = (center[0], center[1] + y_offset - 8)
                end_point = (center[0], center[1] + y_offset + 8)
                pygame.draw.line(screen, line_color, start_point, end_point, line_width)
            
            for i in range(-(player.drill_width_current // 2), (player.drill_width_current // 2) + 1):
                if i == 0:
                    circle_color = (255, 255, 255)
                    circle_radius = 4
                else:
                    circle_color = (200, 200, 100)
                    circle_radius = 3
                
                y_pos = center[1] + i * 16
                pygame.draw.circle(screen, circle_color, (center[0], y_pos), circle_radius)
                pygame.draw.circle(screen, (100, 100, 100), (center[0], y_pos), circle_radius, 1)
    
    if player.digging_active and hasattr(player, 'digging_targets') and player.digging_targets:
        for tx, ty in player.digging_targets:
            target_x = tx*16 - camera_x + 8
            target_y = ty*16 - camera_y + 8
            pygame.draw.line(screen, (255, 100, 100), center, (target_x, target_y), 2)
            pygame.draw.circle(screen, (255, 100, 100), (target_x, target_y), 4)
    
    if player.facing == 0: 
        end = (center[0], center[1]+8)
    elif player.facing == 1: 
        end = (center[0], center[1]-8)
    elif player.facing == 2: 
        end = (center[0]-8, center[1])
    elif player.facing == 3: 
        end = (center[0]+8, center[1])
    pygame.draw.line(screen, (255,255,255), center, end, 2)

def get_surrounding_rock_color(world, x, y):
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < world.width and 0 <= ny < world.depth:
                tile = world.get_tile(nx, ny)
                if tile and not tile.dug:
                    return tile.color
    return None

def draw_simple_inventory(screen, player):
    if not player.show_inventory:
        return
    
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    panel_width = 500
    panel_height = 550
    panel_x = (SCREEN_WIDTH - panel_width) // 2
    panel_y = (SCREEN_HEIGHT - panel_height) // 2
    
    draw_rounded_rect_with_border(screen, (25, 25, 35), 
                                  pygame.Rect(panel_x, panel_y, panel_width, panel_height), 
                                  20, (80, 80, 100), 2)
    
    inner_rect = pygame.Rect(panel_x + 5, panel_y + 5, panel_width - 10, panel_height - 10)
    draw_rounded_rect(screen, (35, 35, 45), inner_rect, 15)
    
    title = pygame.font.Font(None, 42).render(lang.get('inventory'), True, (255, 215, 100))
    title_shadow = pygame.font.Font(None, 42).render(lang.get('inventory'), True, (100, 80, 30))
    title_rect = title.get_rect(center=(panel_x + panel_width//2 + 2, panel_y + 32))
    screen.blit(title_shadow, title_rect)
    title_rect = title.get_rect(center=(panel_x + panel_width//2, panel_y + 30))
    screen.blit(title, title_rect)
    
    line_y = panel_y + 65
    pygame.draw.line(screen, (80, 80, 100), (panel_x + 40, line_y), (panel_x + panel_width - 40, line_y), 2)
    pygame.draw.line(screen, (120, 120, 150), (panel_x + 40, line_y + 1), (panel_x + panel_width - 40, line_y + 1), 1)
    
    headers = [lang.get('resource'), lang.get('count')]
    header_x = panel_x + 100
    for i, header in enumerate(headers):
        text = pygame.font.Font(None, 26).render(header, True, (200, 200, 150))
        screen.blit(text, (header_x + i * 150, panel_y + 80))
    
    y_offset = panel_y + 120
    items_per_page = 8
    
    items = list(player.inventory.items())
    total_pages = max(1, (len(items) + items_per_page - 1) // items_per_page)
    current_page = (player.inventory_scroll // items_per_page) + 1
    
    if not items:
        empty_text = pygame.font.Font(None, 28).render(lang.get('inventory_empty'), True, (150, 150, 150))
        empty_rect = empty_text.get_rect(center=(panel_x + panel_width//2, panel_y + panel_height//2))
        screen.blit(empty_text, empty_rect)
    else:
        visible_items = player.get_visible_inventory()
        
        for i, (resource, count) in enumerate(visible_items):
            color = get_resource_color(resource)
            
            if i % 2 == 0:
                row_rect = pygame.Rect(panel_x + 20, y_offset + i * 40 - 5, panel_width - 40, 35)
                draw_rounded_rect(screen, (45, 45, 55), row_rect, 8)
            
            icon_rect = pygame.Rect(panel_x + 50, y_offset + i * 40, 20, 20)
            pygame.draw.rect(screen, color, icon_rect)
            pygame.draw.rect(screen, (255, 255, 255), icon_rect, 1)
            
            resource_name = lang.get(resource)
            if resource_name == resource:
                resource_name = resource.capitalize()
            
            res_text = pygame.font.Font(None, 24).render(resource_name, True, color)
            screen.blit(res_text, (panel_x + 80, y_offset + i * 40 + 2))
            
            count_bg = pygame.Rect(panel_x + 250, y_offset + i * 40, 60, 22)
            draw_rounded_rect(screen, (20, 20, 30), count_bg, 6)
            count_text = pygame.font.Font(None, 24).render(f"x{count}", True, (255, 255, 255))
            screen.blit(count_text, (panel_x + 260, y_offset + i * 40 + 2))
        
        if len(items) > items_per_page:
            page_text = pygame.font.Font(None, 20).render(f"{lang.get('page')} {current_page}/{total_pages}", True, (180, 180, 180))
            page_rect = page_text.get_rect(center=(panel_x + panel_width//2, panel_y + panel_height - 120))
            screen.blit(page_text, page_rect)
    
    total_items = len(player.inventory)
    total_count = sum(player.inventory.values())
    
    info_bg = pygame.Rect(panel_x + 50, panel_y + panel_height - 100, panel_width - 100, 40)
    draw_rounded_rect(screen, (40, 40, 50), info_bg, 10)
    
    items_text = pygame.font.Font(None, 22).render(lang.get('total_items', types=total_items, count=total_count), True, (200, 200, 200))
    items_rect = items_text.get_rect(center=(panel_x + panel_width//2, panel_y + panel_height - 85))
    screen.blit(items_text, items_rect)

    close_btn = pygame.Rect(panel_x + panel_width//2 - 60, panel_y + panel_height - 50, 120, 35)
    mouse_pos = pygame.mouse.get_pos()
    if close_btn.collidepoint(mouse_pos):
        btn_color = (120, 60, 60)
    else:
        btn_color = (80, 40, 40)
    
    draw_rounded_rect(screen, btn_color, close_btn, 10)
    pygame.draw.rect(screen, (150, 100, 100), close_btn, 2, border_radius=10)
    
    close_text = pygame.font.Font(None, 24).render(lang.get('close'), True, (255, 255, 255))
    text_rect = close_text.get_rect(center=close_btn.center)
    screen.blit(close_text, text_rect)
    
    player.inventory_close_btn = close_btn

def draw_ui(screen, player, world):
    ui_bg = pygame.Surface((230, 280), pygame.SRCALPHA)
    ui_bg.fill((0, 0, 0, 180))
    screen.blit(ui_bg, (5, 5))
    
    bar_width = 200
    bar_height = 18
    bar_x, bar_y = 15, 10
    
    fuel_percent = player.fuel / player.max_fuel
    fuel_text = SMALL_FONT.render(lang.get('fuel_ui', current=int(player.fuel), max=int(player.max_fuel)), True, (255, 255, 255))
    screen.blit(fuel_text, (bar_x, bar_y))
    
    draw_rounded_rect(screen, (60, 60, 60), (bar_x, bar_y + 15, bar_width, bar_height), 6)
    if fuel_percent > 0:
        fill_width = int(bar_width * fuel_percent)
        draw_rounded_rect(screen, (0, 200, 0), (bar_x, bar_y + 15, fill_width, bar_height), 6)

    rounded_money = round(player.money / 10) * 10
    money_text = SMALL_FONT.render(lang.get('money_ui', money=rounded_money), True, (255, 255, 255))
    screen.blit(money_text, (bar_x, bar_y + 40))

    depth_text = SMALL_FONT.render(lang.get('depth_ui', depth=player.y), True, (255, 255, 255))
    screen.blit(depth_text, (bar_x, bar_y + 60))

    hull_percent = player.hull_strength / player.max_hull
    hull_text = SMALL_FONT.render(lang.get('hull_ui', current=int(player.hull_strength), max=int(player.max_hull)), True, (255, 255, 255))
    screen.blit(hull_text, (bar_x, bar_y + 80))
    
    draw_rounded_rect(screen, (60, 60, 60), (bar_x, bar_y + 95, bar_width, bar_height), 6)
    if hull_percent > 0:
        fill_width = int(bar_width * hull_percent)
        if hull_percent > 0.5:
            hull_color = (0, 255, 0)
        elif hull_percent > 0.2:
            hull_color = (255, 165, 0)
        else:
            hull_color = (255, 0, 0)
        draw_rounded_rect(screen, hull_color, (bar_x, bar_y + 95, fill_width, bar_height), 6)

    temp = world.get_temperature(player.y)
    temp_color = (255, 255, 255)
    if temp > player.temp_resistance:
        temp_color = (255, 0, 0)
    temp_text = SMALL_FONT.render(lang.get('temp_ui', temp=int(temp), resist=int(player.temp_resistance)), True, temp_color)
    screen.blit(temp_text, (bar_x, bar_y + 120))

    width_text = SMALL_FONT.render(lang.get('drill_width_ui', current=player.drill_width_current, max=player.drill_width_max), True, (255, 255, 255))
    screen.blit(width_text, (bar_x, bar_y + 140))

    view_text = SMALL_FONT.render(lang.get('view_range_ui', range=player.view_range), True, (200, 200, 255))
    screen.blit(view_text, (bar_x, bar_y + 160))

    control_y = bar_y + 180
    control_text = SMALL_FONT.render(lang.get('width_control'), True, (200, 200, 200))
    screen.blit(control_text, (bar_x, control_y))
    
    btn_size = 25
    btn_spacing = 5
    
    minus_btn = pygame.Rect(bar_x, control_y + 20, btn_size, btn_size)
    draw_rounded_rect(screen, (150, 0, 0) if player.drill_width_current > 1 else (80, 80, 80), minus_btn, 5)
    minus_text = SMALL_FONT.render("-", True, (255, 255, 255))
    minus_x = minus_btn.x + (btn_size - minus_text.get_width()) // 2
    minus_y = minus_btn.y + (btn_size - minus_text.get_height()) // 2
    screen.blit(minus_text, (minus_x, minus_y))
    
    width_display = SMALL_FONT.render(f"{player.drill_width_current}", True, (255, 255, 255))
    screen.blit(width_display, (bar_x + btn_size + btn_spacing, control_y + 25))
    
    plus_btn = pygame.Rect(bar_x + btn_size + btn_spacing * 2 + 20, control_y + 20, btn_size, btn_size)
    draw_rounded_rect(screen, (0, 150, 0) if player.drill_width_current < player.drill_width_max else (80, 80, 80), plus_btn, 5)
    plus_text = SMALL_FONT.render("+", True, (255, 255, 255))
    plus_x = plus_btn.x + (btn_size - plus_text.get_width()) // 2
    plus_y = plus_btn.y + (btn_size - plus_text.get_height()) // 2
    screen.blit(plus_text, (plus_x, plus_y))
    
    player.width_minus_btn = minus_btn
    player.width_plus_btn = plus_btn

    hint_y = control_y + 50
    hint1 = SMALL_FONT.render(lang.get('controls'), True, (200, 200, 200))
    screen.blit(hint1, (bar_x, hint_y))
    hint2 = SMALL_FONT.render("Heigh-Ho Heigh-Ho", True, (150, 150, 150))
    screen.blit(hint2, (bar_x, hint_y + 18))

    if player.show_inventory:
        draw_simple_inventory(screen, player)

    if player.show_stats:
        stats_bg = pygame.Surface((280, 280), pygame.SRCALPHA)
        stats_bg.fill((0, 0, 0, 200))
        screen.blit(stats_bg, (SCREEN_WIDTH - 290, 5))
        
        stats_title = SMALL_FONT.render(lang.get('stats'), True, (0, 255, 255))
        screen.blit(stats_title, (SCREEN_WIDTH - 280, 10))
        
        stats_y = 35
        drill_text = SMALL_FONT.render(lang.get('drill', level=player.drill_level), True, (255, 255, 255))
        screen.blit(drill_text, (SCREEN_WIDTH - 280, stats_y))
        width_text = SMALL_FONT.render(lang.get('width', current=player.drill_width_current, max=player.drill_width_max), True, (255, 255, 255))
        screen.blit(width_text, (SCREEN_WIDTH - 280, stats_y + 20))
        fuel_text = SMALL_FONT.render(lang.get('fuel', level=player.fuel_level), True, (255, 255, 255))
        screen.blit(fuel_text, (SCREEN_WIDTH - 280, stats_y + 40))
        eff_text = SMALL_FONT.render(lang.get('efficiency_stat', level=player.efficiency_level), True, (255, 255, 255))
        screen.blit(eff_text, (SCREEN_WIDTH - 280, stats_y + 60))
        hull_text = SMALL_FONT.render(lang.get('hull_stat', level=player.hull_level), True, (255, 255, 255))
        screen.blit(hull_text, (SCREEN_WIDTH - 280, stats_y + 80))
        
        y = stats_y + 100
        if player.diamond_coating:
            diamond_text = SMALL_FONT.render("✓ Diamond Coating", True, (0, 255, 0))
            screen.blit(diamond_text, (SCREEN_WIDTH - 280, y))
            y += 20
        if player.electric_upgrade:
            electric_text = SMALL_FONT.render("✓ Electric Upgrade", True, (0, 255, 0))
            screen.blit(electric_text, (SCREEN_WIDTH - 280, y))
            y += 20
        if player.uranium_engine:
            uranium_text = SMALL_FONT.render("✓ Uranium Engine", True, (0, 255, 0))
            screen.blit(uranium_text, (SCREEN_WIDTH - 280, y))
            y += 20
        if player.titanium_drill:
            titanium_text = SMALL_FONT.render("✓ Titanium Drill", True, (0, 255, 0))
            screen.blit(titanium_text, (SCREEN_WIDTH - 280, y))
            y += 20
        if player.plasma_cutter:
            plasma_text = SMALL_FONT.render("✓ Plasma Cutter", True, (0, 255, 0))
            screen.blit(plasma_text, (SCREEN_WIDTH - 280, y))
            y += 20
        if player.neutronium_core:
            neutronium_text = SMALL_FONT.render("✓ Neutronium Core", True, (0, 255, 0))
            screen.blit(neutronium_text, (SCREEN_WIDTH - 280, y))
            y += 20