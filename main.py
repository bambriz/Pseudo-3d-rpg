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
from game.npcs import NPCManager, DialogueUI
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
        
        # Enable mouse capture for proper FPS-style controls
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
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
        
        # Give player default fist weapon and some starting items
        self.player.equipped_weapon = self.combat_system.weapons['fist']
        self.player.add_to_inventory(self.combat_system.weapons['sword'])
        self.player.add_to_inventory(self.combat_system.weapons['dagger'])
        self.player.add_to_inventory(self.combat_system.weapons['wand'])
        self.spell_system = SpellSystem(self.asset_manager)
        self.enemy_manager = EnemyManager(self.world, self.asset_manager)
        self.enemy_manager.spawn_initial_enemies()
        
        # Initialize NPC system
        self.npc_manager = NPCManager(self.world, self.asset_manager)
        self.npc_manager.spawn_initial_npcs()
        self.dialogue_ui = DialogueUI(self.asset_manager)
        
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
                        
                elif event.key == pygame.K_q and self.game_state == "PAUSED":
                    # Quit to main menu from pause
                    self.game_state = "MAIN_MENU"
            
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
                self.ui.handle_event(event, self.player)
                # Handle dialogue input
                if self.dialogue_ui.active:
                    self.dialogue_ui.handle_input(event)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    # Interact with NPCs (E key)
                    self.handle_npc_interaction()
    
    def handle_left_click(self):
        """Handle left mouse click for combat."""
        # Get mouse position for targeting
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Convert screen coordinates to world ray for 3D targeting
        ray_angle = self.player.angle + (mouse_x - SCREEN_WIDTH // 2) * FOV / SCREEN_WIDTH
        
        # Get weapon range (use equipped weapon range, or default to fist range)
        weapon_range = 1.0  # Default fist range
        if self.player.equipped_weapon:
            weapon_range = self.player.equipped_weapon.range
        
        # Check for enemy hits using weapon-specific range
        hit_enemy = self.enemy_manager.check_ray_hit(
            self.player.x, self.player.y, ray_angle, weapon_range
        )
        
        if hit_enemy:
            # Perform attack based on weapon type
            if self.player.equipped_weapon:
                weapon = self.player.equipped_weapon
                
                # Handle different weapon types
                if weapon.type == "ranged":
                    # Create projectile for ranged weapons
                    self.create_projectile(self.player.x, self.player.y, ray_angle, weapon, hit_enemy)
                elif weapon.type == "magic":
                    # Cast spell at target
                    self.cast_spell_at_target(hit_enemy)
                else:
                    # Melee attack - check distance and perform immediate hit
                    dx = hit_enemy.x - self.player.x
                    dy = hit_enemy.y - self.player.y
                    distance = (dx*dx + dy*dy)**0.5
                    
                    if distance <= weapon.range:
                        # Trigger attack animation
                        if self.player.attack():
                            weapon.is_attacking = True
                            weapon.attack_animation_time = 0.0
                            damage = self.combat_system.calculate_damage(self.player, weapon)
                            hit_enemy.take_damage(damage)
                            self.combat_system.play_attack_sound(weapon)
            else:
                # Use fist attack if no weapon equipped
                dx = hit_enemy.x - self.player.x
                dy = hit_enemy.y - self.player.y
                distance = (dx*dx + dy*dy)**0.5
                
                if distance <= 1.0:  # Fist range
                    if self.player.attack():
                        fist_weapon = self.combat_system.weapons['fist']
                        fist_weapon.is_attacking = True
                        fist_weapon.attack_animation_time = 0.0
                        damage = self.combat_system.calculate_damage(self.player, fist_weapon)
                        hit_enemy.take_damage(damage)
                        self.combat_system.play_attack_sound(fist_weapon)
        else:
            # Attack even if no target (for animation) 
            if self.player.equipped_weapon:
                weapon = self.player.equipped_weapon
                if self.player.attack():
                    weapon.is_attacking = True
                    weapon.attack_animation_time = 0.0
                    if weapon.type == "ranged":
                        # Create projectile even without target
                        self.create_projectile(self.player.x, self.player.y, ray_angle, weapon, None)
            else:
                # Animate fist attack even without target
                if self.player.attack():
                    fist_weapon = self.combat_system.weapons['fist']
                    fist_weapon.is_attacking = True
                    fist_weapon.attack_animation_time = 0.0
    
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
        
        # Update other game systems
        self.enemy_manager.update(self.delta_time, self.player)
        self.npc_manager.update(self.delta_time)
        self.spell_system.update(self.delta_time)
        self.combat_system.update(self.delta_time)
        
        # Update weapon animations
        if self.player.equipped_weapon:
            if self.player.equipped_weapon.is_attacking:
                self.player.equipped_weapon.attack_animation_time += self.delta_time
                if self.player.equipped_weapon.attack_animation_time >= 0.4:  # Animation duration
                    self.player.equipped_weapon.is_attacking = False
                    self.player.equipped_weapon.attack_animation_time = 0.0
        
        
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
            
            # Render dialogue if active
            if self.dialogue_ui.active:
                self.dialogue_ui.render(self.screen)
            
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
        
        # Render sprites (enemies, NPCs, items) in 3D space
        all_sprites = []
        all_sprites.extend(self.enemy_manager.get_visible_enemies(self.player))
        all_sprites.extend(self.npc_manager.get_visible_npcs(self.player))
        
        self.renderer.render_sprites(
            all_sprites, self.player.x, self.player.y, self.player.angle
        )
        
        # Render weapon/spell effects
        self.renderer.render_weapon(self.player.equipped_weapon)
        self.renderer.render_spell_effects(self.spell_system.active_effects)
    
    def render_pause_overlay(self):
        """Render pause menu with options."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Get fonts
        large_font = self.asset_manager.get_font("large")
        medium_font = self.asset_manager.get_font("medium")
        
        if large_font is None:
            large_font = pygame.font.Font(None, 72)
        if medium_font is None:
            medium_font = pygame.font.Font(None, 48)
        
        # Render title
        title_text = large_font.render("GAME PAUSED", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(title_text, title_rect)
        
        # Render menu options
        options = [
            "Press ESC to Resume",
            "Press Q to Quit to Main Menu",  
            "Press ALT+F4 to Exit Game"
        ]
        
        for i, option in enumerate(options):
            option_text = medium_font.render(option, True, (200, 200, 200))
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20 + i * 40))
            self.screen.blit(option_text, option_rect)
    
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
    
    def handle_npc_interaction(self):
        """Handle NPC interaction when E key is pressed."""
        # Find nearby NPC
        npc = self.npc_manager.get_npc_at_position(self.player.x, self.player.y, radius=2.0)
        if npc:
            self.dialogue_ui.start_dialogue(npc, self.player)
    
    def create_projectile(self, start_x, start_y, angle, weapon, target=None):
        """Create a projectile for ranged weapons."""
        # Add projectile to spell system for rendering and physics
        projectile = {
            'x': start_x,
            'y': start_y,
            'angle': angle,
            'speed': 8.0,  # Projectile speed
            'range': weapon.range,
            'damage': self.combat_system.calculate_damage(self.player, weapon),
            'weapon_type': weapon.type,
            'target': target,
            'lifetime': weapon.range / 8.0  # Time to travel max range
        }
        
        # Add to active projectiles in spell system
        if not hasattr(self.spell_system, 'active_projectiles'):
            self.spell_system.active_projectiles = []
        self.spell_system.active_projectiles.append(projectile)
        
        # Trigger weapon animation
        weapon.is_attacking = True
        weapon.attack_animation_time = 0.0
        self.combat_system.play_attack_sound(weapon)
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
