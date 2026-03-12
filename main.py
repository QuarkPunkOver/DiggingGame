import pygame
import sys
from constants import SCREEN, CLOCK, WORLD_WIDTH, WORLD_DEPTH, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from world import World
from player import Player
from building import Building
from ui import draw_world, draw_ui, draw_rounded_rect, draw_rounded_rect_with_border
from menus import (
    show_main_menu, show_settings_menu, show_fuel_menu, show_shop_menu,
    show_tech_menu, show_save_menu, show_evacuation_message,
    show_core_victory_screen
)
from sound import sound_manager
from settings import settings

def show_pause_menu(player, world, buildings):
    menu_active = True
    pause_bg = None
    
    try:
        pause_bg = SCREEN.copy()
    except:
        pause_bg = None
    
    sound_manager.pause_music()
    
    while menu_active:
        if pause_bg:
            SCREEN.blit(pause_bg, (0, 0))
        else:
            SCREEN.fill((0, 0, 0))
            draw_world(SCREEN, world, player, 0, 0, buildings)
            draw_ui(SCREEN, player, world)
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        SCREEN.blit(overlay, (0, 0))
        
        panel_width = 450
        panel_height = 500
        panel_x = SCREEN_WIDTH//2 - panel_width//2
        panel_y = SCREEN_HEIGHT//2 - panel_height//2
        
        draw_rounded_rect_with_border(SCREEN, (20, 20, 30), 
                                      pygame.Rect(panel_x, panel_y, panel_width, panel_height), 
                                      25, (100, 100, 130), 3)
        
        inner_rect = pygame.Rect(panel_x + 8, panel_y + 8, panel_width - 16, panel_height - 16)
        draw_rounded_rect(SCREEN, (30, 30, 40), inner_rect, 20)
        
        title_font = pygame.font.Font(None, 48)
        title_shadow = title_font.render("PAUSE", True, (80, 60, 20))
        title = title_font.render("PAUSE", True, (255, 215, 100))
        title_rect = title.get_rect(center=(panel_x + panel_width//2 + 2, panel_y + 47))
        SCREEN.blit(title_shadow, title_rect)
        title_rect = title.get_rect(center=(panel_x + panel_width//2, panel_y + 45))
        SCREEN.blit(title, title_rect)
        
        buttons = []
        btn_width, btn_height = 250, 50
        btn_x = SCREEN_WIDTH//2 - btn_width//2
        btn_y_start = panel_y + 130
        btn_spacing = 20
        
        options = [
            ("CONTINUE", "continue", (40, 80, 40)),      # Green
            ("SAVE GAME", "save", (40, 40, 80)),         # Blue
            ("SETTINGS", "settings", (80, 80, 40)),      # Yellow
            ("EXIT TO MENU", "exit", (80, 40, 40))       # Red
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        
        for i, (text, action, base_color) in enumerate(options):
            btn_rect = pygame.Rect(btn_x, btn_y_start + i * (btn_height + btn_spacing), btn_width, btn_height)
            
            if action == "save" and not player:
                draw_rounded_rect(SCREEN, (40, 40, 40), btn_rect, 12)
                btn_text = pygame.font.Font(None, 30).render(text, True, (100, 100, 100))
                text_rect = btn_text.get_rect(center=btn_rect.center)
                SCREEN.blit(btn_text, text_rect)
            else:
                if btn_rect.collidepoint(mouse_pos):
                    hover_color = tuple(min(c + 40, 255) for c in base_color)
                    draw_rounded_rect(SCREEN, hover_color, btn_rect, 12)
                else:
                    draw_rounded_rect(SCREEN, base_color, btn_rect, 12)
                
                border_color = tuple(min(c + 60, 255) for c in base_color)
                pygame.draw.rect(SCREEN, border_color, btn_rect, 2, border_radius=12)
                
                btn_text = pygame.font.Font(None, 30).render(text, True, (255, 255, 255))
                text_rect = btn_text.get_rect(center=btn_rect.center)
                SCREEN.blit(btn_text, text_rect)
                
                buttons.append((btn_rect, action))
        
        info_text = pygame.font.Font(None, 20).render("Press ESC again to continue", True, (150, 150, 150))
        info_rect = info_text.get_rect(center=(panel_x + panel_width//2, panel_y + panel_height - 40))
        SCREEN.blit(info_text, info_rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sound_manager.unpause_music()
                    menu_active = False
                    return "continue"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for btn_rect, action in buttons:
                    if btn_rect.collidepoint(event.pos):
                        sound_manager.play('menu_click')
                        
                        if action == "continue":
                            sound_manager.unpause_music()
                            menu_active = False
                            return "continue"
                        
                        elif action == "save":
                            if player:
                                show_save_menu(player, world, buildings)
                                try:
                                    pause_bg = SCREEN.copy()
                                except:
                                    pass
                        
                        elif action == "settings":
                            show_settings_menu(player, world)
                            try:
                                pause_bg = SCREEN.copy()
                            except:
                                pass
                        
                        elif action == "exit":
                            sound_manager.stop_music()
                            menu_active = False
                            return "exit"
        
        pygame.display.flip()
        CLOCK.tick(30)
    
    return "continue"

def main():
    buildings = []
    
    MUSIC_TRANSITION_EVENT = pygame.USEREVENT + 1
    
    while True:
        menu_result = show_main_menu()
        
        if menu_result == "exit":
            pygame.quit()
            sys.exit()
        elif menu_result == "settings":
            show_settings_menu()
            continue
        
        if menu_result == "load":
            player = Player(0, 0)
            save_data = player.load_game()
            if save_data:
                world = World(WORLD_WIDTH, WORLD_DEPTH, True, save_data['world'])
                player = Player(WORLD_WIDTH // 2, 0, True, save_data['player'])
            else:
                world = World(WORLD_WIDTH, WORLD_DEPTH)
                player = Player(WORLD_WIDTH // 2, 0)
        else:
            world = World(WORLD_WIDTH, WORLD_DEPTH)
            player = Player(WORLD_WIDTH // 2, 0)
        
        buildings = [
            Building(WORLD_WIDTH // 2 - 3, 0, 'fuel'),
            Building(WORLD_WIDTH // 2 - 1, 0, 'shop'),
            Building(WORLD_WIDTH // 2 + 1, 0, 'tech'),
            Building(WORLD_WIDTH // 2 + 3, 0, 'save')
        ]

        camera_x = player.x * TILE_SIZE - SCREEN_WIDTH // 2
        camera_y = player.y * TILE_SIZE - SCREEN_HEIGHT // 2

        running = True
        
        cheat_hesoyam = []
        
        target_hesoyam = [pygame.K_h, pygame.K_e, pygame.K_s, pygame.K_o, pygame.K_y, pygame.K_a, pygame.K_m]


        damage_timer = 0
        DAMAGE_INTERVAL = 1000
        
        if settings.music_enabled:
            sound_manager.play_music('ost_upper')

        while running:
            dt = CLOCK.tick(60)
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == MUSIC_TRANSITION_EVENT:
                    sound_manager.finish_transition()
                elif event.type == pygame.KEYDOWN:
                    if event.key in target_hesoyam:
                        cheat_hesoyam.append(event.key)
                        if len(cheat_hesoyam) > len(target_hesoyam):
                            cheat_hesoyam.pop(0)
                        if cheat_hesoyam == target_hesoyam:
                            player.fuel = player.max_fuel
                            player.money += 10000
                            player.cheat_rocketman()
                            sound_manager.play('upgrade')
                            print("[CHEAT] HESOYAM activated! Okay, but who's going to play")
                    else:
                        cheat_hesoyam.clear()

                    if player.show_inventory:
                        if event.key == pygame.K_UP:
                            player.scroll_inventory(-1)
                        elif event.key == pygame.K_DOWN:
                            player.scroll_inventory(1)
                        elif event.key == pygame.K_ESCAPE:
                            player.show_inventory = False
                            player.selected_inventory_item = None

                    if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN,
                                     pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s]:
                        player.keys_pressed.add(event.key)
                        if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            player.try_move_or_dig(-1, 0, world)
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            player.try_move_or_dig(1, 0, world)
                        elif event.key == pygame.K_UP or event.key == pygame.K_w:
                            player.try_move_or_dig(0, -1, world)
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            player.try_move_or_dig(0, 1, world)
                        player.last_move_time = current_time

                    elif event.key == pygame.K_SPACE:
                        player.start_digging(world)
                    elif event.key == pygame.K_i:
                        player.show_inventory = not player.show_inventory
                        if not player.show_inventory:
                            player.selected_inventory_item = None
                    elif event.key == pygame.K_u:
                        player.show_stats = not player.show_stats
                    elif event.key == pygame.K_e:
                        for b in buildings:
                            if b.x == player.x and b.y == player.y:
                                menu = b.interact(player)
                                if menu == "fuel_menu":
                                    show_fuel_menu(player, world, buildings)
                                elif menu == "shop_menu":
                                    show_shop_menu(player, world, buildings)
                                elif menu == "tech_menu":
                                    show_tech_menu(player, world, buildings)
                                elif menu == "save_menu":
                                    show_save_menu(player, world, buildings)
                                break
                    elif event.key == pygame.K_ESCAPE:
                            pause_result = show_pause_menu(player, world, buildings)
                            if pause_result == "exit":
                                running = False
                                break
                            camera_x = player.x * TILE_SIZE - SCREEN_WIDTH // 2
                            camera_y = player.y * TILE_SIZE - SCREEN_HEIGHT // 2

                elif event.type == pygame.KEYUP:
                    if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN,
                                     pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s]:
                        player.keys_pressed.discard(event.key)
                        if not player.keys_pressed:
                            player.auto_dig_direction = None
                            player.continue_digging = False
                    if event.key == pygame.K_SPACE:
                        player.stop_digging()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if hasattr(player, 'width_minus_btn') and player.width_minus_btn and player.width_minus_btn.collidepoint(event.pos):
                            player.decrease_width()
                        if hasattr(player, 'width_plus_btn') and player.width_plus_btn and player.width_plus_btn.collidepoint(event.pos):
                            player.increase_width()
                        if player.show_inventory:
                            if hasattr(player, 'inventory_close_btn') and player.inventory_close_btn and player.inventory_close_btn.collidepoint(event.pos):
                                player.show_inventory = False
                                player.inventory_scroll = 0
                                sound_manager.play('menu_click')
                                if hasattr(player, 'inventory_close_btn'):
                                    delattr(player, 'inventory_close_btn')
                
                elif event.type == pygame.MOUSEWHEEL:
                    if player.show_inventory:
                        if event.y > 0:
                            if hasattr(player, 'scroll_inventory'):
                                player.scroll_inventory(-1)
                        elif event.y < 0:
                            if hasattr(player, 'scroll_inventory'):
                                player.scroll_inventory(1)

            if not running:
                break

            current_delay = player.get_current_move_delay(world)
            
            if player.keys_pressed and current_time - player.last_move_time > current_delay:
                sorted_keys = sorted(player.keys_pressed)
                for key in sorted_keys:
                    if key in [pygame.K_LEFT, pygame.K_a]:
                        player.try_move_or_dig(-1, 0, world)
                        break
                    elif key in [pygame.K_RIGHT, pygame.K_d]:
                        player.try_move_or_dig(1, 0, world)
                        break
                    elif key in [pygame.K_UP, pygame.K_w]:
                        player.try_move_or_dig(0, -1, world)
                        break
                    elif key in [pygame.K_DOWN, pygame.K_s]:
                        player.try_move_or_dig(0, 1, world)
                        break
                player.last_move_time = current_time

            result = player.update_digging(world)
            if result == "core_reached":
                if not show_core_victory_screen(player):
                    running = False
                    break
                else:
                    player.game_completed = False

            if current_time - damage_timer > DAMAGE_INTERVAL:
                if player.take_damage(world):
                    show_evacuation_message("heat")
                    player.evacuate()
                damage_timer = current_time

            if player.fuel <= 0 and player.y > 0:
                show_evacuation_message("fuel")
                player.evacuate()

            if settings.music_enabled:
                sound_manager.update_music(player.y, world.depth)
            
            sound_manager.update(current_time)

            camera_x = player.x * TILE_SIZE - SCREEN_WIDTH // 2
            camera_y = player.y * TILE_SIZE - SCREEN_HEIGHT // 2
            camera_x = max(0, min(camera_x, world.width * TILE_SIZE - SCREEN_WIDTH))
            camera_y = max(0, min(camera_y, world.depth * TILE_SIZE - SCREEN_HEIGHT))

            SCREEN.fill((0,0,0))
            draw_world(SCREEN, world, player, camera_x, camera_y, buildings)
            draw_ui(SCREEN, player, world)

            pygame.display.flip()

if __name__ == "__main__":
    main()