"""
Main entry point for the pseudo-3D RPG game.
Handles game initialization, main loop, and event management.
"""

import pygame
import sys
import numpy as np
from engine.renderer import Renderer
from engine.raycaster import RayCaster
from engine.mode7 import Mode7Renderer
from game.player import Player
from game.world import World
from game.combat import CombatSystem
from game.spells import SpellSystem
from game.enemies import EnemyManager
from ui.interface import GameUI
from ui.menu import MainMenu
from assets.asset_manager import AssetManager
from save.save_manager import SaveManager
from config import *

class Game:
    def __init__(self):
        """Initialize the game engine and all systems."""
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error:
            print("Audio device not available, continuing without sound")
            # Continue without audio
        
        # Create display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pseudo-3D RPG")
        self.clock = pygame.time.Clock()
        
        # Initialize asset manager first
        self.asset_manager = AssetManager()
        self.asset_manager.load_all_assets()
        
        # Initialize rendering systems
        self.renderer = Renderer(self.screen, self.asset_manager)
        self.raycaster = RayCaster()
        self.mode7 = Mode7Renderer(self.asset_manager)
        
        # Initialize game systems
        self.world = World()
        self.player = Player(self.world.spawn_x, self.world.spawn_y)
        self.combat_system = CombatSystem(self.asset_manager)
        self.spell_system = SpellSystem(self.asset_manager)
        self.enemy_manager = EnemyManager(self.world, self.asset_manager)
        
        # Initialize UI
        self.ui = GameUI(self.asset_manager)
        self.main_menu = MainMenu(self.asset_manager)
        
        # Initialize save system
        self.save_manager = SaveManager()
        
        # Game state
        self.game_state = "MAIN_MENU"  # MAIN_MENU, PLAYING, PAUSED
        self.running = True
        self.delta_time = 0
        
        # Performance tracking
        self.frame_count = 0
        self.fps_timer = 0
        
    def handle_events(self):
        """Handle all input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "PLAYING":
                        self.game_state = "PAUSED"
                    elif self.game_state == "PAUSED":
                        self.game_state = "PLAYING"
                    elif self.game_state == "MAIN_MENU":
                        self.running = False
                        
                elif event.key == pygame.K_F1:
                    # Quick save
                    if self.game_state == "PLAYING":
                        self.save_game("quicksave")
                        
                elif event.key == pygame.K_F2:
                    # Quick load
                    if self.load_game("quicksave"):
                        self.game_state = "PLAYING"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_state == "PLAYING":
                    if event.button == 1:  # Left click
                        self.handle_left_click()
                    elif event.button == 3:  # Right click
                        self.handle_right_click()
                        
            # Pass events to appropriate systems
            if self.game_state == "MAIN_MENU":
                menu_action = self.main_menu.handle_event(event)
                if menu_action == "START_GAME":
                    self.game_state = "PLAYING"
                elif menu_action == "LOAD_GAME":
                    if self.load_game("save"):
                        self.game_state = "PLAYING"
                elif menu_action == "QUIT":
                    self.running = False
                    
            elif self.game_state == "PLAYING":
                self.ui.handle_event(event)
    
    def handle_left_click(self):
        """Handle left mouse click for combat."""
        # Get mouse position for targeting
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Convert screen coordinates to world ray for 3D targeting
        ray_angle = self.player.angle + (mouse_x - SCREEN_WIDTH // 2) * FOV / SCREEN_WIDTH
        
        # Check for enemy hits
        hit_enemy = self.enemy_manager.check_ray_hit(
            self.player.x, self.player.y, ray_angle, ATTACK_RANGE
        )
        
        if hit_enemy:
            # Perform attack
            if self.player.equipped_weapon:
                damage = self.combat_system.calculate_damage(
                    self.player, self.player.equipped_weapon
                )
                hit_enemy.take_damage(damage)
                self.combat_system.play_attack_sound(self.player.equipped_weapon)
            else:
                # Cast spell if no weapon equipped
                self.cast_spell_at_target(hit_enemy)
    
    def handle_right_click(self):
        """Handle right mouse click for blocking or secondary actions."""
        if self.player.equipped_shield:
            self.player.is_blocking = True
        elif self.player.equipped_weapon and self.player.equipped_weapon.type == "magic":
            # Alternative spell casting
            self.cast_area_spell()
    
    def cast_spell_at_target(self, target):
        """Cast a targeted spell."""
        if self.player.current_spell and self.player.spirit >= self.player.current_spell.cost:
            success = self.spell_system.cast_spell(
                self.player.current_spell, self.player, target
            )
            if success:
                self.player.spirit -= self.player.current_spell.cost
    
    def cast_area_spell(self):
        """Cast an area effect spell."""
        if self.player.current_spell and self.player.spirit >= self.player.current_spell.cost:
            # Cast at player position or in front of player
            target_x = self.player.x + np.cos(self.player.angle) * 2
            target_y = self.player.y + np.sin(self.player.angle) * 2
            
            success = self.spell_system.cast_area_spell(
                self.player.current_spell, target_x, target_y
            )
            if success:
                self.player.spirit -= self.player.current_spell.cost
    
    def update(self):
        """Update all game systems."""
        if self.game_state != "PLAYING":
            return
            
        # Handle continuous input
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        
        # Update player
        self.player.update(keys, self.world, self.delta_time)
        
        # Update enemies
        self.enemy_manager.update(self.player, self.delta_time)
        
        # Update combat system
        self.combat_system.update(self.delta_time)
        
        # Update spell system
        self.spell_system.update(self.delta_time)
        
        # Update UI
        self.ui.update(self.player, self.delta_time)
        
        # Check for player death
        if self.player.health <= 0:
            self.game_state = "MAIN_MENU"  # Game over
    
    def render(self):
        """Render the current frame."""
        if self.game_state == "MAIN_MENU":
            self.main_menu.render(self.screen)
        else:
            self.render_3d_view()
            self.ui.render(self.screen, self.player)
            
            if self.game_state == "PAUSED":
                self.render_pause_overlay()
    
    def render_3d_view(self):
        """Render the 3D perspective view."""
        # Clear screen with sky color
        self.screen.fill(SKY_COLOR)
        
        # Render floor and ceiling using Mode 7
        self.mode7.render_floor_ceiling(
            self.screen, self.player.x, self.player.y, self.player.angle
        )
        
        # Perform raycasting for walls
        rays = self.raycaster.cast_rays(
            self.player.x, self.player.y, self.player.angle, self.world
        )
        
        # Render walls
        self.renderer.render_walls(rays)
        
        # Render sprites (enemies, items) in 3D space
        self.renderer.render_sprites(
            self.enemy_manager.get_visible_enemies(self.player),
            self.player.x, self.player.y, self.player.angle
        )
        
        # Render weapon/spell effects
        self.renderer.render_weapon(self.player.equipped_weapon)
        self.renderer.render_spell_effects(self.spell_system.active_effects)
    
    def render_pause_overlay(self):
        """Render pause menu overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Render pause menu
        font = self.asset_manager.get_font("large")
        text = font.render("PAUSED", True, (255, 255, 255))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)
    
    def save_game(self, save_name):
        """Save the current game state."""
        game_data = {
            'player': self.player.to_dict(),
            'world': self.world.to_dict(),
            'enemies': self.enemy_manager.to_dict(),
            'timestamp': pygame.time.get_ticks()
        }
        self.save_manager.save_game(save_name, game_data)
    
    def load_game(self, save_name):
        """Load a saved game state."""
        game_data = self.save_manager.load_game(save_name)
        if game_data:
            self.player.from_dict(game_data['player'])
            self.world.from_dict(game_data['world'])
            self.enemy_manager.from_dict(game_data['enemies'])
            return True
        return False
    
    def run(self):
        """Main game loop."""
        while self.running:
            # Calculate delta time
            self.delta_time = self.clock.tick(TARGET_FPS) / 1000.0
            
            # Handle events
            self.handle_events()
            
            # Update game state
            self.update()
            
            # Render frame
            self.render()
            
            # Update display
            pygame.display.flip()
            
            # Performance tracking
            self.frame_count += 1
            self.fps_timer += self.delta_time
            if self.fps_timer >= 1.0:
                fps = self.frame_count / self.fps_timer
                pygame.display.set_caption(f"Pseudo-3D RPG - FPS: {fps:.1f}")
                self.frame_count = 0
                self.fps_timer = 0
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
