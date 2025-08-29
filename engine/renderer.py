"""
Main rendering engine for the pseudo-3D RPG.
Handles wall rendering, sprite rendering, and visual effects.
"""

import pygame
import numpy as np
from numba import jit
from config import *

class Renderer:
    def __init__(self, screen, asset_manager):
        """Initialize the renderer with screen surface and asset manager."""
        self.screen = screen
        self.asset_manager = asset_manager
        self.z_buffer = np.zeros(SCREEN_WIDTH)
        
        # Pre-calculate wall heights for optimization
        self.wall_heights = np.zeros(SCREEN_WIDTH)
        
    def render_walls(self, rays):
        """Render walls using optimized batch operations."""
        # Extract distances and update z-buffer in batch
        distances = np.array([ray['distance'] if ray['hit'] else float('inf') for ray in rays])
        self.z_buffer = distances
        
        # Render wall slices
        for i, ray in enumerate(rays):
            if ray['hit'] and ray['distance'] > 0.001:  # Avoid division by zero
                self.render_wall_slice(i, ray)
                
    def render_wall_slice(self, x, ray):
        """Render a single vertical slice of a wall."""
        # Calculate wall height on screen
        distance = ray['distance']
        if distance == 0:
            distance = 0.001  # Prevent division by zero
            
        wall_height = int(SCREEN_HEIGHT / distance)
        
        # Calculate wall start and end positions
        wall_start = max(0, (SCREEN_HEIGHT - wall_height) // 2)
        wall_end = min(SCREEN_HEIGHT, (SCREEN_HEIGHT + wall_height) // 2)
        
        # Store z-buffer value
        self.z_buffer[x] = distance
        
        # Get wall texture
        texture = self.asset_manager.get_texture(ray['texture_id'])
        if texture is None:
            # Fallback to solid color
            color = self.get_wall_color(ray['texture_id'])
            pygame.draw.line(self.screen, color, (x, wall_start), (x, wall_end))
            return
            
        # Calculate texture coordinates
        tex_x = int(ray['texture_x'] * texture.get_width()) % texture.get_width()
        
        # Apply distance-based shading
        shade_factor = min(1.0, 5.0 / distance)
        
        # Render textured wall slice
        self.render_textured_wall_slice(
            x, wall_start, wall_end, texture, tex_x, shade_factor
        )
    
    def render_textured_wall_slice(self, x, wall_start, wall_end, texture, tex_x, shade_factor):
        """Render a textured wall slice with shading using optimized array operations."""
        wall_height = wall_end - wall_start
        if wall_height <= 0:
            return
            
        tex_height = texture.get_height()
        
        # Get texture column as array for faster access
        try:
            texture_array = pygame.surfarray.array3d(texture)
            screen_array = pygame.surfarray.pixels3d(self.screen)
            
            # Vectorized texture sampling
            y_coords = np.arange(wall_start, wall_end)
            tex_y_coords = ((y_coords - wall_start) / wall_height * tex_height).astype(np.int32) % tex_height
            
            # Sample texture column
            tex_colors = texture_array[tex_x, tex_y_coords]
            
            # Apply shading
            shaded_colors = (tex_colors * shade_factor).astype(np.uint8)
            
            # Copy to screen
            screen_array[x, wall_start:wall_end] = shaded_colors.T
            
        except (IndexError, ValueError):
            # Fallback to simple colored line
            color = (int(128 * shade_factor), int(128 * shade_factor), int(128 * shade_factor))
            pygame.draw.line(self.screen, color, (x, wall_start), (x, wall_end))
    
    def get_wall_color(self, texture_id):
        """Get fallback color for wall texture ID."""
        colors = {
            1: (128, 128, 128),  # Gray stone
            2: (139, 69, 19),    # Brown wood
            3: (105, 105, 105),  # Dark gray
            4: (160, 82, 45),    # Saddle brown
        }
        return colors.get(texture_id, (100, 100, 100))
    
    def render_sprites(self, sprites, player_x, player_y, player_angle):
        """Render sprites (enemies, items) in 3D space."""
        # Sort sprites by distance (back to front)
        sprite_distances = []
        for sprite in sprites:
            dx = sprite.x - player_x
            dy = sprite.y - player_y
            distance = np.sqrt(dx * dx + dy * dy)
            sprite_distances.append((distance, sprite))
        
        # Sort by distance (farthest first)
        sprite_distances.sort(key=lambda x: x[0], reverse=True)
        
        # Render each sprite
        for distance, sprite in sprite_distances:
            self.render_sprite(sprite, player_x, player_y, player_angle, distance)
    
    def render_sprite(self, sprite, player_x, player_y, player_angle, distance):
        """Render a single sprite in 3D space."""
        if distance > MAX_RENDER_DISTANCE:
            return
            
        # Calculate sprite position relative to player
        dx = sprite.x - player_x
        dy = sprite.y - player_y
        
        # Transform to camera space
        cos_a = np.cos(-player_angle)
        sin_a = np.sin(-player_angle)
        
        sprite_x = dx * cos_a - dy * sin_a
        sprite_y = dx * sin_a + dy * cos_a
        
        # Skip sprites behind the player
        if sprite_y <= 0.1:
            return
            
        # Project to screen coordinates
        screen_x = int(SCREEN_WIDTH / 2 + (sprite_x / sprite_y) * (SCREEN_WIDTH / 2) / np.tan(FOV / 2))
        
        # Calculate sprite size based on distance
        sprite_size = int(SCREEN_HEIGHT / sprite_y)
        
        # Skip sprites outside screen bounds
        if screen_x < -sprite_size or screen_x > SCREEN_WIDTH + sprite_size:
            return
            
        # Get sprite texture
        texture = self.asset_manager.get_sprite_texture(sprite.sprite_id)
        if texture is None:
            # Fallback to colored rectangle
            self.render_sprite_fallback(screen_x, sprite_size, sprite_y, sprite.color)
            return
            
        # Scale texture to sprite size
        scaled_texture = pygame.transform.scale(texture, (sprite_size, sprite_size))
        
        # Calculate sprite position on screen
        sprite_screen_y = (SCREEN_HEIGHT - sprite_size) // 2
        sprite_rect = pygame.Rect(
            screen_x - sprite_size // 2, 
            sprite_screen_y, 
            sprite_size, 
            sprite_size
        )
        
        # Check z-buffer for visibility
        if self.is_sprite_visible(sprite_rect, sprite_y):
            # Apply distance-based shading
            shade_factor = min(1.0, 3.0 / distance)
            shaded_texture = self.apply_sprite_shading(scaled_texture, shade_factor)
            
            self.screen.blit(shaded_texture, sprite_rect)
    
    def render_sprite_fallback(self, screen_x, sprite_size, depth, color):
        """Render a fallback colored rectangle for sprites without textures."""
        sprite_rect = pygame.Rect(
            screen_x - sprite_size // 2,
            (SCREEN_HEIGHT - sprite_size) // 2,
            sprite_size,
            sprite_size
        )
        
        # Check z-buffer
        if self.is_sprite_visible(sprite_rect, depth):
            pygame.draw.rect(self.screen, color, sprite_rect)
    
    def is_sprite_visible(self, sprite_rect, depth):
        """Check if sprite is visible using vectorized z-buffer operations."""
        start_x = max(0, sprite_rect.left)
        end_x = min(SCREEN_WIDTH, sprite_rect.right)
        
        if start_x >= end_x or end_x > len(self.z_buffer):
            return False
            
        # Vectorized comparison
        relevant_depths = self.z_buffer[start_x:end_x]
        return np.any(depth < relevant_depths)
    
    def apply_sprite_shading(self, texture, shade_factor):
        """Apply distance-based shading to sprite texture."""
        if shade_factor >= 1.0:
            return texture
            
        # Create a shaded copy
        shaded = texture.copy()
        
        # Apply color multiplication for shading
        color_filter = pygame.Surface(texture.get_size())
        color_filter.fill((
            int(255 * shade_factor),
            int(255 * shade_factor),
            int(255 * shade_factor)
        ))
        
        shaded.blit(color_filter, (0, 0), special_flags=pygame.BLEND_MULT)
        return shaded
    
    def render_weapon(self, weapon):
        """Render the equipped weapon in first-person view."""
        if weapon is None:
            return
            
        weapon_texture = self.asset_manager.get_weapon_texture(weapon.type)
        if weapon_texture is None:
            return
            
        # Position weapon in bottom-right of screen
        weapon_size = (weapon_texture.get_width() * 2, weapon_texture.get_height() * 2)
        scaled_weapon = pygame.transform.scale(weapon_texture, weapon_size)
        
        weapon_pos = (
            SCREEN_WIDTH - weapon_size[0] - 20,
            SCREEN_HEIGHT - weapon_size[1] - 20
        )
        
        self.screen.blit(scaled_weapon, weapon_pos)
        
        # Render attack animation if active
        if weapon.is_attacking:
            self.render_weapon_attack_effect(weapon_pos, weapon_size)
    
    def render_weapon_attack_effect(self, weapon_pos, weapon_size):
        """Render visual effect for weapon attacks."""
        # Simple flash effect
        flash_surface = pygame.Surface(weapon_size)
        flash_surface.set_alpha(100)
        flash_surface.fill((255, 255, 255))
        self.screen.blit(flash_surface, weapon_pos)
    
    def render_spell_effects(self, effects):
        """Render active spell effects."""
        for effect in effects:
            if effect.type == "fireball":
                self.render_fireball_effect(effect)
            elif effect.type == "heal":
                self.render_heal_effect(effect)
            elif effect.type == "shield":
                self.render_shield_effect(effect)
    
    def render_fireball_effect(self, effect):
        """Render fireball spell effect."""
        # Simple particle effect
        center = (int(effect.x), int(effect.y))
        radius = int(effect.radius * 10)
        
        # Animated fire colors
        colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0)]
        color = colors[int(effect.animation_time * 10) % len(colors)]
        
        pygame.draw.circle(self.screen, color, center, radius)
    
    def render_heal_effect(self, effect):
        """Render healing spell effect."""
        # Green sparkles around target
        center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        for i in range(5):
            angle = effect.animation_time * 5 + i * np.pi * 2 / 5
            x = center[0] + int(np.cos(angle) * 30)
            y = center[1] + int(np.sin(angle) * 30)
            pygame.draw.circle(self.screen, (0, 255, 0), (x, y), 3)
    
    def render_shield_effect(self, effect):
        """Render shield spell effect."""
        # Blue glow around screen edges
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(30)
        overlay.fill((0, 0, 255))
        
        # Draw border
        pygame.draw.rect(overlay, (0, 100, 255), overlay.get_rect(), 5)
        self.screen.blit(overlay, (0, 0))
    
    def clear_z_buffer(self):
        """Clear the z-buffer for the next frame using optimized NumPy operations."""
        self.z_buffer.fill(float('inf'))
    
    def update_z_buffer_vectorized(self, distances):
        """Update z-buffer with vectorized operations for better performance."""
        if len(distances) == len(self.z_buffer):
            self.z_buffer = np.minimum(self.z_buffer, distances)
