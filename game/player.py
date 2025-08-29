"""
Player character class with movement, stats, and equipment management.
Handles first-person camera and physics in the 3D world.
"""

import pygame
import numpy as np
from config import *

class Player:
    def __init__(self, start_x, start_y):
        """Initialize the player character."""
        # Position and orientation
        self.x = start_x
        self.y = start_y
        self.angle = 0.0  # Facing direction in radians
        
        # Movement
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.is_moving = False
        
        # Stats
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.max_spirit = PLAYER_MAX_SPIRIT
        self.spirit = self.max_spirit
        self.fatigue = 0.0
        self.level = 1
        self.experience = 0
        
        # Equipment
        self.equipped_weapon = None
        self.equipped_shield = None
        self.inventory = []
        
        # Combat state
        self.is_blocking = False
        self.is_attacking = False
        self.attack_cooldown = 0.0
        
        # Spell casting
        self.current_spell = None
        self.spell_cooldown = 0.0
        
        # Input state
        self.mouse_sensitivity = MOUSE_SENSITIVITY
        self.keys_pressed = set()
        
    def update(self, keys, world, delta_time):
        """Update player state each frame."""
        self.keys_pressed = set()
        for key in keys:
            if keys[key]:
                self.keys_pressed.add(key)
        
        # Update movement
        self.update_movement(keys, world, delta_time)
        
        # Update mouse look
        self.update_mouse_look()
        
        # Update combat state
        self.update_combat(delta_time)
        
        # Update stats
        self.update_stats(delta_time)
        
        # Handle input actions
        self.handle_input_actions(keys)
    
    def update_movement(self, keys, world, delta_time):
        """Handle player movement and collision detection."""
        move_x = 0.0
        move_y = 0.0
        
        # Calculate movement direction
        if keys[pygame.K_w]:
            move_x += np.cos(self.angle)
            move_y += np.sin(self.angle)
        if keys[pygame.K_s]:
            move_x -= np.cos(self.angle)
            move_y -= np.sin(self.angle)
        if keys[pygame.K_a]:
            move_x += np.cos(self.angle - np.pi / 2)
            move_y += np.sin(self.angle - np.pi / 2)
        if keys[pygame.K_d]:
            move_x += np.cos(self.angle + np.pi / 2)
            move_y += np.sin(self.angle + np.pi / 2)
        
        # Normalize movement vector
        if move_x != 0 or move_y != 0:
            length = np.sqrt(move_x * move_x + move_y * move_y)
            move_x /= length
            move_y /= length
            self.is_moving = True
        else:
            self.is_moving = False
        
        # Apply movement speed
        move_speed = PLAYER_MOVE_SPEED * delta_time
        
        # Check for running (shift key)
        if keys[pygame.K_LSHIFT] and self.spirit > 0:
            move_speed *= 1.5
            self.spirit = max(0, self.spirit - 10 * delta_time)  # Drain spirit while running
        
        # Calculate new position
        new_x = self.x + move_x * move_speed
        new_y = self.y + move_y * move_speed
        
        # Collision detection
        new_x, new_y = self.check_collision(new_x, new_y, world)
        
        # Update position
        self.x = new_x
        self.y = new_y
        
        # Handle rotation with arrow keys
        if keys[pygame.K_LEFT]:
            self.angle -= PLAYER_ROTATE_SPEED * delta_time
        if keys[pygame.K_RIGHT]:
            self.angle += PLAYER_ROTATE_SPEED * delta_time
        
        # Normalize angle
        self.angle = self.angle % (2 * np.pi)
    
    def update_mouse_look(self):
        """Handle mouse look rotation."""
        mouse_rel = pygame.mouse.get_rel()
        self.angle += mouse_rel[0] * self.mouse_sensitivity
        self.angle = self.angle % (2 * np.pi)
    
    def check_collision(self, new_x, new_y, world):
        """Check collision with walls and adjust position."""
        # Check X movement
        if self.can_move_to(new_x, self.y, world):
            final_x = new_x
        else:
            final_x = self.x
        
        # Check Y movement
        if self.can_move_to(final_x, new_y, world):
            final_y = new_y
        else:
            final_y = self.y
        
        return final_x, final_y
    
    def can_move_to(self, x, y, world):
        """Check if the player can move to the given position."""
        # Check corners of player bounding box
        corners = [
            (x - PLAYER_RADIUS, y - PLAYER_RADIUS),
            (x + PLAYER_RADIUS, y - PLAYER_RADIUS),
            (x - PLAYER_RADIUS, y + PLAYER_RADIUS),
            (x + PLAYER_RADIUS, y + PLAYER_RADIUS)
        ]
        
        for corner_x, corner_y in corners:
            map_x = int(corner_x)
            map_y = int(corner_y)
            
            if (map_x < 0 or map_x >= world.width or 
                map_y < 0 or map_y >= world.height or
                world.get_cell(map_x, map_y) > 0):
                return False
        
        return True
    
    def update_combat(self, delta_time):
        """Update combat-related timers and states."""
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= delta_time
            if self.attack_cooldown <= 0:
                self.is_attacking = False
        
        # Update spell cooldown
        if self.spell_cooldown > 0:
            self.spell_cooldown -= delta_time
        
        # Reset blocking state (must be actively held)
        self.is_blocking = False
    
    def update_stats(self, delta_time):
        """Update health, spirit, and fatigue."""
        # Natural health regeneration
        if self.health < self.max_health and self.fatigue < 50:
            self.health = min(self.max_health, self.health + HEALTH_REGEN_RATE * delta_time)
        
        # Natural spirit regeneration
        if self.spirit < self.max_spirit:
            regen_rate = SPIRIT_REGEN_RATE
            if self.fatigue > 75:
                regen_rate *= 0.5  # Slower regen when very fatigued
            self.spirit = min(self.max_spirit, self.spirit + regen_rate * delta_time)
        
        # Fatigue decay
        if self.fatigue > 0 and not self.is_moving:
            self.fatigue = max(0, self.fatigue - 5 * delta_time)
        
        # Apply fatigue effects
        if self.is_moving:
            self.fatigue = min(100, self.fatigue + FATIGUE_RATE * delta_time)
    
    def handle_input_actions(self, keys):
        """Handle discrete input actions."""
        # Weapon switching
        if keys[pygame.K_1] and pygame.K_1 not in self.keys_pressed:
            self.switch_to_weapon_slot(0)
        elif keys[pygame.K_2] and pygame.K_2 not in self.keys_pressed:
            self.switch_to_weapon_slot(1)
        elif keys[pygame.K_3] and pygame.K_3 not in self.keys_pressed:
            self.switch_to_weapon_slot(2)
        
        # Spell switching
        if keys[pygame.K_q] and pygame.K_q not in self.keys_pressed:
            self.cycle_spell()
        
        # Use item
        if keys[pygame.K_e] and pygame.K_e not in self.keys_pressed:
            self.use_item()
    
    def attack(self):
        """Perform an attack with the equipped weapon."""
        if self.attack_cooldown > 0 or self.equipped_weapon is None:
            return False
        
        self.is_attacking = True
        self.attack_cooldown = self.equipped_weapon.attack_speed
        
        # Add fatigue for attacking
        self.fatigue = min(100, self.fatigue + 5)
        
        return True
    
    def block(self):
        """Attempt to block with equipped shield."""
        if self.equipped_shield is not None:
            self.is_blocking = True
            return True
        return False
    
    def cast_spell(self, spell):
        """Cast a spell if possible."""
        if (self.spell_cooldown > 0 or 
            spell is None or 
            self.spirit < spell.cost):
            return False
        
        self.current_spell = spell
        self.spell_cooldown = spell.cooldown
        self.spirit -= spell.cost
        
        # Add fatigue for spell casting
        self.fatigue = min(100, self.fatigue + spell.cost / 2)
        
        return True
    
    def take_damage(self, damage):
        """Apply damage to the player."""
        if self.is_blocking and self.equipped_shield:
            damage *= BLOCK_REDUCTION
        
        self.health = max(0, self.health - damage)
        
        # Add fatigue when taking damage
        self.fatigue = min(100, self.fatigue + damage / 2)
    
    def heal(self, amount):
        """Heal the player."""
        self.health = min(self.max_health, self.health + amount)
    
    def restore_spirit(self, amount):
        """Restore spirit to the player."""
        self.spirit = min(self.max_spirit, self.spirit + amount)
    
    def switch_to_weapon_slot(self, slot):
        """Switch to a weapon in the given inventory slot."""
        if slot < len(self.inventory):
            item = self.inventory[slot]
            if hasattr(item, 'type') and item.type in ['melee', 'ranged', 'magic']:
                self.equipped_weapon = item
    
    def cycle_spell(self):
        """Cycle through available spells."""
        # This would cycle through learned spells
        # For now, just a placeholder
        pass
    
    def use_item(self):
        """Use an item from inventory."""
        # Placeholder for item usage
        pass
    
    def add_to_inventory(self, item):
        """Add an item to the player's inventory."""
        self.inventory.append(item)
    
    def remove_from_inventory(self, item):
        """Remove an item from the player's inventory."""
        if item in self.inventory:
            self.inventory.remove(item)
    
    def gain_experience(self, amount):
        """Gain experience points."""
        self.experience += amount
        
        # Check for level up
        exp_needed = self.level * 100  # Simple leveling formula
        if self.experience >= exp_needed:
            self.level_up()
    
    def level_up(self):
        """Level up the player character."""
        self.level += 1
        self.experience = 0
        
        # Increase stats
        self.max_health += 10
        self.max_spirit += 5
        self.health = self.max_health  # Full heal on level up
        self.spirit = self.max_spirit
    
    def to_dict(self):
        """Convert player state to dictionary for saving."""
        return {
            'x': self.x,
            'y': self.y,
            'angle': self.angle,
            'health': self.health,
            'max_health': self.max_health,
            'spirit': self.spirit,
            'max_spirit': self.max_spirit,
            'fatigue': self.fatigue,
            'level': self.level,
            'experience': self.experience,
            'inventory': [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in self.inventory]
        }
    
    def from_dict(self, data):
        """Load player state from dictionary."""
        self.x = data.get('x', self.x)
        self.y = data.get('y', self.y)
        self.angle = data.get('angle', self.angle)
        self.health = data.get('health', self.health)
        self.max_health = data.get('max_health', self.max_health)
        self.spirit = data.get('spirit', self.spirit)
        self.max_spirit = data.get('max_spirit', self.max_spirit)
        self.fatigue = data.get('fatigue', self.fatigue)
        self.level = data.get('level', self.level)
        self.experience = data.get('experience', self.experience)
        # Note: Inventory loading would need more complex item reconstruction
