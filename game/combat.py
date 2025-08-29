"""
Combat system for the pseudo-3D RPG.
Handles weapon mechanics, damage calculation, and combat animations.
"""

import pygame
import numpy as np
from config import *

class Weapon:
    def __init__(self, name, weapon_type, damage, attack_speed, range_val, sprite_id):
        """Initialize a weapon."""
        self.name = name
        self.type = weapon_type  # 'melee', 'ranged', 'magic'
        self.damage = damage
        self.attack_speed = attack_speed  # Cooldown between attacks
        self.range = range_val
        self.sprite_id = sprite_id
        self.durability = 100
        self.is_attacking = False
        self.attack_animation_time = 0.0

class Shield:
    def __init__(self, name, defense, durability):
        """Initialize a shield."""
        self.name = name
        self.defense = defense
        self.durability = durability

class CombatSystem:
    def __init__(self, asset_manager):
        """Initialize the combat system."""
        self.asset_manager = asset_manager
        self.active_attacks = []
        
        # Initialize default weapons
        self.weapons = {
            'sword': Weapon("Iron Sword", "melee", 15, 1.0, 1.5, "sword"),
            'dagger': Weapon("Steel Dagger", "melee", 8, 0.5, 1.0, "dagger"),
            'axe': Weapon("Battle Axe", "melee", 20, 1.5, 1.2, "axe"),
            'spear': Weapon("Long Spear", "melee", 12, 1.2, 2.0, "spear"),
            'bow': Weapon("Hunting Bow", "ranged", 10, 2.0, 8.0, "bow"),
            'wand': Weapon("Magic Wand", "magic", 5, 0.8, 5.0, "wand"),
            'staff': Weapon("Wizard Staff", "magic", 8, 1.0, 6.0, "staff")
        }
        
        # Initialize shields
        self.shields = {
            'wooden_shield': Shield("Wooden Shield", 5, 80),
            'iron_shield': Shield("Iron Shield", 8, 120),
            'steel_shield': Shield("Steel Shield", 12, 150)
        }
        
        # Combat sound effects
        self.combat_sounds = {}
        self.load_combat_sounds()
    
    def load_combat_sounds(self):
        """Load combat sound effects."""
        sound_files = {
            'sword_hit': 'sword_clang.wav',
            'bow_shoot': 'bow_release.wav',
            'spell_cast': 'magic_cast.wav',
            'block': 'shield_block.wav',
            'enemy_hit': 'enemy_grunt.wav'
        }
        
        for sound_name, filename in sound_files.items():
            sound = self.asset_manager.get_sound(filename)
            if sound:
                self.combat_sounds[sound_name] = sound
    
    def update(self, delta_time):
        """Update combat system each frame."""
        # Update active attacks
        self.update_active_attacks(delta_time)
        
        # Update weapon animations
        for weapon in self.weapons.values():
            if weapon.is_attacking:
                weapon.attack_animation_time += delta_time
                if weapon.attack_animation_time >= weapon.attack_speed:
                    weapon.is_attacking = False
                    weapon.attack_animation_time = 0.0
    
    def update_active_attacks(self, delta_time):
        """Update active attack effects."""
        for attack in self.active_attacks[:]:  # Copy list to avoid modification during iteration
            attack['duration'] -= delta_time
            if attack['duration'] <= 0:
                self.active_attacks.remove(attack)
    
    def perform_attack(self, attacker, weapon, target_x, target_y):
        """Perform an attack with the given weapon."""
        if weapon is None:
            return False
        
        # Calculate distance to target
        distance = np.sqrt((target_x - attacker.x)**2 + (target_y - attacker.y)**2)
        
        # Check if target is in range
        if distance > weapon.range:
            return False
        
        # Check if attack is on cooldown
        if weapon.is_attacking:
            return False
        
        # Start attack animation
        weapon.is_attacking = True
        weapon.attack_animation_time = 0.0
        
        # Calculate damage
        damage = self.calculate_damage(attacker, weapon)
        
        # Create attack effect
        attack_effect = {
            'type': weapon.type,
            'x': target_x,
            'y': target_y,
            'damage': damage,
            'duration': 0.3,  # Visual effect duration
            'attacker': attacker
        }
        self.active_attacks.append(attack_effect)
        
        # Play attack sound
        self.play_attack_sound(weapon)
        
        return True
    
    def calculate_damage(self, attacker, weapon):
        """Calculate damage for an attack."""
        base_damage = weapon.damage
        
        # Add attacker level bonus
        level_bonus = attacker.level * 2 if hasattr(attacker, 'level') else 0
        
        # Add random variation
        damage_variation = np.random.uniform(0.8, 1.2)
        
        # Calculate critical hit
        critical_hit = np.random.random() < CRITICAL_HIT_CHANCE
        critical_multiplier = 2.0 if critical_hit else 1.0
        
        # Apply fatigue penalty if applicable
        fatigue_penalty = 1.0
        if hasattr(attacker, 'fatigue'):
            fatigue_penalty = max(0.5, 1.0 - attacker.fatigue / 200)
        
        final_damage = int(
            (base_damage + level_bonus) * 
            damage_variation * 
            critical_multiplier * 
            fatigue_penalty
        )
        
        return max(1, final_damage)  # Minimum 1 damage
    
    def apply_damage(self, target, damage, damage_type="physical"):
        """Apply damage to a target."""
        if not hasattr(target, 'take_damage'):
            return False
        
        # Apply damage reduction if target is blocking
        if hasattr(target, 'is_blocking') and target.is_blocking:
            if hasattr(target, 'equipped_shield') and target.equipped_shield:
                damage = max(1, damage - target.equipped_shield.defense)
                damage = int(damage * BLOCK_REDUCTION)
                self.play_sound('block')
        
        # Apply the damage
        target.take_damage(damage)
        
        # Play hit sound
        self.play_sound('enemy_hit')
        
        return True
    
    def check_melee_hit(self, attacker, weapon, world, enemies):
        """Check for melee weapon hits."""
        if weapon.type != 'melee':
            return []
        
        hit_enemies = []
        
        # Calculate attack direction
        attack_angle = attacker.angle
        attack_range = weapon.range
        
        # Check for enemies in attack arc
        for enemy in enemies:
            # Calculate distance and angle to enemy
            dx = enemy.x - attacker.x
            dy = enemy.y - attacker.y
            distance = np.sqrt(dx * dx + dy * dy)
            
            if distance <= attack_range:
                # Calculate angle to enemy
                enemy_angle = np.arctan2(dy, dx)
                angle_diff = abs(enemy_angle - attack_angle)
                
                # Normalize angle difference
                if angle_diff > np.pi:
                    angle_diff = 2 * np.pi - angle_diff
                
                # Check if enemy is in attack arc (45-degree cone)
                if angle_diff <= np.pi / 4:
                    hit_enemies.append(enemy)
        
        return hit_enemies
    
    def check_ranged_hit(self, attacker, weapon, target_x, target_y, world):
        """Check if a ranged attack hits."""
        if weapon.type != 'ranged':
            return False
        
        # Calculate trajectory
        dx = target_x - attacker.x
        dy = target_y - attacker.y
        distance = np.sqrt(dx * dx + dy * dy)
        
        if distance > weapon.range:
            return False
        
        # Check for obstacles in the path
        steps = int(distance * 10)  # 10 steps per unit
        for i in range(1, steps):
            progress = i / steps
            check_x = attacker.x + dx * progress
            check_y = attacker.y + dy * progress
            
            map_x = int(check_x)
            map_y = int(check_y)
            
            if (map_x < 0 or map_x >= world.width or 
                map_y < 0 or map_y >= world.height or
                world.get_cell(map_x, map_y) > 0):
                return False  # Hit a wall
        
        return True
    
    def create_projectile(self, attacker, weapon, target_x, target_y):
        """Create a projectile for ranged attacks."""
        if weapon.type != 'ranged':
            return None
        
        # Calculate direction
        dx = target_x - attacker.x
        dy = target_y - attacker.y
        distance = np.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return None
        
        # Normalize direction
        dir_x = dx / distance
        dir_y = dy / distance
        
        projectile = {
            'x': attacker.x,
            'y': attacker.y,
            'dir_x': dir_x,
            'dir_y': dir_y,
            'speed': 10.0,  # Units per second
            'damage': self.calculate_damage(attacker, weapon),
            'max_distance': weapon.range,
            'traveled': 0.0,
            'weapon_type': weapon.type,
            'sprite_id': weapon.sprite_id + '_projectile'
        }
        
        return projectile
    
    def play_attack_sound(self, weapon):
        """Play appropriate sound for weapon attack."""
        sound_map = {
            'melee': 'sword_hit',
            'ranged': 'bow_shoot',
            'magic': 'spell_cast'
        }
        
        sound_name = sound_map.get(weapon.type, 'sword_hit')
        self.play_sound(sound_name)
    
    def play_sound(self, sound_name):
        """Play a combat sound effect."""
        if sound_name in self.combat_sounds:
            self.combat_sounds[sound_name].play()
    
    def get_weapon(self, weapon_name):
        """Get a weapon by name."""
        return self.weapons.get(weapon_name)
    
    def get_shield(self, shield_name):
        """Get a shield by name."""
        return self.shields.get(shield_name)
    
    def create_custom_weapon(self, name, weapon_type, damage, attack_speed, range_val, sprite_id):
        """Create a custom weapon."""
        weapon = Weapon(name, weapon_type, damage, attack_speed, range_val, sprite_id)
        self.weapons[name.lower().replace(' ', '_')] = weapon
        return weapon
    
    def get_attack_effects(self):
        """Get current active attack effects for rendering."""
        return self.active_attacks.copy()
