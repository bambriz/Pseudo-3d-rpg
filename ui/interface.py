"""
In-game UI system for the pseudo-3D RPG.
Handles HUD elements, inventory, character stats, and game interface.
"""

import pygame
import numpy as np
from config import *

class GameUI:
    def __init__(self, asset_manager):
        """Initialize the game UI system."""
        self.asset_manager = asset_manager
        
        # UI state
        self.show_inventory = False
        self.show_character_sheet = False
        self.show_minimap = True
        
        # Inventory selection
        self.selected_inventory_slot = 0
        self.inventory_scroll_offset = 0
        
        # UI surfaces
        self.hud_surface = pygame.Surface((SCREEN_WIDTH, 100))
        self.hud_surface.set_alpha(200)
        
        # Load UI fonts
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 48)
        
        # UI colors
        self.ui_bg_color = (20, 20, 20)
        self.ui_border_color = (100, 100, 100)
        self.health_color = (200, 50, 50)
        self.spirit_color = (50, 200, 50)
        self.fatigue_color = (200, 200, 50)
        self.text_color = (255, 255, 255)
        
        # Animation timers
        self.damage_flash_timer = 0.0
        self.heal_flash_timer = 0.0
        
        # Message system
        self.messages = []
        self.message_timer = 0.0
    
    def update(self, player, delta_time):
        """Update UI elements each frame."""
        # Update animation timers
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= delta_time
        
        if self.heal_flash_timer > 0:
            self.heal_flash_timer -= delta_time
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= delta_time
            if self.message_timer <= 0 and self.messages:
                self.messages.pop(0)
                if self.messages:
                    self.message_timer = 3.0  # Next message duration
    
    def handle_event(self, event, player=None):
        """Handle UI input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                self.toggle_inventory()
            elif event.key == pygame.K_c:
                self.toggle_character_sheet()
            elif event.key == pygame.K_m:
                self.toggle_minimap()
            elif event.key == pygame.K_TAB:
                # Cycle through UI displays
                if self.show_inventory:
                    self.show_inventory = False
                    self.show_character_sheet = True
                elif self.show_character_sheet:
                    self.show_character_sheet = False
                else:
                    self.show_inventory = True
            
            # Inventory navigation with arrow keys
            if self.show_inventory and player:
                if event.key == pygame.K_UP:
                    self.selected_inventory_slot = max(0, self.selected_inventory_slot - 8)
                elif event.key == pygame.K_DOWN:
                    max_slots = max(0, len(player.inventory) - 1)
                    self.selected_inventory_slot = min(max_slots, self.selected_inventory_slot + 8)
                elif event.key == pygame.K_LEFT:
                    self.selected_inventory_slot = max(0, self.selected_inventory_slot - 1)
                elif event.key == pygame.K_RIGHT:
                    max_slots = max(0, len(player.inventory) - 1)
                    self.selected_inventory_slot = min(max_slots, self.selected_inventory_slot + 1)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # Use/equip selected item
                    if self.selected_inventory_slot < len(player.inventory):
                        self.use_inventory_item(player, self.selected_inventory_slot)
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Handle inventory clicks
            if self.show_inventory and player:
                self.handle_inventory_click(event.pos, player)
        
        elif event.type == pygame.MOUSEWHEEL and self.show_inventory:
            # Scroll through inventory with mouse wheel
            if player and len(player.inventory) > 32:
                self.inventory_scroll_offset = max(0, min(len(player.inventory) // 8 - 4, 
                                                         self.inventory_scroll_offset - event.y))
    
    def render(self, screen, player):
        """Render all UI elements."""
        # Render HUD (always visible)
        self.render_hud(screen, player)
        
        # Render conditional UI elements
        if self.show_inventory:
            self.render_inventory(screen, player)
        
        if self.show_character_sheet:
            self.render_character_sheet(screen, player)
        
        if self.show_minimap:
            self.render_minimap(screen, player)
        
        # Render messages
        self.render_messages(screen)
        
        # Render crosshair
        self.render_crosshair(screen)
    
    def toggle_inventory(self):
        """Toggle inventory display."""
        self.show_inventory = not self.show_inventory
    
    def toggle_character_sheet(self):
        """Toggle character sheet display."""
        self.show_character_sheet = not self.show_character_sheet
    
    def toggle_minimap(self):
        """Toggle minimap display."""
        self.show_minimap = not self.show_minimap
    
    def add_message(self, message):
        """Add a message to display queue."""
        self.messages.append(message)
        self.message_timer = 3.0  # Display duration
    
    def render_messages(self, screen):
        """Render message queue."""
        if self.messages and self.message_timer > 0:
            message_surface = self.font_medium.render(self.messages[0], True, (255, 255, 255))
            message_rect = message_surface.get_rect()
            message_rect.centerx = SCREEN_WIDTH // 2
            message_rect.y = 50
            
            # Background
            bg_rect = message_rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
            pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2)
            
            screen.blit(message_surface, message_rect)
    
    def render_crosshair(self, screen):
        """Render crosshair in center of screen."""
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Simple crosshair
        pygame.draw.line(screen, (255, 255, 255), (center_x - 10, center_y), (center_x + 10, center_y), 2)
        pygame.draw.line(screen, (255, 255, 255), (center_x, center_y - 10), (center_x, center_y + 10), 2)
    
    def render_hud(self, screen, player):
        """Render the main HUD with health, spirit, and stats."""
        # Clear HUD surface
        self.hud_surface.fill(self.ui_bg_color)
        
        # Health bar
        health_percentage = player.health / player.max_health
        fatigue_health_reduction = player.fatigue / 100.0 * 0.3  # Max 30% reduction
        effective_max_health = player.max_health * (1.0 - fatigue_health_reduction)
        
        health_rect = pygame.Rect(UI_MARGIN, 10, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
        
        # Background
        pygame.draw.rect(self.hud_surface, (50, 50, 50), health_rect)
        pygame.draw.rect(self.hud_surface, self.ui_border_color, health_rect, 2)
        
        # Fatigue overlay (yellow)
        if fatigue_health_reduction > 0:
            fatigue_width = int(HEALTH_BAR_WIDTH * fatigue_health_reduction)
            fatigue_rect = pygame.Rect(
                health_rect.right - fatigue_width, health_rect.top,
                fatigue_width, HEALTH_BAR_HEIGHT
            )
            pygame.draw.rect(self.hud_surface, self.fatigue_color, fatigue_rect)
        
        # Health fill
        health_width = int(HEALTH_BAR_WIDTH * (player.health / player.max_health))
        if health_width > 0:
            health_fill_rect = pygame.Rect(
                health_rect.left, health_rect.top,
                health_width, HEALTH_BAR_HEIGHT
            )
            health_color = self.health_color
            
            # Flash red when taking damage
            if self.damage_flash_timer > 0:
                flash_intensity = int(100 * (self.damage_flash_timer / 0.5))
                health_color = (min(255, self.health_color[0] + flash_intensity), 
                              self.health_color[1], self.health_color[2])
            
            pygame.draw.rect(self.hud_surface, health_color, health_fill_rect)
        
        # Health text
        health_text = f"HP: {int(player.health)}/{int(player.max_health)}"
        text_surface = self.font_small.render(health_text, True, self.text_color)
        text_x = health_rect.centerx - text_surface.get_width() // 2
        text_y = health_rect.centery - text_surface.get_height() // 2
        self.hud_surface.blit(text_surface, (text_x, text_y))
        
        # Spirit bar
        spirit_percentage = player.spirit / player.max_spirit
        fatigue_spirit_reduction = player.fatigue / 100.0 * 0.4  # Max 40% reduction
        
        spirit_rect = pygame.Rect(UI_MARGIN, 40, SPIRIT_BAR_WIDTH, SPIRIT_BAR_HEIGHT)
        
        # Background
        pygame.draw.rect(self.hud_surface, (50, 50, 50), spirit_rect)
        pygame.draw.rect(self.hud_surface, self.ui_border_color, spirit_rect, 2)
        
        # Fatigue overlay
        if fatigue_spirit_reduction > 0:
            fatigue_width = int(SPIRIT_BAR_WIDTH * fatigue_spirit_reduction)
            fatigue_rect = pygame.Rect(
                spirit_rect.right - fatigue_width, spirit_rect.top,
                fatigue_width, SPIRIT_BAR_HEIGHT
            )
            pygame.draw.rect(self.hud_surface, self.fatigue_color, fatigue_rect)
        
        # Spirit fill
        spirit_width = int(SPIRIT_BAR_WIDTH * spirit_percentage)
        if spirit_width > 0:
            spirit_fill_rect = pygame.Rect(
                spirit_rect.left, spirit_rect.top,
                spirit_width, SPIRIT_BAR_HEIGHT
            )
            spirit_color = self.spirit_color
            
            # Flash green when healing/restoring spirit
            if self.heal_flash_timer > 0:
                flash_intensity = int(100 * (self.heal_flash_timer / 0.5))
                spirit_color = (self.spirit_color[0], 
                              min(255, self.spirit_color[1] + flash_intensity), 
                              self.spirit_color[2])
            
            pygame.draw.rect(self.hud_surface, spirit_color, spirit_fill_rect)
        
        # Spirit text
        spirit_text = f"SP: {int(player.spirit)}/{int(player.max_spirit)}"
        text_surface = self.font_small.render(spirit_text, True, self.text_color)
        text_x = spirit_rect.centerx - text_surface.get_width() // 2
        text_y = spirit_rect.centery - text_surface.get_height() // 2
        self.hud_surface.blit(text_surface, (text_x, text_y))
        
        # Player level and experience
        level_text = f"Level {player.level}"
        level_surface = self.font_small.render(level_text, True, self.text_color)
        self.hud_surface.blit(level_surface, (SPIRIT_BAR_WIDTH + UI_MARGIN * 2, 10))
        
        # Experience bar (small)
        exp_needed = player.level * 100
        exp_percentage = player.experience / exp_needed if exp_needed > 0 else 0
        exp_rect = pygame.Rect(SPIRIT_BAR_WIDTH + UI_MARGIN * 2, 30, 100, 8)
        pygame.draw.rect(self.hud_surface, (50, 50, 50), exp_rect)
        pygame.draw.rect(self.hud_surface, self.ui_border_color, exp_rect, 1)
        
        exp_width = int(100 * exp_percentage)
        if exp_width > 0:
            exp_fill_rect = pygame.Rect(exp_rect.left, exp_rect.top, exp_width, 8)
            pygame.draw.rect(self.hud_surface, (100, 100, 200), exp_fill_rect)
        
        # Current weapon info
        weapon_y = 50
        if player.equipped_weapon:
            weapon_text = f"Weapon: {player.equipped_weapon.name}"
            weapon_surface = self.font_small.render(weapon_text, True, self.text_color)
            self.hud_surface.blit(weapon_surface, (SPIRIT_BAR_WIDTH + UI_MARGIN * 2, weapon_y))
        
        # Current spell info
        if player.current_spell:
            spell_text = f"Spell: {player.current_spell.name}"
            spell_surface = self.font_small.render(spell_text, True, self.text_color)
            self.hud_surface.blit(spell_surface, (SPIRIT_BAR_WIDTH + UI_MARGIN * 2, weapon_y + 20))
        
        # Blit HUD to main screen
        screen.blit(self.hud_surface, (0, SCREEN_HEIGHT - 100))
    
    def render_crosshair(self, screen):
        """Render crosshair in center of screen."""
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Simple cross crosshair
        crosshair_color = (255, 255, 255)
        crosshair_size = 10
        
        # Horizontal line
        pygame.draw.line(screen, crosshair_color,
                        (center_x - crosshair_size, center_y),
                        (center_x + crosshair_size, center_y), 2)
        
        # Vertical line
        pygame.draw.line(screen, crosshair_color,
                        (center_x, center_y - crosshair_size),
                        (center_x, center_y + crosshair_size), 2)
    
    def render_inventory(self, screen, player):
        """Render the inventory interface."""
        # Create inventory background
        inventory_width = 400
        inventory_height = 300
        inventory_x = (SCREEN_WIDTH - inventory_width) // 2
        inventory_y = (SCREEN_HEIGHT - inventory_height) // 2
        
        inventory_rect = pygame.Rect(inventory_x, inventory_y, inventory_width, inventory_height)
        
        # Background
        pygame.draw.rect(screen, self.ui_bg_color, inventory_rect)
        pygame.draw.rect(screen, self.ui_border_color, inventory_rect, 3)
        
        # Title
        title_surface = self.font_medium.render("Inventory", True, self.text_color)
        title_x = inventory_rect.centerx - title_surface.get_width() // 2
        screen.blit(title_surface, (title_x, inventory_y + 10))
        
        # Inventory grid
        grid_start_x = inventory_x + 20
        grid_start_y = inventory_y + 50
        slot_size = 40
        slots_per_row = 8
        
        for i, item in enumerate(player.inventory[:32]):  # Show up to 32 items
            row = i // slots_per_row
            col = i % slots_per_row
            
            slot_x = grid_start_x + col * (slot_size + 5)
            slot_y = grid_start_y + row * (slot_size + 5)
            
            slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)
            
            # Slot background
            pygame.draw.rect(screen, (60, 60, 60), slot_rect)
            pygame.draw.rect(screen, self.ui_border_color, slot_rect, 2)
            
            # Item representation (simplified)
            if hasattr(item, 'name'):
                # Draw first letter of item name
                item_text = item.name[0].upper()
                text_surface = self.font_small.render(item_text, True, self.text_color)
                text_x = slot_rect.centerx - text_surface.get_width() // 2
                text_y = slot_rect.centery - text_surface.get_height() // 2
                screen.blit(text_surface, (text_x, text_y))
        
        # Instructions
        instruction_text = "I: close | Arrows: navigate | Enter/Space: use | Click: select"
        instruction_surface = self.font_small.render(instruction_text, True, self.text_color)
        instruction_x = inventory_rect.centerx - instruction_surface.get_width() // 2
        screen.blit(instruction_surface, (instruction_x, inventory_rect.bottom - 30))
    
    def use_inventory_item(self, player, slot):
        """Use or equip an item from inventory."""
        if slot >= len(player.inventory):
            return
        
        item = player.inventory[slot]
        if hasattr(item, 'type') and item.type in ['melee', 'ranged', 'magic']:
            player.equipped_weapon = item
            self.add_message(f"Equipped {item.name}")
        elif hasattr(item, 'effect'):
            item.use(player)  # Use consumable items
            self.add_message(f"Used {item.name}")
    
    def handle_inventory_click(self, mouse_pos, player):
        """Handle mouse clicks on inventory slots."""
        # Calculate which inventory slot was clicked
        inventory_x = (SCREEN_WIDTH - 400) // 2
        inventory_y = (SCREEN_HEIGHT - 300) // 2
        grid_start_x = inventory_x + 20
        grid_start_y = inventory_y + 50
        slot_size = 40
        slots_per_row = 8
        
        rel_x = mouse_pos[0] - grid_start_x
        rel_y = mouse_pos[1] - grid_start_y
        
        if rel_x >= 0 and rel_y >= 0:
            col = rel_x // (slot_size + 5)
            row = rel_y // (slot_size + 5)
            
            if col < slots_per_row and row < 4:  # Max 4 rows shown
                slot = row * slots_per_row + col + self.inventory_scroll_offset * slots_per_row
                if slot < len(player.inventory):
                    self.selected_inventory_slot = slot
                    self.use_inventory_item(player, slot)
    
    def render_character_sheet(self, screen, player):
        """Render the character sheet interface."""
        # Character sheet background
        sheet_width = 350
        sheet_height = 400
        sheet_x = (SCREEN_WIDTH - sheet_width) // 2
        sheet_y = (SCREEN_HEIGHT - sheet_height) // 2
        
        sheet_rect = pygame.Rect(sheet_x, sheet_y, sheet_width, sheet_height)
        
        # Background
        pygame.draw.rect(screen, self.ui_bg_color, sheet_rect)
        pygame.draw.rect(screen, self.ui_border_color, sheet_rect, 3)
        
        # Title
        title_surface = self.font_medium.render("Character", True, self.text_color)
        title_x = sheet_rect.centerx - title_surface.get_width() // 2
        screen.blit(title_surface, (title_x, sheet_y + 10))
        
        # Stats
        stats_start_y = sheet_y + 60
        line_height = 25
        
        stats = [
            f"Level: {player.level}",
            f"Experience: {player.experience}",
            f"Health: {int(player.health)}/{int(player.max_health)}",
            f"Spirit: {int(player.spirit)}/{int(player.max_spirit)}",
            f"Fatigue: {int(player.fatigue)}%",
            "",
            "Equipment:",
            f"Weapon: {player.equipped_weapon.name if player.equipped_weapon else 'None'}",
            f"Shield: {player.equipped_shield.name if player.equipped_shield else 'None'}",
            "",
            "Position:",
            f"X: {player.x:.1f}",
            f"Y: {player.y:.1f}",
            f"Angle: {np.degrees(player.angle):.1f}°"
        ]
        
        for i, stat in enumerate(stats):
            if stat:  # Skip empty lines for spacing
                stat_surface = self.font_small.render(stat, True, self.text_color)
                screen.blit(stat_surface, (sheet_x + 20, stats_start_y + i * line_height))
        
        # Instructions
        instruction_text = "Press C to close"
        instruction_surface = self.font_small.render(instruction_text, True, self.text_color)
        instruction_x = sheet_rect.centerx - instruction_surface.get_width() // 2
        screen.blit(instruction_surface, (instruction_x, sheet_rect.bottom - 30))
    
    def render_minimap(self, screen, player):
        """Render a simple minimap."""
        minimap_size = 120
        minimap_x = SCREEN_WIDTH - minimap_size - 10
        minimap_y = 10
        
        minimap_rect = pygame.Rect(minimap_x, minimap_y, minimap_size, minimap_size)
        
        # Background
        pygame.draw.rect(screen, (0, 0, 0), minimap_rect)
        pygame.draw.rect(screen, self.ui_border_color, minimap_rect, 2)
        
        # Simplified world representation
        # This would normally show explored areas
        
        # Player position indicator
        player_map_x = minimap_x + int((player.x / 32) * minimap_size)  # Assuming 32x32 world
        player_map_y = minimap_y + int((player.y / 32) * minimap_size)
        
        # Clamp to minimap bounds
        player_map_x = max(minimap_x, min(minimap_x + minimap_size - 1, player_map_x))
        player_map_y = max(minimap_y, min(minimap_y + minimap_size - 1, player_map_y))
        
        pygame.draw.circle(screen, (255, 255, 255), (player_map_x, player_map_y), 3)
        
        # Direction indicator
        direction_length = 8
        end_x = player_map_x + int(np.cos(player.angle) * direction_length)
        end_y = player_map_y + int(np.sin(player.angle) * direction_length)
        pygame.draw.line(screen, (255, 255, 0), (player_map_x, player_map_y), (end_x, end_y), 2)
    
    def render_messages(self, screen):
        """Render system messages."""
        if not self.messages:
            return
        
        message_y = 150
        for message in self.messages:
            message_surface = self.font_small.render(message, True, self.text_color)
            message_rect = message_surface.get_rect()
            
            # Background for message
            bg_rect = pygame.Rect(10, message_y - 5, message_rect.width + 10, message_rect.height + 10)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)
            pygame.draw.rect(screen, self.ui_border_color, bg_rect, 1)
            
            screen.blit(message_surface, (15, message_y))
            message_y += message_rect.height + 15
    
    def toggle_inventory(self):
        """Toggle inventory display."""
        self.show_inventory = not self.show_inventory
        if self.show_inventory:
            self.show_character_sheet = False
    
    def toggle_character_sheet(self):
        """Toggle character sheet display."""
        self.show_character_sheet = not self.show_character_sheet
        if self.show_character_sheet:
            self.show_inventory = False
    
    def toggle_minimap(self):
        """Toggle minimap display."""
        self.show_minimap = not self.show_minimap
    
    def show_damage_flash(self):
        """Trigger damage flash animation."""
        self.damage_flash_timer = 0.5
    
    def show_heal_flash(self):
        """Trigger heal flash animation."""
        self.heal_flash_timer = 0.5
    
    def add_message(self, message, duration=3.0):
        """Add a message to the message queue."""
        self.messages.append(message)
        if len(self.messages) == 1:  # First message
            self.message_timer = duration
    
    def clear_messages(self):
        """Clear all messages."""
        self.messages.clear()
        self.message_timer = 0.0
