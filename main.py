import pygame
import sys
from constants import SCREEN, CLOCK, WORLD_WIDTH, WORLD_DEPTH, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from world import World
from player import Player
from building import Building
from ui import draw_world, draw_ui
from menus import (
    show_main_menu, show_settings_menu, show_fuel_menu, show_shop_menu,
    show_tech_menu, show_save_menu, show_evacuation_message,
    show_core_victory_screen
)
from sound import sound_manager

def main():
    buildings = []
    
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
        cheat_sequence = []
        target_cheat = [pygame.K_h, pygame.K_e, pygame.K_s, pygame.K_o, pygame.K_y, pygame.K_a, pygame.K_m]

        damage_timer = 0
        DAMAGE_INTERVAL = 1000

        while running:
            dt = CLOCK.tick(60)
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in target_cheat:
                        cheat_sequence.append(event.key)
                        if len(cheat_sequence) > len(target_cheat):
                            cheat_sequence.pop(0)
                        if cheat_sequence == target_cheat:
                            player.fuel = player.max_fuel
                            player.money += 10000
                            sound_manager.play('upgrade')
                            cheat_sequence.clear()
                    else:
                        cheat_sequence.clear()

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
                        running = False

                elif event.type == pygame.KEYUP:
                    if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN,
                                     pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s]:
                        player.keys_pressed.discard(event.key)
                        if not player.keys_pressed:
                            player.auto_dig_direction = None
                            player.continue_digging = False
                    if event.key == pygame.K_SPACE:
                        player.stop_digging()

            if player.keys_pressed and current_time - player.last_move_time > player.move_delay:
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