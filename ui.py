import pygame
from constants import SCREEN, SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, FONT, SMALL_FONT

def draw_rounded_rect(surface, color, rect, radius=10):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_world(screen, world, player, camera_x, camera_y, buildings):
    start_x = max(0, camera_x // 16)
    start_y = max(0, camera_y // 16)
    end_x = min(world.width, (camera_x + SCREEN_WIDTH) // 16 + 1)
    end_y = min(world.depth, (camera_y + SCREEN_HEIGHT) // 16 + 1)

    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            tile = world.get_tile(x, y)
            if tile:
                color = COLORS['air'] if tile.dug else tile.color
                rect = pygame.Rect(x*16 - camera_x, y*16 - camera_y, 16, 16)
                pygame.draw.rect(screen, color, rect)
                if player.digging_target == (x, y) and player.digging_active:
                    progress = tile.progress / (tile.hardness * 10)
                    bar_width = 16 * progress
                    bar_rect = pygame.Rect(x*16 - camera_x, y*16 - camera_y, bar_width, 3)
                    pygame.draw.rect(screen, (255,255,0), bar_rect)

    for building in buildings:
        if 0 <= building.x < world.width and 0 <= building.y < world.depth:
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
    if player.facing == 0: 
        end = (center[0], center[1]+8)
    elif player.facing == 1: 
        end = (center[0], center[1]-8)
    elif player.facing == 2: 
        end = (center[0]-8, center[1])
    elif player.facing == 3: 
        end = (center[0]+8, center[1])
    pygame.draw.line(screen, (255,255,255), center, end, 2)

def draw_ui(screen, player, world):

    ui_bg = pygame.Surface((230, 180), pygame.SRCALPHA)
    ui_bg.fill((0, 0, 0, 180))
    screen.blit(ui_bg, (5, 5))
    
    bar_width = 200
    bar_height = 18
    bar_x, bar_y = 15, 10
    
    fuel_percent = player.fuel / player.max_fuel
    fuel_text = SMALL_FONT.render(f"Fuel: {int(player.fuel)}/{player.max_fuel}", True, (255, 255, 255))
    screen.blit(fuel_text, (bar_x, bar_y))
    
    draw_rounded_rect(screen, (60, 60, 60), (bar_x, bar_y + 15, bar_width, bar_height), 6)
    if fuel_percent > 0:
        fill_width = int(bar_width * fuel_percent)
        draw_rounded_rect(screen, (0, 200, 0), (bar_x, bar_y + 15, fill_width, bar_height), 6)

    money_text = SMALL_FONT.render(f"Money: ${player.money}", True, (255, 255, 255))
    screen.blit(money_text, (bar_x, bar_y + 40))

    depth_text = SMALL_FONT.render(f"Depth: {player.y}", True, (255, 255, 255))
    screen.blit(depth_text, (bar_x, bar_y + 65))

    hull_percent = player.hull_strength / player.max_hull
    hull_text = SMALL_FONT.render(f"Hull: {int(player.hull_strength)}/{player.max_hull}", True, (255, 255, 255))
    screen.blit(hull_text, (bar_x, bar_y + 90))
    
    draw_rounded_rect(screen, (60, 60, 60), (bar_x, bar_y + 105, bar_width, bar_height), 6)
    if hull_percent > 0:
        fill_width = int(bar_width * hull_percent)
        if hull_percent > 0.5:
            hull_color = (0, 255, 0)
        elif hull_percent > 0.2:
            hull_color = (255, 165, 0)
        else:
            hull_color = (255, 0, 0)
        draw_rounded_rect(screen, hull_color, (bar_x, bar_y + 105, fill_width, bar_height), 6)

    temp = world.get_temperature(player.y)
    temp_color = (255, 255, 255)
    if temp > player.temp_resistance:
        temp_color = (255, 0, 0)
    temp_text = SMALL_FONT.render(f"Temp: {int(temp)}°C / {int(player.temp_resistance)}°C", True, temp_color)
    screen.blit(temp_text, (bar_x, bar_y + 135))

    hint_y = bar_y + 160
    hint1 = SMALL_FONT.render("I-inv | U-stats | E-interact", True, (200, 200, 200))
    screen.blit(hint1, (bar_x, hint_y))

    if player.show_inventory:
        inv_bg = pygame.Surface((280, 350), pygame.SRCALPHA)
        inv_bg.fill((0, 0, 0, 200))
        screen.blit(inv_bg, (SCREEN_WIDTH - 290, 100))
        
        inv_title = FONT.render("INVENTORY", True, (255, 255, 0))
        screen.blit(inv_title, (SCREEN_WIDTH - 280, 110))
        
        y_offset = 150
        i = 0
        for res, count in player.inventory.items():
            if i < 10:
                text = SMALL_FONT.render(f"{res}: {count}", True, (255, 255, 255))
                screen.blit(text, (SCREEN_WIDTH - 280, y_offset + i*25))
                i += 1

    if player.show_stats:
        stats_bg = pygame.Surface((200, 120), pygame.SRCALPHA)
        stats_bg.fill((0, 0, 0, 200))
        screen.blit(stats_bg, (SCREEN_WIDTH - 210, 5))
        
        stats_title = SMALL_FONT.render("STATS", True, (0, 255, 255))
        screen.blit(stats_title, (SCREEN_WIDTH - 200, 10))
        
        stats_y = 35
        drill_text = SMALL_FONT.render(f"Drill: {player.drill_level}", True, (255, 255, 255))
        screen.blit(drill_text, (SCREEN_WIDTH - 200, stats_y))
        fuel_text = SMALL_FONT.render(f"Fuel: {player.fuel_level}", True, (255, 255, 255))
        screen.blit(fuel_text, (SCREEN_WIDTH - 200, stats_y + 20))
        eff_text = SMALL_FONT.render(f"Efficiency: {player.efficiency_level}", True, (255, 255, 255))
        screen.blit(eff_text, (SCREEN_WIDTH - 200, stats_y + 40))
        hull_text = SMALL_FONT.render(f"Hull: {player.hull_level}", True, (255, 255, 255))
        screen.blit(hull_text, (SCREEN_WIDTH - 200, stats_y + 60))