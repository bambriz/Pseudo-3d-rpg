"""
Spell system for the pseudo-3D RPG.
Handles spell casting, effects, and magical combat.
"""

import pygame
import numpy as np
from config import *

class Spell:
    def __init__(self, name, spell_type, cost, damage, range_val, duration, cooldown, description):
        """Initialize a spell."""
        self.name = name
        self.type = spell_type  # 'damage', 'heal', 'buff', 'utility'
        self.cost = cost  # Spirit cost
        self.damage = damage
        self.range = range_val
        self.duration = duration  # Effect duration for buffs/debuffs
        self.cooldown = cooldown  # Cooldown between casts
        self.description = description
        self.level = 1
        
class SpellEffect:
    def __init__(self, spell, target, caster, duration):
        """Initialize a spell effect."""
        self.spell = spell
        self.target = target
        self.caster = caster
        self.duration = duration
        self.remaining_time = duration
        self.animation_time = 0.0
        self.x = target.x if hasattr(target, 'x') else 0
        self.y = target.y if hasattr(target, 'y') else 0

class SpellSystem:
    def __init__(self, asset_manager):
        """Initialize the spell system."""
        self.asset_manager = asset_manager
        self.active_effects = []
        self.projectiles = []
        
        # Initialize spell library
        self.spells = {}
        self.initialize_spells()
        
        # Load spell sounds
        self.spell_sounds = {}
        self.load_spell_sounds()
    
    def initialize_spells(self):
        """Initialize the default spell library."""
        # Damage spells
        self.spells['fireball'] = Spell(
            "Fireball", "damage", 15, 20, 8.0, 0.0, 2.0,
            "Launches a ball of fire at the target."
        )
        
        self.spells['lightning_bolt'] = Spell(
            "Lightning Bolt", "damage", 20, 25, 10.0, 0.0, 3.0,
            "Strikes the target with a bolt of lightning."
        )
        
        self.spells['ice_shard'] = Spell(
            "Ice Shard", "damage", 12, 15, 6.0, 0.0, 1.5,
            "Hurls a sharp shard of ice at the enemy."
        )
        
        # Healing spells
        self.spells['heal'] = Spell(
            "Heal", "heal", 10, 25, 0.0, 0.0, 1.0,
            "Restores health to the caster."
        )
        
        self.spells['greater_heal'] = Spell(
            "Greater Heal", "heal", 25, 50, 0.0, 0.0, 3.0,
            "Greatly restores health to the caster."
        )
        
        # Buff spells
        self.spells['shield'] = Spell(
            "Shield", "buff", 15, 0, 0.0, 10.0, 5.0,
            "Creates a magical barrier that reduces damage."
        )
        
        self.spells['haste'] = Spell(
            "Haste", "buff", 20, 0, 0.0, 15.0, 8.0,
            "Increases movement and attack speed."
        )
        
        # Utility spells
        self.spells['teleport'] = Spell(
            "Teleport", "utility", 25, 0, 5.0, 0.0, 10.0,
            "Instantly teleports the caster a short distance."
        )
        
        self.spells['detect_enemies'] = Spell(
            "Detect Enemies", "utility", 10, 0, 0.0, 30.0, 5.0,
            "Reveals nearby enemies for a duration."
        )
    
    def load_spell_sounds(self):
        """Load spell sound effects."""
        sound_files = {
            'fireball': 'fireball_cast.wav',
            'lightning_bolt': 'lightning_cast.wav',
            'ice_shard': 'ice_cast.wav',
            'heal': 'heal_cast.wav',
            'shield': 'shield_cast.wav',
            'teleport': 'teleport_cast.wav'
        }
        
        for spell_name, filename in sound_files.items():
            sound = self.asset_manager.get_sound(filename)
            if sound:
                self.spell_sounds[spell_name] = sound
    
    def update(self, delta_time):
        """Update spell system each frame."""
        # Update active effects
        self.update_active_effects(delta_time)
        
        # Update projectiles
        self.update_projectiles(delta_time)
    
    def update_active_effects(self, delta_time):
        """Update active spell effects."""
        for effect in self.active_effects[:]:  # Copy to avoid modification during iteration
            effect.remaining_time -= delta_time
            effect.animation_time += delta_time
            
            # Update effect position if target is moving
            if hasattr(effect.target, 'x'):
                effect.x = effect.target.x
                effect.y = effect.target.y
            
            # Remove expired effects
            if effect.remaining_time <= 0:
                self.remove_spell_effect(effect)
    
    def update_projectiles(self, delta_time):
        """Update spell projectiles."""
        for projectile in self.projectiles[:]:
            # Move projectile
            projectile['x'] += projectile['dir_x'] * projectile['speed'] * delta_time
            projectile['y'] += projectile['dir_y'] * projectile['speed'] * delta_time
            projectile['traveled'] += projectile['speed'] * delta_time
            
            # Check if projectile has traveled too far
            if projectile['traveled'] >= projectile['max_distance']:
                self.projectiles.remove(projectile)
                continue
            
            # Check for collision with walls (would need world reference)
            # This is a simplified version
            
            # Check for collision with enemies (would need enemy list)
            # This is a simplified version
    
    def cast_spell(self, spell_name, caster, target=None, target_x=None, target_y=None):
        """Cast a spell."""
        if isinstance(spell_name, str):
            spell = self.spells.get(spell_name)
        else:
            spell = spell_name  # Already a Spell object
        
        if spell is None:
            return False
        
        # Check if caster has enough spirit
        if hasattr(caster, 'spirit') and caster.spirit < spell.cost:
            return False
        
        # Deduct spirit cost
        if hasattr(caster, 'spirit'):
            caster.spirit -= spell.cost
        
        # Play spell sound
        self.play_spell_sound(spell.name.lower().replace(' ', '_'))
        
        # Handle different spell types
        if spell.type == 'damage':
            return self.cast_damage_spell(spell, caster, target, target_x, target_y)
        elif spell.type == 'heal':
            return self.cast_heal_spell(spell, caster, target)
        elif spell.type == 'buff':
            return self.cast_buff_spell(spell, caster, target)
        elif spell.type == 'utility':
            return self.cast_utility_spell(spell, caster, target_x, target_y)
        
        return False
    
    def cast_damage_spell(self, spell, caster, target, target_x, target_y):
        """Cast a damage spell."""
        if target is not None:
            # Direct target spell
            if hasattr(target, 'take_damage'):
                damage = self.calculate_spell_damage(spell, caster)
                target.take_damage(damage)
                
                # Create visual effect
                effect = SpellEffect(spell, target, caster, 1.0)
                self.active_effects.append(effect)
                
                return True
        elif target_x is not None and target_y is not None:
            # Projectile spell
            projectile = self.create_spell_projectile(spell, caster, target_x, target_y)
            if projectile:
                self.projectiles.append(projectile)
                return True
        
        return False
    
    def cast_heal_spell(self, spell, caster, target=None):
        """Cast a healing spell."""
        heal_target = target if target is not None else caster
        
        if hasattr(heal_target, 'heal'):
            heal_amount = spell.damage  # For heal spells, 'damage' is heal amount
            heal_target.heal(heal_amount)
            
            # Create visual effect
            effect = SpellEffect(spell, heal_target, caster, 2.0)
            self.active_effects.append(effect)
            
            return True
        
        return False
    
    def cast_buff_spell(self, spell, caster, target=None):
        """Cast a buff spell."""
        buff_target = target if target is not None else caster
        
        # Create buff effect
        effect = SpellEffect(spell, buff_target, caster, spell.duration)
        self.active_effects.append(effect)
        
        # Apply immediate buff effects
        if spell.name.lower() == 'shield':
            if hasattr(buff_target, 'shield_bonus'):
                buff_target.shield_bonus += 10
            else:
                buff_target.shield_bonus = 10
        elif spell.name.lower() == 'haste':
            if hasattr(buff_target, 'speed_bonus'):
                buff_target.speed_bonus += 0.5
            else:
                buff_target.speed_bonus = 0.5
        
        return True
    
    def cast_utility_spell(self, spell, caster, target_x, target_y):
        """Cast a utility spell."""
        if spell.name.lower() == 'teleport':
            return self.cast_teleport(spell, caster, target_x, target_y)
        elif spell.name.lower() == 'detect_enemies':
            return self.cast_detect_enemies(spell, caster)
        
        return False
    
    def cast_teleport(self, spell, caster, target_x, target_y):
        """Cast teleport spell."""
        # Calculate distance
        dx = target_x - caster.x
        dy = target_y - caster.y
        distance = np.sqrt(dx * dx + dy * dy)
        
        if distance > spell.range:
            return False
        
        # TODO: Check if target location is valid (no walls, no enemies)
        # For now, just teleport
        caster.x = target_x
        caster.y = target_y
        
        # Create visual effect
        effect = SpellEffect(spell, caster, caster, 1.0)
        self.active_effects.append(effect)
        
        return True
    
    def cast_detect_enemies(self, spell, caster):
        """Cast detect enemies spell."""
        # Create detection effect
        effect = SpellEffect(spell, caster, caster, spell.duration)
        self.active_effects.append(effect)
        
        # TODO: Set detection flag on caster
        if hasattr(caster, 'can_detect_enemies'):
            caster.can_detect_enemies = True
        
        return True
    
    def cast_area_spell(self, spell_name, center_x, center_y, radius=2.0):
        """Cast an area effect spell."""
        spell = self.spells.get(spell_name)
        if spell is None:
            return False
        
        # Create area effect
        area_effect = {
            'spell': spell,
            'x': center_x,
            'y': center_y,
            'radius': radius,
            'duration': 3.0,
            'damage_per_second': spell.damage / 3.0
        }
        
        # Add to active effects (simplified)
        effect = SpellEffect(spell, None, None, 3.0)
        effect.x = center_x
        effect.y = center_y
        effect.radius = radius
        effect.type = 'area'
        self.active_effects.append(effect)
        
        return True
    
    def create_spell_projectile(self, spell, caster, target_x, target_y):
        """Create a spell projectile."""
        # Calculate direction
        dx = target_x - caster.x
        dy = target_y - caster.y
        distance = np.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return None
        
        # Normalize direction
        dir_x = dx / distance
        dir_y = dy / distance
        
        projectile = {
            'spell': spell,
            'x': caster.x,
            'y': caster.y,
            'dir_x': dir_x,
            'dir_y': dir_y,
            'speed': 8.0,  # Units per second
            'damage': self.calculate_spell_damage(spell, caster),
            'max_distance': spell.range,
            'traveled': 0.0,
            'caster': caster,
            'type': 'projectile'
        }
        
        return projectile
    
    def calculate_spell_damage(self, spell, caster):
        """Calculate damage for a spell."""
        base_damage = spell.damage
        
        # Add caster level bonus
        level_bonus = caster.level * 1.5 if hasattr(caster, 'level') else 0
        
        # Add spell level bonus
        spell_level_bonus = spell.level * 2
        
        # Add random variation
        damage_variation = np.random.uniform(0.9, 1.1)
        
        # Apply intelligence bonus if applicable
        int_bonus = 1.0
        if hasattr(caster, 'intelligence'):
            int_bonus = 1.0 + (caster.intelligence - 10) * 0.05
        
        final_damage = int(
            (base_damage + level_bonus + spell_level_bonus) * 
            damage_variation * 
            int_bonus
        )
        
        return max(1, final_damage)
    
    def remove_spell_effect(self, effect):
        """Remove a spell effect and clean up."""
        if effect in self.active_effects:
            # Remove buff effects
            if effect.spell.type == 'buff':
                if effect.spell.name.lower() == 'shield':
                    if hasattr(effect.target, 'shield_bonus'):
                        effect.target.shield_bonus = max(0, effect.target.shield_bonus - 10)
                elif effect.spell.name.lower() == 'haste':
                    if hasattr(effect.target, 'speed_bonus'):
                        effect.target.speed_bonus = max(0, effect.target.speed_bonus - 0.5)
            
            self.active_effects.remove(effect)
    
    def play_spell_sound(self, spell_name):
        """Play a spell sound effect."""
        if spell_name in self.spell_sounds:
            self.spell_sounds[spell_name].play()
    
    def get_spell(self, spell_name):
        """Get a spell by name."""
        return self.spells.get(spell_name)
    
    def learn_spell(self, caster, spell_name):
        """Teach a spell to the caster."""
        spell = self.spells.get(spell_name)
        if spell is None:
            return False
        
        if not hasattr(caster, 'known_spells'):
            caster.known_spells = []
        
        if spell not in caster.known_spells:
            caster.known_spells.append(spell)
            return True
        
        return False
    
    def get_active_effects_for_target(self, target):
        """Get all active effects affecting a specific target."""
        return [effect for effect in self.active_effects if effect.target == target]
    
    def has_active_buff(self, target, buff_name):
        """Check if target has a specific buff active."""
        for effect in self.active_effects:
            if (effect.target == target and 
                effect.spell.type == 'buff' and 
                effect.spell.name.lower() == buff_name.lower()):
                return True
        return False
