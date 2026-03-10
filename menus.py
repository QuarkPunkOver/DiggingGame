import pygame
import os
import sys
from constants import SCREEN, SCREEN_WIDTH, SCREEN_HEIGHT, FONT, SMALL_FONT, TITLE_FONT, SAVE_FILE, REPAIR_COST, CLOCK
from ui import draw_rounded_rect, draw_world, draw_ui
from sound import sound_manager
from settings import settings

def show_main_menu():
    menu_active = True
    
    while menu_active:
        SCREEN.fill((0, 0, 0))
        
        title = TITLE_FONT.render("DIGGING GAME", True, (255, 215, 0))
        SCREEN.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 80))
        
        subtitle = FONT.render("Core of the Earth", True, (255, 255, 255))
        SCREEN.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 150))
        
        buttons = []
        btn_width, btn_height = 250, 50
        btn_x = SCREEN_WIDTH//2 - btn_width//2
        btn_y_start = 220
        btn_spacing = 15
        
        options = [
            ("NEW GAME", "new"),
            ("LOAD GAME", "load" if os.path.exists(SAVE_FILE) else "load_disabled"),
            ("SETTINGS", "settings"),
            ("EXIT", "exit")
        ]
        
        for i, (text, action) in enumerate(options):
            btn_rect = pygame.Rect(btn_x, btn_y_start + i * (btn_height + btn_spacing), btn_width, btn_height)
            
            if action == "load_disabled":
                color = (80, 80, 80)
            else:
                color = (0, 100, 0) if i == 0 else (100, 100, 100) if i == 1 else (80, 80, 150) if i == 2 else (100, 0, 0)
            
            draw_rounded_rect(SCREEN, color, btn_rect, 10)
            
            if action != "load_disabled":
                pygame.draw.rect(SCREEN, (255, 255, 255), btn_rect, 2, border_radius=10)
            
            btn_text = FONT.render(text, True, (255, 255, 255))
            text_x = btn_x + (btn_width - btn_text.get_width()) // 2
            text_y = btn_y_start + i * (btn_height + btn_spacing) + (btn_height - btn_text.get_height()) // 2
            SCREEN.blit(btn_text, (text_x, text_y))
            
            if action != "load_disabled":
                buttons.append((btn_rect, action))
        
        credits = SMALL_FONT.render("Made by funDAVEover", True, (100, 100, 100))
        SCREEN.blit(credits, (SCREEN_WIDTH//2 - credits.get_width()//2, 520))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn_rect, action in buttons:
                    if btn_rect.collidepoint(event.pos):
                        sound_manager.play('menu_click')
                        return action
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "exit"
        
        pygame.display.flip()
        CLOCK.tick(30)

def show_settings_menu():
    menu_active = True
    
    while menu_active:
        SCREEN.fill((0, 0, 0))
        
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        SCREEN.blit(s, (0, 0))
        
        menu_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 200, 500, 400)
        draw_rounded_rect(SCREEN, (40, 40, 40), menu_rect, 20)
        draw_rounded_rect(SCREEN, (80, 80, 80), menu_rect.inflate(-4, -4), 18)
        
        title = FONT.render("SETTINGS", True, (255, 255, 255))
        SCREEN.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 170))
        
        y = SCREEN_HEIGHT//2 - 100
        
        sound_text = FONT.render(f"Sound: {'ON' if settings.sound_enabled else 'OFF'}", True, (255, 255, 255))
        SCREEN.blit(sound_text, (SCREEN_WIDTH//2 - 100, y))
        sound_btn = pygame.Rect(SCREEN_WIDTH//2 + 50, y, 80, 30)
        draw_rounded_rect(SCREEN, (0, 150, 0) if settings.sound_enabled else (150, 0, 0), sound_btn, 8)
        sound_btn_text = FONT.render("Toggle", True, (255, 255, 255))
        sound_btn_x = sound_btn.x + (80 - sound_btn_text.get_width()) // 2
        sound_btn_y = sound_btn.y + (30 - sound_btn_text.get_height()) // 2
        SCREEN.blit(sound_btn_text, (sound_btn_x, sound_btn_y))
        
        back_btn = pygame.Rect(SCREEN_WIDTH//2 - 75, SCREEN_HEIGHT//2 + 100, 150, 40)
        draw_rounded_rect(SCREEN, (150, 0, 0), back_btn, 10)
        back_text = FONT.render("Back", True, (255, 255, 255))
        back_x = back_btn.x + (150 - back_text.get_width()) // 2
        back_y = back_btn.y + (40 - back_text.get_height()) // 2
        SCREEN.blit(back_text, (back_x, back_y))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if sound_btn.collidepoint(event.pos):
                    settings.sound_enabled = not settings.sound_enabled
                    settings.save()
                    sound_manager.play('menu_click')
                if back_btn.collidepoint(event.pos):
                    sound_manager.play('menu_click')
                    menu_active = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_active = False
        
        pygame.display.flip()
        CLOCK.tick(30)

def show_save_menu(player, world, buildings):
    menu_active = True
    
    while menu_active:
        SCREEN.fill((0,0,0))
        draw_world(SCREEN, world, player, 0, 0, buildings)
        draw_ui(SCREEN, player, world)
        
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        SCREEN.blit(s, (0, 0))
        
        menu_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 150, 400, 300)
        draw_rounded_rect(SCREEN, (40, 40, 40), menu_rect, 20)
        draw_rounded_rect(SCREEN, (80, 80, 80), menu_rect.inflate(-4, -4), 18)
        
        title = FONT.render("SAVE GAME", True, (255, 255, 255))
        SCREEN.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 120))
        
        info = SMALL_FONT.render("Save your progress?", True, (255, 255, 255))
        SCREEN.blit(info, (SCREEN_WIDTH//2 - info.get_width()//2, SCREEN_HEIGHT//2 - 70))
        
        save_btn = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 20, 120, 40)
        draw_rounded_rect(SCREEN, (0, 150, 0), save_btn, 10)
        save_text = FONT.render("Save", True, (255, 255, 255))
        save_x = save_btn.x + (120 - save_text.get_width()) // 2
        save_y = save_btn.y + (40 - save_text.get_height()) // 2
        SCREEN.blit(save_text, (save_x, save_y))
        
        cancel_btn = pygame.Rect(SCREEN_WIDTH//2 + 30, SCREEN_HEIGHT//2 - 20, 120, 40)
        draw_rounded_rect(SCREEN, (150, 0, 0), cancel_btn, 10)
        cancel_text = FONT.render("Cancel", True, (255, 255, 255))
        cancel_x = cancel_btn.x + (120 - cancel_text.get_width()) // 2
        cancel_y = cancel_btn.y + (40 - cancel_text.get_height()) // 2
        SCREEN.blit(cancel_text, (cancel_x, cancel_y))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if save_btn.collidepoint(event.pos):
                    player.save_game(world)
                    menu_active = False
                elif cancel_btn.collidepoint(event.pos):
                    menu_active = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_active = False
        
        pygame.display.flip()
        CLOCK.tick(30)

def show_evacuation_message(reason="fuel"):
    message_active = True
    while message_active:
        SCREEN.fill((0,0,0))
        
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        SCREEN.blit(s, (0, 0))
        
        msg_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 150, 600, 300)
        draw_rounded_rect(SCREEN, (50, 50, 50), msg_rect, 20)
        draw_rounded_rect(SCREEN, (100, 100, 100), msg_rect.inflate(-4, -4), 18)
        
        title = FONT.render("EVACUATION", True, (255, 0, 0))
        SCREEN.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 120))
        
        if reason == "fuel":
            msg = FONT.render("You ran out of fuel! Rescued to base.", True, (255, 255, 255))
        else:
            msg = FONT.render("Your drill was destroyed by heat! Rescued to base.", True, (255, 255, 255))
        
        SCREEN.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, SCREEN_HEIGHT//2 - 60))
        msg2 = FONT.render("All resources and money lost.", True, (255, 255, 255))
        SCREEN.blit(msg2, (SCREEN_WIDTH//2 - msg2.get_width()//2, SCREEN_HEIGHT//2 - 20))
        msg3 = FONT.render("Press any key to continue...", True, (255, 255, 255))
        SCREEN.blit(msg3, (SCREEN_WIDTH//2 - msg3.get_width()//2, SCREEN_HEIGHT//2 + 40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                message_active = False
        pygame.display.flip()
        CLOCK.tick(30)

def show_core_victory_screen(player):
    message_active = True
    sound_manager.play('victory')
    
    while message_active:
        SCREEN.fill((0,0,0))
        
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        SCREEN.blit(s, (0, 0))
        
        msg_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 150, 600, 300)
        draw_rounded_rect(SCREEN, (50, 50, 50), msg_rect, 20)
        draw_rounded_rect(SCREEN, (100, 100, 100), msg_rect.inflate(-4, -4), 18)
        
        title = FONT.render("VICTORY! CORE REACHED!", True, (255, 215, 0))
        SCREEN.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 120))
        
        msg1 = FONT.render("You have drilled to the center of the Earth!", True, (255, 255, 255))
        SCREEN.blit(msg1, (SCREEN_WIDTH//2 - msg1.get_width()//2, SCREEN_HEIGHT//2 - 60))
        
        msg2 = FONT.render(f"Final money: ${player.money}", True, (255, 255, 255))
        SCREEN.blit(msg2, (SCREEN_WIDTH//2 - msg2.get_width()//2, SCREEN_HEIGHT//2 - 20))
        
        msg3 = FONT.render("Press C to continue or Q to quit", True, (255, 255, 255))
        SCREEN.blit(msg3, (SCREEN_WIDTH//2 - msg3.get_width()//2, SCREEN_HEIGHT//2 + 40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    return True
                elif event.key == pygame.K_q:
                    return False
        pygame.display.flip()
        CLOCK.tick(30)

def show_fuel_menu(player, world, buildings):
    menu_active = True
    cost_per_fuel = 1

    while menu_active:
        SCREEN.fill((0,0,0))
        draw_world(SCREEN, world, player, 0, 0, buildings)
        draw_ui(SCREEN, player, world)
        
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        SCREEN.blit(s, (0, 0))
        
        menu_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 220, 400, 440)
        draw_rounded_rect(SCREEN, (40, 40, 40), menu_rect, 20)
        draw_rounded_rect(SCREEN, (80, 80, 80), menu_rect.inflate(-4, -4), 18)
        
        title = FONT.render("FUEL STATION", True, (0, 255, 0))
        SCREEN.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 190))

        info = SMALL_FONT.render(f"Price: ${cost_per_fuel} per unit", True, (255, 255, 255))
        SCREEN.blit(info, (SCREEN_WIDTH//2 - info.get_width()//2, SCREEN_HEIGHT//2 - 140))

        buttons = []
        btn_y_start = SCREEN_HEIGHT//2 - 100
        btn_width, btn_height = 150, 35
        btn_spacing = 10
        
        options = [
            ("+100", 100),
            ("+250", 250),
            ("+500", 500),
            ("+1000", 1000),
        ]
        
        for i, (text, amount) in enumerate(options):
            btn_x = SCREEN_WIDTH//2 - btn_width//2
            btn_y = btn_y_start + i * (btn_height + btn_spacing)
            btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
            draw_rounded_rect(SCREEN, (0, 150, 0), btn_rect, 8)
            btn_text = SMALL_FONT.render(text, True, (255, 255, 255))
            text_x = btn_x + (btn_width - btn_text.get_width()) // 2
            text_y = btn_y + (btn_height - btn_text.get_height()) // 2
            SCREEN.blit(btn_text, (text_x, text_y))
            buttons.append((btn_rect, amount))

        fill_btn = pygame.Rect(SCREEN_WIDTH//2 - btn_width//2, SCREEN_HEIGHT//2 + 70, btn_width, btn_height)
        draw_rounded_rect(SCREEN, (0, 150, 0), fill_btn, 8)
        fill_text = SMALL_FONT.render("Fill all", True, (255, 255, 255))
        fill_x = fill_btn.x + (btn_width - fill_text.get_width()) // 2
        fill_y = fill_btn.y + (btn_height - fill_text.get_height()) // 2
        SCREEN.blit(fill_text, (fill_x, fill_y))
        buttons.append((fill_btn, "max"))

        close_btn = pygame.Rect(SCREEN_WIDTH//2 - btn_width//2, SCREEN_HEIGHT//2 + 120, btn_width, btn_height)
        draw_rounded_rect(SCREEN, (150, 0, 0), close_btn, 8)
        close_text = SMALL_FONT.render("Close", True, (255, 255, 255))
        close_x = close_btn.x + (btn_width - close_text.get_width()) // 2
        close_y = close_btn.y + (btn_height - close_text.get_height()) // 2
        SCREEN.blit(close_text, (close_x, close_y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn_rect, amount in buttons:
                    if btn_rect.collidepoint(event.pos):
                        sound_manager.play('fuel')
                        if amount == "max":
                            max_possible = player.max_fuel - player.fuel
                            cost = max_possible * cost_per_fuel
                            if player.money >= cost:
                                player.money -= cost
                                player.fuel = player.max_fuel
                            else:
                                affordable = player.money // cost_per_fuel
                                if affordable > 0:
                                    player.fuel = min(player.max_fuel, player.fuel + affordable)
                                    player.money -= affordable * cost_per_fuel
                        else:
                            cost = amount * cost_per_fuel
                            if player.money >= cost:
                                player.money -= cost
                                player.fuel = min(player.max_fuel, player.fuel + amount)
                if close_btn.collidepoint(event.pos):
                    menu_active = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_active = False
        pygame.display.flip()
        CLOCK.tick(30)

def show_shop_menu(player, world, buildings):
    menu_active = True
    prices = {
        'gravel': 1,
        'dense_earth': 2,
        'soft_stone': 3,
        'stone': 4,
        'dense_stone': 6,
        'andesite': 8,
        'granite': 10,
        'soft_matter': 100,
        'dense_matter': 200,
        'coal': 2,
        'silicon': 5,
        'copper': 8,
        'tin': 8,
        'iron': 15,
        'gold': 50,
        'platinum': 80,
        'tungsten': 100,
        'diamond': 200,
        'core_fragment': 10000
    }

    while menu_active:
        SCREEN.fill((0,0,0))
        draw_world(SCREEN, world, player, 0, 0, buildings)
        draw_ui(SCREEN, player, world)
        
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        SCREEN.blit(s, (0, 0))
        
        menu_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 250, 600, 500)
        draw_rounded_rect(SCREEN, (40, 40, 40), menu_rect, 20)
        draw_rounded_rect(SCREEN, (80, 80, 80), menu_rect.inflate(-4, -4), 18)
        
        title = FONT.render("SHOP", True, (0, 0, 255))
        SCREEN.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 220))

        inv_title = FONT.render("Your inventory:", True, (255, 255, 0))
        SCREEN.blit(inv_title, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 170))

        y = SCREEN_HEIGHT//2 - 140
        buttons = []
        for i, (res, count) in enumerate(player.inventory.items()):
            if i < 6:
                price = prices.get(res, 0)
                text = SMALL_FONT.render(f"{res}: {count}  (${price} each)", True, (255, 255, 255))
                SCREEN.blit(text, (SCREEN_WIDTH//2 - 250, y + i*30))
                btn = pygame.Rect(SCREEN_WIDTH//2 + 150, y + i*30, 80, 25)
                draw_rounded_rect(SCREEN, (0, 150, 0), btn, 8)
                btn_text = SMALL_FONT.render("Sell", True, (255, 255, 255))
                btn_x = btn.x + (80 - btn_text.get_width()) // 2
                btn_y = btn.y + (25 - btn_text.get_height()) // 2
                SCREEN.blit(btn_text, (btn_x, btn_y))
                buttons.append((btn, res, price))

        stats_title = FONT.render("Your stats:", True, (0, 255, 255))
        SCREEN.blit(stats_title, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 + 20))
        
        stats_y = SCREEN_HEIGHT//2 + 50
        drill_text = FONT.render(f"Drill: {player.drill_level}", True, (255, 255, 255))
        SCREEN.blit(drill_text, (SCREEN_WIDTH//2 - 250, stats_y))
        fuel_text = FONT.render(f"Fuel: {player.fuel_level}", True, (255, 255, 255))
        SCREEN.blit(fuel_text, (SCREEN_WIDTH//2 - 250, stats_y + 25))
        eff_text = FONT.render(f"Efficiency: {player.efficiency_level}", True, (255, 255, 255))
        SCREEN.blit(eff_text, (SCREEN_WIDTH//2 - 250, stats_y + 50))
        hull_text = FONT.render(f"Hull: {player.hull_level}", True, (255, 255, 255))
        SCREEN.blit(hull_text, (SCREEN_WIDTH//2 - 250, stats_y + 75))

        btn_width, btn_height = 150, 40
        sell_all_btn = pygame.Rect(SCREEN_WIDTH//2 - 160, SCREEN_HEIGHT//2 + 150, btn_width, btn_height)
        draw_rounded_rect(SCREEN, (0, 150, 0), sell_all_btn, 10)
        sell_all_text = FONT.render("Sell All", True, (255, 255, 255))
        sell_all_x = sell_all_btn.x + (btn_width - sell_all_text.get_width()) // 2
        sell_all_y = sell_all_btn.y + (btn_height - sell_all_text.get_height()) // 2
        SCREEN.blit(sell_all_text, (sell_all_x, sell_all_y))

        close_btn = pygame.Rect(SCREEN_WIDTH//2 + 10, SCREEN_HEIGHT//2 + 150, btn_width, btn_height)
        draw_rounded_rect(SCREEN, (150, 0, 0), close_btn, 10)
        close_text = FONT.render("Close", True, (255, 255, 255))
        close_x = close_btn.x + (btn_width - close_text.get_width()) // 2
        close_y = close_btn.y + (btn_height - close_text.get_height()) // 2
        SCREEN.blit(close_text, (close_x, close_y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn, res, price in buttons:
                    if btn.collidepoint(event.pos):
                        if player.inventory[res] > 0:
                            player.inventory[res] -= 1
                            player.money += price
                            sound_manager.play('collect')
                            if player.inventory[res] == 0:
                                del player.inventory[res]
                if sell_all_btn.collidepoint(event.pos):
                    for res, count in list(player.inventory.items()):
                        price = prices.get(res, 0)
                        player.money += price * count
                    player.inventory.clear()
                    sound_manager.play('collect')
                if close_btn.collidepoint(event.pos):
                    menu_active = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_active = False
        pygame.display.flip()
        CLOCK.tick(30)

def show_tech_menu(player, world, buildings):
    menu_active = True

    while menu_active:
        SCREEN.fill((0,0,0))
        draw_world(SCREEN, world, player, 0, 0, buildings)
        draw_ui(SCREEN, player, world)
        
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        SCREEN.blit(s, (0, 0))
        
        menu_rect = pygame.Rect(SCREEN_WIDTH//2 - 350, SCREEN_HEIGHT//2 - 220, 700, 440)
        draw_rounded_rect(SCREEN, (40, 40, 40), menu_rect, 20)
        draw_rounded_rect(SCREEN, (80, 80, 80), menu_rect.inflate(-4, -4), 18)
        
        title = FONT.render("TECH SERVICE", True, (255, 255, 0))
        SCREEN.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 200))

        upgrades = [
            {"name": "Drill Power", "level_attr": "drill_level", "cost": 300, "desc": "Allows mining deeper"},
            {"name": "Fuel Capacity", "level_attr": "fuel_level", "cost": 200, "desc": "+75 fuel"},
            {"name": "Efficiency", "level_attr": "efficiency_level", "cost": 250, "desc": "Less fuel usage"},
            {"name": "Hull", "level_attr": "hull_level", "cost": 400, "desc": "+200 hull, +700°C resist"},
        ]

        y = SCREEN_HEIGHT//2 - 140
        buttons = []
        for i, upg in enumerate(upgrades):
            level = getattr(player, upg["level_attr"])
            if level < 10:
                text = SMALL_FONT.render(f"{upg['name']}: {level} -> {level+1} | {upg['desc']} | ${upg['cost']}", True, (255, 255, 255))
            else:
                text = SMALL_FONT.render(f"{upg['name']}: MAX", True, (255, 255, 255))
            SCREEN.blit(text, (SCREEN_WIDTH//2 - 320, y + i*40))
            if level < 10:
                btn = pygame.Rect(SCREEN_WIDTH//2 + 180, y + i*40, 80, 25)
                draw_rounded_rect(SCREEN, (0, 150, 0), btn, 8)
                btn_text = SMALL_FONT.render("Upgrade", True, (255, 255, 255))
                btn_x = btn.x + (80 - btn_text.get_width()) // 2
                btn_y = btn.y + (25 - btn_text.get_height()) // 2
                SCREEN.blit(btn_text, (btn_x, btn_y))
                buttons.append((btn, upg))

        stats_bg = pygame.Rect(SCREEN_WIDTH//2 - 340, SCREEN_HEIGHT//2 + 60, 150, 110)
        draw_rounded_rect(SCREEN, (30, 30, 30), stats_bg, 10)
        
        stats_title = SMALL_FONT.render("Your stats:", True, (0, 255, 255))
        SCREEN.blit(stats_title, (SCREEN_WIDTH//2 - 330, SCREEN_HEIGHT//2 + 70))
        
        stats_y = SCREEN_HEIGHT//2 + 95
        drill_text = SMALL_FONT.render(f"Drill: {player.drill_level}", True, (255, 255, 255))
        SCREEN.blit(drill_text, (SCREEN_WIDTH//2 - 330, stats_y))
        fuel_text = SMALL_FONT.render(f"Fuel: {player.fuel_level}", True, (255, 255, 255))
        SCREEN.blit(fuel_text, (SCREEN_WIDTH//2 - 330, stats_y + 20))
        eff_text = SMALL_FONT.render(f"Efficiency: {player.efficiency_level}", True, (255, 255, 255))
        SCREEN.blit(eff_text, (SCREEN_WIDTH//2 - 330, stats_y + 40))
        hull_text = SMALL_FONT.render(f"Hull: {player.hull_level}", True, (255, 255, 255))
        SCREEN.blit(hull_text, (SCREEN_WIDTH//2 - 330, stats_y + 60))

        btn_y = SCREEN_HEIGHT//2 + 140
        btn_width, btn_height = 120, 35
        
        repair_btn = pygame.Rect(SCREEN_WIDTH//2 - 130, btn_y, btn_width, btn_height)
        if player.hull_strength < player.max_hull:
            draw_rounded_rect(SCREEN, (0, 150, 0), repair_btn, 8)
        else:
            draw_rounded_rect(SCREEN, (80, 80, 80), repair_btn, 8)
        repair_text = SMALL_FONT.render(f"Repair ${REPAIR_COST}", True, (255, 255, 255))
        repair_x = repair_btn.x + (btn_width - repair_text.get_width()) // 2
        repair_y = repair_btn.y + (btn_height - repair_text.get_height()) // 2
        SCREEN.blit(repair_text, (repair_x, repair_y))

        close_btn = pygame.Rect(SCREEN_WIDTH//2 + 10, btn_y, btn_width, btn_height)
        draw_rounded_rect(SCREEN, (150, 0, 0), close_btn, 8)
        close_text = SMALL_FONT.render("Close", True, (255, 255, 255))
        close_x = close_btn.x + (btn_width - close_text.get_width()) // 2
        close_y = close_btn.y + (btn_height - close_text.get_height()) // 2
        SCREEN.blit(close_text, (close_x, close_y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn, upg in buttons:
                    if btn.collidepoint(event.pos):
                        level = getattr(player, upg["level_attr"])
                        if level < 10 and player.money >= upg["cost"]:
                            player.money -= upg["cost"]
                            setattr(player, upg["level_attr"], level + 1)
                            player.update_stats()
                            sound_manager.play('upgrade')
                if repair_btn.collidepoint(event.pos) and player.hull_strength < player.max_hull:
                    if player.repair():
                        sound_manager.play('repair')
                if close_btn.collidepoint(event.pos):
                    menu_active = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_active = False
        pygame.display.flip()
        CLOCK.tick(30)