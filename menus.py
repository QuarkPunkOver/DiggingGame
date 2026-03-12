import pygame
import os
import sys
from constants import SCREEN, SCREEN_WIDTH, SCREEN_HEIGHT, FONT, SMALL_FONT, TITLE_FONT, SAVE_FILE, REPAIR_COST, CLOCK
from ui import draw_rounded_rect, draw_world, draw_ui, draw_rounded_rect_with_border
from sound import sound_manager
from settings import settings

def draw_panel(screen, rect, title_text=None, title_color=(255, 215, 100)):
    draw_rounded_rect_with_border(screen, (20, 20, 30), rect, 25, (100, 100, 130), 3)
    inner_rect = pygame.Rect(rect.x + 8, rect.y + 8, rect.width - 16, rect.height - 16)
    draw_rounded_rect(screen, (30, 30, 40), inner_rect, 20)
    if title_text:
        title_font = pygame.font.Font(None, 42)
        title_shadow = title_font.render(title_text, True, (80, 60, 20))
        title = title_font.render(title_text, True, title_color)
        title_rect = title.get_rect(center=(rect.centerx + 2, rect.y + 37))
        screen.blit(title_shadow, title_rect)
        title_rect = title.get_rect(center=(rect.centerx, rect.y + 35))
        screen.blit(title, title_rect)

def draw_button(screen, rect, text, color=(40, 80, 40), hover_color=(80, 120, 80), text_color=(255, 255, 255), radius=8):
    mouse_pos = pygame.mouse.get_pos()
    if rect.collidepoint(mouse_pos):
        draw_rounded_rect(screen, hover_color, rect, radius)
    else:
        draw_rounded_rect(screen, color, rect, radius)
    border_color = tuple(min(c + 60, 255) for c in color)
    pygame.draw.rect(screen, border_color, rect, 1, border_radius=radius)
    text_surf = SMALL_FONT.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    return rect

def show_main_menu():
    menu_active = True
    while menu_active:
        SCREEN.fill((0, 0, 0))
        title_shadow = TITLE_FONT.render("DIGGING GAME", True, (80, 60, 20))
        title = TITLE_FONT.render("DIGGING GAME", True, (255, 215, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2 + 4, 84))
        SCREEN.blit(title_shadow, title_rect)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 80))
        SCREEN.blit(title, title_rect)
        subtitle_shadow = FONT.render("Core of the Earth", True, (40, 40, 40))
        subtitle = FONT.render("Core of the Earth", True, (255, 255, 255))
        sub_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2 + 2, 154))
        SCREEN.blit(subtitle_shadow, sub_rect)
        sub_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, 150))
        SCREEN.blit(subtitle, sub_rect)
        panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, 200, 400, 300)
        draw_panel(SCREEN, panel_rect)
        buttons = []
        btn_width, btn_height = 250, 50
        btn_x = SCREEN_WIDTH//2 - btn_width//2
        btn_y_start = 250
        btn_spacing = 15
        options = [
            ("NEW GAME", "new", (40, 80, 40)),
            ("LOAD GAME", "load" if os.path.exists(SAVE_FILE) else "load_disabled", (40, 40, 80) if os.path.exists(SAVE_FILE) else (40, 40, 40)),
            ("SETTINGS", "settings", (80, 80, 40)),
            ("EXIT", "exit", (80, 40, 40))
        ]
        for i, (text, action, color) in enumerate(options):
            btn_rect = pygame.Rect(btn_x, btn_y_start + i * (btn_height + btn_spacing), btn_width, btn_height)
            if action == "load_disabled":
                draw_rounded_rect(SCREEN, (40, 40, 40), btn_rect, 10)
                btn_text = SMALL_FONT.render(text, True, (100, 100, 100))
                text_rect = btn_text.get_rect(center=btn_rect.center)
                SCREEN.blit(btn_text, text_rect)
            else:
                draw_button(SCREEN, btn_rect, text, color, tuple(min(c + 40, 255) for c in color))
                buttons.append((btn_rect, action))
        credits = SMALL_FONT.render("Made by funDAVEover", True, (100, 100, 100))
        credits_rect = credits.get_rect(center=(SCREEN_WIDTH//2, 550))
        SCREEN.blit(credits, credits_rect)
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

def show_settings_menu(player=None, world=None):
    menu_active = True
    dragging_sound = False
    dragging_music = False
    resolutions = [(800, 600), (1024, 768), (1280, 720), (1366, 768), (1600, 900), (1920, 1080)]
    current_res_index = 0
    for i, (w, h) in enumerate(resolutions):
        if w == settings.screen_width and h == settings.screen_height:
            current_res_index = i
            break
    slider_width = 200
    slider_height = 10
    slider_x = SCREEN_WIDTH//2 - 100
    sound_slider_y = SCREEN_HEIGHT//2 - 40
    music_slider_y = SCREEN_HEIGHT//2 + 10
    while menu_active:
        SCREEN.fill((0, 0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        SCREEN.blit(overlay, (0, 0))
        panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 250, 600, 500)
        draw_panel(SCREEN, panel_rect, "SETTINGS", (100, 200, 255))
        y = SCREEN_HEIGHT//2 - 170
        sound_text = FONT.render("Sound:", True, (255, 255, 255))
        SCREEN.blit(sound_text, (SCREEN_WIDTH//2 - 250, y))
        sound_btn = pygame.Rect(SCREEN_WIDTH//2 + 150, y, 80, 30)
        color = (40, 80, 40) if settings.sound_enabled else (80, 40, 40)
        draw_button(SCREEN, sound_btn, "Toggle", color, (80, 120, 80) if settings.sound_enabled else (120, 80, 80))
        y += 50
        music_text = FONT.render("Music:", True, (255, 255, 255))
        SCREEN.blit(music_text, (SCREEN_WIDTH//2 - 250, y))
        music_btn = pygame.Rect(SCREEN_WIDTH//2 + 150, y, 80, 30)
        color = (40, 80, 40) if settings.music_enabled else (80, 40, 40)
        draw_button(SCREEN, music_btn, "Toggle", color, (80, 120, 80) if settings.music_enabled else (120, 80, 80))
        y += 50
        sound_vol_text = SMALL_FONT.render(f"Sound: {int(settings.sound_volume * 100)}%", True, (255, 255, 255))
        SCREEN.blit(sound_vol_text, (SCREEN_WIDTH//2 - 250, y))
        slider_rect = pygame.Rect(slider_x, sound_slider_y, slider_width, slider_height)
        draw_rounded_rect(SCREEN, (60, 60, 60), slider_rect, 5)
        fill_width = int(slider_width * settings.sound_volume)
        if fill_width > 0:
            fill_rect = pygame.Rect(slider_x, sound_slider_y, fill_width, slider_height)
            draw_rounded_rect(SCREEN, (0, 200, 0), fill_rect, 5)
        handle_x = slider_x + fill_width - 5
        handle_rect = pygame.Rect(handle_x, sound_slider_y - 5, 10, 20)
        draw_rounded_rect(SCREEN, (255, 255, 255), handle_rect, 3)
        y += 50
        music_vol_text = SMALL_FONT.render(f"Music: {int(settings.music_volume * 100)}%", True, (255, 255, 255))
        SCREEN.blit(music_vol_text, (SCREEN_WIDTH//2 - 250, y))
        music_slider_rect = pygame.Rect(slider_x, music_slider_y, slider_width, slider_height)
        draw_rounded_rect(SCREEN, (60, 60, 60), music_slider_rect, 5)
        music_fill_width = int(slider_width * settings.music_volume)
        if music_fill_width > 0:
            music_fill_rect = pygame.Rect(slider_x, music_slider_y, music_fill_width, slider_height)
            draw_rounded_rect(SCREEN, (0, 0, 200), music_fill_rect, 5)
        music_handle_x = slider_x + music_fill_width - 5
        music_handle_rect = pygame.Rect(music_handle_x, music_slider_y - 5, 10, 20)
        draw_rounded_rect(SCREEN, (255, 255, 255), music_handle_rect, 3)
        y += 50
        res_text = FONT.render("Resolution:", True, (255, 255, 255))
        SCREEN.blit(res_text, (SCREEN_WIDTH//2 - 250, y))
        res_value = SMALL_FONT.render(f"{settings.screen_width}x{settings.screen_height}", True, (255, 255, 255))
        SCREEN.blit(res_value, (SCREEN_WIDTH//2 + 50, y + 5))
        res_left_btn = pygame.Rect(SCREEN_WIDTH//2 + 120, y, 25, 25)
        draw_button(SCREEN, res_left_btn, "<", (80, 80, 80), (120, 120, 120))
        res_right_btn = pygame.Rect(SCREEN_WIDTH//2 + 150, y, 25, 25)
        draw_button(SCREEN, res_right_btn, ">", (80, 80, 80), (120, 120, 120))
        y += 50
        fs_text = FONT.render("Fullscreen:", True, (255, 255, 255))
        SCREEN.blit(fs_text, (SCREEN_WIDTH//2 - 250, y))
        fs_btn = pygame.Rect(SCREEN_WIDTH//2 + 50, y, 80, 30)
        color = (40, 80, 40) if settings.fullscreen else (80, 40, 40)
        draw_button(SCREEN, fs_btn, "Toggle", color, (80, 120, 80) if settings.fullscreen else (120, 80, 80))
        btn_y = SCREEN_HEIGHT//2 + 150
        apply_btn = pygame.Rect(SCREEN_WIDTH//2 - 130, btn_y, 120, 40)
        draw_button(SCREEN, apply_btn, "Apply", (40, 80, 120), (80, 120, 160))
        back_btn = pygame.Rect(SCREEN_WIDTH//2 + 10, btn_y, 120, 40)
        draw_button(SCREEN, back_btn, "Back", (80, 40, 40), (120, 80, 80))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if sound_btn.collidepoint(event.pos):
                    settings.sound_enabled = not settings.sound_enabled
                    settings.save()
                    sound_manager.play('menu_click')
                elif music_btn.collidepoint(event.pos):
                    settings.music_enabled = not settings.music_enabled
                    settings.save()
                    if settings.music_enabled and player and world:
                        sound_manager.update_music(player.y, world.depth)
                    else:
                        sound_manager.stop_music()
                    sound_manager.play('menu_click')
                elif handle_rect.collidepoint(event.pos):
                    dragging_sound = True
                elif music_handle_rect.collidepoint(event.pos):
                    dragging_music = True
                elif res_left_btn.collidepoint(event.pos):
                    current_res_index = (current_res_index - 1) % len(resolutions)
                    w, h = resolutions[current_res_index]
                    settings.screen_width = w
                    settings.screen_height = h
                    sound_manager.play('menu_click')
                elif res_right_btn.collidepoint(event.pos):
                    current_res_index = (current_res_index + 1) % len(resolutions)
                    w, h = resolutions[current_res_index]
                    settings.screen_width = w
                    settings.screen_height = h
                    sound_manager.play('menu_click')
                elif fs_btn.collidepoint(event.pos):
                    settings.fullscreen = not settings.fullscreen
                    sound_manager.play('menu_click')
                elif apply_btn.collidepoint(event.pos):
                    settings.save()
                    sound_manager.play('menu_click')
                    show_restart_message()
                elif back_btn.collidepoint(event.pos):
                    sound_manager.play('menu_click')
                    menu_active = False
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_sound = False
                dragging_music = False
            elif event.type == pygame.MOUSEMOTION:
                if dragging_sound:
                    mouse_x = event.pos[0]
                    new_volume = (mouse_x - slider_x) / slider_width
                    new_volume = max(0.0, min(1.0, new_volume))
                    settings.sound_volume = new_volume
                    sound_manager.set_sound_volume(new_volume)
                    settings.save()
                if dragging_music:
                    mouse_x = event.pos[0]
                    new_volume = (mouse_x - slider_x) / slider_width
                    new_volume = max(0.0, min(1.0, new_volume))
                    settings.music_volume = new_volume
                    sound_manager.set_music_volume(new_volume)
                    settings.save()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_active = False
        pygame.display.flip()
        CLOCK.tick(30)

def show_restart_message():
    msg_active = True
    while msg_active:
        SCREEN.fill((0,0,0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        SCREEN.blit(overlay, (0, 0))
        panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 100, 600, 200)
        draw_panel(SCREEN, panel_rect, "SETTINGS APPLIED", (100, 255, 100))
        msg = FONT.render("Please restart the game for changes to take effect.", True, (255, 255, 255))
        msg_rect = msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
        SCREEN.blit(msg, msg_rect)
        ok_btn = pygame.Rect(SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2 + 40, 120, 40)
        draw_button(SCREEN, ok_btn, "OK", (40, 80, 40), (80, 120, 80))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ok_btn.collidepoint(event.pos):
                    msg_active = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    msg_active = False
        pygame.display.flip()
        CLOCK.tick(30)

def show_save_menu(player, world, buildings):
    menu_active = True
    while menu_active:
        SCREEN.fill((0,0,0))
        draw_world(SCREEN, world, player, 0, 0, buildings)
        draw_ui(SCREEN, player, world)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        SCREEN.blit(overlay, (0, 0))
        panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 150, 400, 300)
        draw_panel(SCREEN, panel_rect, "SAVE GAME", (100, 200, 255))
        info = SMALL_FONT.render("Save your progress?", True, (255, 255, 255))
        info_rect = info.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 70))
        SCREEN.blit(info, info_rect)
        save_btn = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 20, 120, 40)
        draw_button(SCREEN, save_btn, "Save", (40, 80, 40), (80, 120, 80))
        cancel_btn = pygame.Rect(SCREEN_WIDTH//2 + 30, SCREEN_HEIGHT//2 - 20, 120, 40)
        draw_button(SCREEN, cancel_btn, "Cancel", (80, 40, 40), (120, 80, 80))
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
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        SCREEN.blit(overlay, (0, 0))
        panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 150, 600, 300)
        draw_panel(SCREEN, panel_rect, "EVACUATION", (255, 100, 100))
        if reason == "fuel":
            msg = FONT.render("You ran out of fuel! Rescued to base.", True, (255, 255, 255))
        else:
            msg = FONT.render("Your drill was destroyed by heat! Rescued to base.", True, (255, 255, 255))
        msg_rect = msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60))
        SCREEN.blit(msg, msg_rect)
        msg2 = FONT.render("All resources and money lost.", True, (255, 255, 255))
        msg2_rect = msg2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
        SCREEN.blit(msg2, msg2_rect)
        msg3 = FONT.render("Press any key to continue...", True, (255, 255, 255))
        msg3_rect = msg3.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        SCREEN.blit(msg3, msg3_rect)
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
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        SCREEN.blit(overlay, (0, 0))
        panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 150, 600, 300)
        draw_panel(SCREEN, panel_rect, "VICTORY!", (255, 215, 100))
        msg1 = FONT.render("You have drilled to the center of the Earth!", True, (255, 255, 255))
        msg1_rect = msg1.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60))
        SCREEN.blit(msg1, msg1_rect)
        msg2 = FONT.render(f"Final money: ${player.money}", True, (255, 255, 255))
        msg2_rect = msg2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
        SCREEN.blit(msg2, msg2_rect)
        msg3 = FONT.render("Press C to continue or Q to quit", True, (255, 255, 255))
        msg3_rect = msg3.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        SCREEN.blit(msg3, msg3_rect)
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
    cost_per_fuel = 0.7
    while menu_active:
        SCREEN.fill((0,0,0))
        draw_world(SCREEN, world, player, 0, 0, buildings)
        draw_ui(SCREEN, player, world)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        SCREEN.blit(overlay, (0, 0))
        panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 220, 400, 440)
        draw_panel(SCREEN, panel_rect, "FUEL STATION", (100, 255, 100))
        info = SMALL_FONT.render(f"Price: ${cost_per_fuel} per unit", True, (255, 255, 255))
        info_rect = info.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 140))
        SCREEN.blit(info, info_rect)
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
            draw_button(SCREEN, btn_rect, text, (40, 80, 40), (80, 120, 80))
            buttons.append((btn_rect, amount))
        fill_btn = pygame.Rect(SCREEN_WIDTH//2 - btn_width//2, SCREEN_HEIGHT//2 + 70, btn_width, btn_height)
        draw_button(SCREEN, fill_btn, "Fill all", (40, 80, 120), (80, 120, 160))
        buttons.append((fill_btn, "max"))
        close_btn = pygame.Rect(SCREEN_WIDTH//2 - btn_width//2, SCREEN_HEIGHT//2 + 120, btn_width, btn_height)
        draw_button(SCREEN, close_btn, "Close", (80, 40, 40), (120, 80, 80))
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

def show_tech_menu(player, world, buildings):
    menu_active = True
    while menu_active:
        SCREEN.fill((0,0,0))
        draw_world(SCREEN, world, player, 0, 0, buildings)
        draw_ui(SCREEN, player, world)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        SCREEN.blit(overlay, (0, 0))
        menu_width = 750
        menu_height = 550
        menu_x = SCREEN_WIDTH//2 - menu_width//2
        menu_y = SCREEN_HEIGHT//2 - menu_height//2
        panel_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        draw_panel(SCREEN, panel_rect, "TECH SERVICE", (255, 255, 100))
        upgrades = [
            {"name": "Drill Power", "level_attr": "drill_level", "cost": 300, "desc": "Allows mining deeper"},
            {"name": "Drill Width", "special": "width", "desc": "Increases max width"},
            {"name": "Fuel Capacity", "level_attr": "fuel_level", "cost": 200, "desc": "+75 fuel"},
            {"name": "Efficiency", "level_attr": "efficiency_level", "cost": 250, "desc": "Less fuel usage"},
            {"name": "Hull", "level_attr": "hull_level", "cost": 400, "desc": "+200 hull, +700°C resist"},
            {"name": "View Range", "special": "view_range", "desc": "See further in darkness"},
            {"name": "Speed", "level_attr": "speed_level", "cost": 300, "desc": "Faster movement (+15% per level)"},
        ]
        special_upgrades = [
            {"name": "Diamond Coating", "func": "apply_diamond_coating", "cost": "10 diamonds, $1000", "desc": "+66% drill speed"},
            {"name": "Electric Upgrade", "func": "apply_electric_upgrade", "cost": "20 gold, $500", "desc": "+10% speed, -10% fuel"},
            {"name": "Uranium Engine", "func": "apply_uranium_engine", "cost": "50 uranium, 30 tungsten, $5000", "desc": "+50% power, -20% fuel"},
            {"name": "Titanium Drill", "func": "apply_titanium_drill", "cost": "40 tungsten, 20 platinum, $8000", "desc": "+30% power, -15% fuel"},
            {"name": "Plasma Cutter", "func": "apply_plasma_cutter", "cost": "30 uranium isotope, 25 diamonds, $15000", "desc": "+100% power, -30% fuel, +500°C resist"},
            {"name": "Neutronium Core", "func": "apply_neutronium_core", "cost": "5 core fragments, 50 dense matter, $50000", "desc": "+200% power, -50% fuel, +1000°C resist, +50% fuel cap"},
        ]
        y = menu_y + 70
        buttons = []
        for i, upg in enumerate(upgrades):
            text_x = menu_x + 20
            btn_x = menu_x + 550
            if upg.get("special") == "width":
                if player.can_upgrade_width():
                    current_width = player.drill_width_max
                    next_width = current_width + 2 if current_width < 11 else 11
                    cost = player.get_width_cost()
                    text = SMALL_FONT.render(f"{upg['name']}: {current_width}->{next_width} | {upg['desc']} | ${cost}", True, (255, 255, 255))
                else:
                    text = SMALL_FONT.render(f"{upg['name']}: MAX (11 blocks)", True, (255, 255, 255))
                SCREEN.blit(text, (text_x, y + i*30))
                if player.can_upgrade_width():
                    btn_rect = pygame.Rect(btn_x, y + i*30, 70, 22)
                    draw_button(SCREEN, btn_rect, "Upgrade", (40, 80, 40), (80, 120, 80), radius=6)
                    buttons.append((btn_rect, "width"))
            elif upg.get("special") == "view_range":
                if player.can_upgrade_view_range():
                    current_range = player.view_range
                    next_range = current_range + 5
                    cost = player.get_view_range_cost()
                    text = SMALL_FONT.render(f"{upg['name']}: {current_range}->{next_range} | {upg['desc']} | ${cost}", True, (255, 255, 255))
                else:
                    text = SMALL_FONT.render(f"{upg['name']}: MAX ({player.max_view_range})", True, (255, 255, 255))
                SCREEN.blit(text, (text_x, y + i*30))
                if player.can_upgrade_view_range():
                    btn_rect = pygame.Rect(btn_x, y + i*30, 70, 22)
                    draw_button(SCREEN, btn_rect, "Upgrade", (40, 80, 40), (80, 120, 80), radius=6)
                    buttons.append((btn_rect, "view_range"))
            else:
                level = getattr(player, upg["level_attr"])
                if level < 10:
                    text = SMALL_FONT.render(f"{upg['name']}: {level}->{level+1} | {upg['desc']} | ${upg['cost']}", True, (255, 255, 255))
                else:
                    text = SMALL_FONT.render(f"{upg['name']}: MAX", True, (255, 255, 255))
                SCREEN.blit(text, (text_x, y + i*30))
                if level < 10:
                    btn_rect = pygame.Rect(btn_x, y + i*30, 70, 22)
                    draw_button(SCREEN, btn_rect, "Upgrade", (40, 80, 40), (80, 120, 80), radius=6)
                    buttons.append((btn_rect, upg))
        special_y = y + len(upgrades) * 30 + 20
        special_title = SMALL_FONT.render("SPECIAL UPGRADES:", True, (255, 255, 0))
        SCREEN.blit(special_title, (menu_x + 20, special_y))
        for j, upg in enumerate(special_upgrades):
            text_y = special_y + 25 + j*25
            text_x = menu_x + 20
            btn_x = menu_x + 550
            func_name = upg['func'].replace('apply_', '')
            is_owned = getattr(player, func_name, False)
            if is_owned:
                text = SMALL_FONT.render(f"{upg['name']}: {upg['cost']} - OWNED", True, (0, 255, 0))
                SCREEN.blit(text, (text_x, text_y))
            else:
                text = SMALL_FONT.render(f"{upg['name']}: {upg['cost']}", True, (200, 200, 255))
                SCREEN.blit(text, (text_x, text_y))
                desc_text = SMALL_FONT.render(upg['desc'], True, (150, 150, 150))
                SCREEN.blit(desc_text, (text_x + 10, text_y + 15))
                btn_rect = pygame.Rect(btn_x, text_y + 5, 70, 22)
                draw_button(SCREEN, btn_rect, "Buy", (40, 80, 40), (80, 120, 80), radius=6)
                buttons.append((btn_rect, upg['func']))
        btn_y = menu_y + menu_height - 50
        btn_width, btn_height = 120, 35
        repair_btn = pygame.Rect(menu_x + 200, btn_y, btn_width, btn_height)
        if player.hull_strength < player.max_hull:
            draw_button(SCREEN, repair_btn, f"Repair ${REPAIR_COST}", (40, 80, 40), (80, 120, 80))
        else:
            draw_rounded_rect(SCREEN, (40, 40, 40), repair_btn, 8)
            repair_text = SMALL_FONT.render(f"Repair ${REPAIR_COST}", True, (100, 100, 100))
            text_rect = repair_text.get_rect(center=repair_btn.center)
            SCREEN.blit(repair_text, text_rect)
        close_btn = pygame.Rect(menu_x + 400, btn_y, btn_width, btn_height)
        draw_button(SCREEN, close_btn, "Close", (80, 40, 40), (120, 80, 80))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn_rect, upg in buttons:
                    if btn_rect.collidepoint(event.pos):
                        if upg == "width":
                            if player.upgrade_width():
                                sound_manager.play('upgrade')
                        elif upg == "view_range":
                            if player.upgrade_view_range():
                                sound_manager.play('upgrade')
                        elif isinstance(upg, dict) and "level_attr" in upg:
                            level = getattr(player, upg["level_attr"])
                            if level < 10 and player.money >= upg["cost"]:
                                player.money -= upg["cost"]
                                setattr(player, upg["level_attr"], level + 1)
                                player.update_stats()
                                sound_manager.play('upgrade')
                        else:
                            func = getattr(player, upg)
                            if func():
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

def show_shop_menu(player, world, buildings):
    shop_active = True
    player_scroll = 0
    player_items_per_page = 8
    sell_prices = {
        'copper': 10, 'tin': 8, 'iron': 15, 'coal': 5,
        'gold': 50, 'platinum': 100, 'diamond': 200,
        'tungsten': 75, 'uranium': 150, 'silicon': 12,
        'gravel': 1, 'stone': 2, 'granite': 3,
        'uranium_isotope': 300, 'core_fragment': 1000,
        'soft_matter': 500, 'dense_matter': 800
    }
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    SCREEN.blit(overlay, (0, 0))
    panel_width = 700
    panel_height = 550
    panel_x = (SCREEN_WIDTH - panel_width) // 2
    panel_y = (SCREEN_HEIGHT - panel_height) // 2
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 18)
    title_font = pygame.font.Font(None, 42)
    
    while shop_active:
        draw_rounded_rect_with_border(SCREEN, (20, 20, 30), 
                                      pygame.Rect(panel_x, panel_y, panel_width, panel_height), 
                                      25, (100, 100, 130), 3)
        inner_rect = pygame.Rect(panel_x + 8, panel_y + 8, panel_width - 16, panel_height - 16)
        draw_rounded_rect(SCREEN, (30, 30, 40), inner_rect, 20)
        title_shadow = title_font.render("SELL RESOURCES", True, (80, 60, 20))
        title = title_font.render("SELL RESOURCES", True, (255, 215, 100))
        title_rect = title.get_rect(center=(panel_x + panel_width//2 + 2, panel_y + 37))
        SCREEN.blit(title_shadow, title_rect)
        title_rect = title.get_rect(center=(panel_x + panel_width//2, panel_y + 35))
        SCREEN.blit(title, title_rect)
        
        headers = ["Resource", "Count", "Price", "Total", "Actions"]
        header_x = panel_x + 50
        for i, header in enumerate(headers):
            text = small_font.render(header, True, (200, 200, 150))
            SCREEN.blit(text, (header_x + i * 120, panel_y + 90))
        
        player_items = list(player.inventory.items())
        visible_player_items = player_items[player_scroll:player_scroll + player_items_per_page]
        y_offset = panel_y + 120
        mouse_pos = pygame.mouse.get_pos()
        
        for i, (item, count) in enumerate(visible_player_items):
            y_pos = y_offset + i * 45
            price = sell_prices.get(item, 5)
            total_value = price * count
            
            if 'uranium' in item:
                color = (57, 255, 20)
            elif 'core' in item:
                color = (255, 100, 100)
            elif 'diamond' in item:
                color = (185, 242, 255)
            elif 'gold' in item:
                color = (255, 215, 0)
            elif 'platinum' in item:
                color = (229, 228, 226)
            else:
                color = (255, 255, 255)
            
            if i % 2 == 0:
                row_rect = pygame.Rect(panel_x + 30, y_pos - 5, panel_width - 60, 40)
                draw_rounded_rect(SCREEN, (40, 40, 50), row_rect, 10)
            
            icon_rect = pygame.Rect(panel_x + 40, y_pos, 20, 20)
            pygame.draw.rect(SCREEN, color, icon_rect)
            pygame.draw.rect(SCREEN, (255, 255, 255), icon_rect, 1)
            
            name_text = small_font.render(item.capitalize(), True, color)
            SCREEN.blit(name_text, (panel_x + 70, y_pos + 2))
            
            count_bg = pygame.Rect(panel_x + 160, y_pos, 40, 20)
            draw_rounded_rect(SCREEN, (20, 20, 30), count_bg, 6)
            count_text = small_font.render(str(count), True, (255, 255, 255))
            SCREEN.blit(count_text, (panel_x + 170, y_pos + 2))
            
            price_text = small_font.render(f"${price}", True, (100, 255, 100))
            SCREEN.blit(price_text, (panel_x + 270, y_pos + 2))
            
            total_text = small_font.render(f"${total_value}", True, (255, 255, 100))
            SCREEN.blit(total_text, (panel_x + 390, y_pos + 2))
            
            sell1_btn = pygame.Rect(panel_x + 490, y_pos - 2, 60, 24)
            if sell1_btn.collidepoint(mouse_pos):
                btn_color = (80, 120, 80)
            else:
                btn_color = (40, 80, 40)
            draw_rounded_rect(SCREEN, btn_color, sell1_btn, 8)
            pygame.draw.rect(SCREEN, (100, 200, 100), sell1_btn, 1, border_radius=8)
            sell1_text = small_font.render("1", True, (255, 255, 255))
            sell1_rect = sell1_text.get_rect(center=sell1_btn.center)
            SCREEN.blit(sell1_text, sell1_rect)
            
            sellall_btn = pygame.Rect(panel_x + 560, y_pos - 2, 70, 24)
            if sellall_btn.collidepoint(mouse_pos):
                btn_color = (80, 80, 120)
            else:
                btn_color = (40, 40, 80)
            draw_rounded_rect(SCREEN, btn_color, sellall_btn, 8)
            pygame.draw.rect(SCREEN, (150, 150, 255), sellall_btn, 1, border_radius=8)
            sellall_text = small_font.render("All", True, (255, 255, 255))
            sellall_rect = sellall_text.get_rect(center=sellall_btn.center)
            SCREEN.blit(sellall_text, sellall_rect)
        
        if len(player_items) > player_items_per_page:
            player_page = player_scroll // player_items_per_page + 1
            player_pages = (len(player_items) - 1) // player_items_per_page + 1
            scroll_bg = pygame.Rect(panel_x + panel_width//2 - 100, panel_y + panel_height - 120, 200, 30)
            draw_rounded_rect(SCREEN, (30, 30, 40), scroll_bg, 10)
            scroll_text = small_font.render(f"Page {player_page}/{player_pages}", True, (180, 180, 180))
            scroll_rect = scroll_text.get_rect(center=scroll_bg.center)
            SCREEN.blit(scroll_text, scroll_rect)
        
        close_btn = pygame.Rect(panel_x + panel_width//2 - 75, panel_y + panel_height - 70, 150, 40)
        
        if close_btn.collidepoint(mouse_pos):
            btn_color = (120, 60, 60)
        else:
            btn_color = (80, 40, 40)
        
        draw_rounded_rect(SCREEN, btn_color, close_btn, 10)
        pygame.draw.rect(SCREEN, (150, 100, 100), close_btn, 2, border_radius=10)
        
        close_text = pygame.font.Font(None, 28).render("Close", True, (255, 255, 255))
        text_rect = close_text.get_rect(center=close_btn.center)
        SCREEN.blit(close_text, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    shop_active = False
                elif event.key == pygame.K_UP:
                    player_scroll = max(0, player_scroll - 1)
                elif event.key == pygame.K_DOWN:
                    max_scroll = max(0, len(player_items) - player_items_per_page)
                    player_scroll = min(max_scroll, player_scroll + 1)
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    player_scroll = max(0, player_scroll - 1)
                elif event.y < 0:
                    max_scroll = max(0, len(player_items) - player_items_per_page)
                    player_scroll = min(max_scroll, player_scroll + 1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if close_btn.collidepoint(event.pos):
                        shop_active = False
                        sound_manager.play('menu_click')
                        break
                        
                    for i, (item, count) in enumerate(visible_player_items):
                        y_pos = panel_y + 120 + i * 45
                        sell1_btn = pygame.Rect(panel_x + 490, y_pos - 2, 60, 24)
                        if sell1_btn.collidepoint(event.pos):
                            price = sell_prices.get(item, 5)
                            player.money += price
                            player.inventory[item] -= 1
                            if player.inventory[item] <= 0:
                                del player.inventory[item]
                            sound_manager.play('collect')
                            player_items = list(player.inventory.items())
                            break
                        sellall_btn = pygame.Rect(panel_x + 560, y_pos - 2, 70, 24)
                        if sellall_btn.collidepoint(event.pos):
                            price = sell_prices.get(item, 5)
                            total = price * count
                            player.money += total
                            del player.inventory[item]
                            sound_manager.play('collect')
                            player_items = list(player.inventory.items())
                            break
        pygame.display.flip()
        CLOCK.tick(30)