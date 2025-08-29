"""
Mode 7-style rendering for floors and ceilings.
Creates pseudo-3D depth perception for horizontal surfaces.
"""

import pygame
import numpy as np
from numba import jit
from config import *

class Mode7Renderer:
    def __init__(self, asset_manager):
        """Initialize Mode 7 renderer."""
        self.asset_manager = asset_manager
        
        # Pre-calculate perspective lookup tables for optimization
        self.perspective_table = self.generate_perspective_table()
        
        # Floor and ceiling surfaces
        self.floor_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        self.ceiling_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        
    def generate_perspective_table(self):
        """Pre-calculate perspective transformation values."""
        table = np.zeros((SCREEN_HEIGHT // 2, SCREEN_WIDTH, 2))
        
        for y in range(SCREEN_HEIGHT // 2):
            screen_y = HORIZON_HEIGHT + y
            if screen_y >= SCREEN_HEIGHT:
                continue
                
            # Distance to the floor
            p = SCREEN_HEIGHT // 2
            pos_z = p / (screen_y - p) if screen_y != p else 0.001
            
            for x in range(SCREEN_WIDTH):
                # Horizontal distance from camera center
                screen_x = x - SCREEN_WIDTH // 2
                pos_x = screen_x * pos_z / (SCREEN_WIDTH // 2)
                
                table[y, x, 0] = pos_x
                table[y, x, 1] = pos_z
                
        return table
    
    def render_floor_ceiling(self, screen, player_x, player_y, player_angle):
        """Render floor and ceiling using Mode 7 perspective."""
        # Get floor and ceiling textures
        floor_texture = self.asset_manager.get_texture("floor")
        ceiling_texture = self.asset_manager.get_texture("ceiling")
        
        if floor_texture is None:
            floor_texture = self.create_default_floor_texture()
        if ceiling_texture is None:
            ceiling_texture = self.create_default_ceiling_texture()
            
        # Render floor
        self.render_horizontal_surface(
            self.floor_surface, floor_texture, player_x, player_y, player_angle, False
        )
        
        # Render ceiling
        self.render_horizontal_surface(
            self.ceiling_surface, ceiling_texture, player_x, player_y, player_angle, True
        )
        
        # Blit to main screen
        screen.blit(self.floor_surface, (0, HORIZON_HEIGHT))
        
        # Flip ceiling vertically and blit to top half
        flipped_ceiling = pygame.transform.flip(self.ceiling_surface, False, True)
        screen.blit(flipped_ceiling, (0, 0))
    
    def render_horizontal_surface(self, surface, texture, player_x, player_y, player_angle, is_ceiling):
        """Render a horizontal surface using optimized Numba function."""
        surface.fill((0, 0, 0))  # Clear surface
        
        # Rotation matrix for player angle
        cos_a = np.cos(player_angle)
        sin_a = np.sin(player_angle)
        
        texture_width = texture.get_width()
        texture_height = texture.get_height()
        
        try:
            # Get arrays for fast processing
            texture_array = pygame.surfarray.array3d(texture)
            surface_array = pygame.surfarray.pixels3d(surface)
            
            # Use optimized Numba function
            fast_mode7_render(
                texture_array, surface_array, self.perspective_table,
                player_x, player_y, cos_a, sin_a,
                texture_width, texture_height, MAX_RENDER_DISTANCE
            )
            
        except Exception:
            # Fallback to simple fill
            if is_ceiling:
                surface.fill(CEILING_COLOR)
            else:
                surface.fill(FLOOR_COLOR)
    
    def create_default_floor_texture(self):
        """Create a default procedural floor texture."""
        texture = pygame.Surface((FLOOR_TEXTURE_SIZE, FLOOR_TEXTURE_SIZE))
        
        for y in range(FLOOR_TEXTURE_SIZE):
            for x in range(FLOOR_TEXTURE_SIZE):
                # Checkerboard pattern
                if (x // 8 + y // 8) % 2:
                    color = (120, 80, 40)  # Darker brown
                else:
                    color = (100, 70, 35)  # Brown
                    
                # Add some noise
                noise = np.random.randint(-10, 10)
                color = (
                    max(0, min(255, color[0] + noise)),
                    max(0, min(255, color[1] + noise)),
                    max(0, min(255, color[2] + noise))
                )
                
                texture.set_at((x, y), color)
                
        return texture
    
    def create_default_ceiling_texture(self):
        """Create a default procedural ceiling texture."""
        texture = pygame.Surface((CEILING_TEXTURE_SIZE, CEILING_TEXTURE_SIZE))
        
        for y in range(CEILING_TEXTURE_SIZE):
            for x in range(CEILING_TEXTURE_SIZE):
                # Stone-like pattern
                base_color = 80
                variation = int(20 * np.sin(x * 0.3) * np.cos(y * 0.3))
                
                gray_value = max(40, min(120, base_color + variation))
                color = (gray_value, gray_value, gray_value)
                
                texture.set_at((x, y), color)
                
        return texture

@jit(nopython=True)
def fast_mode7_render(texture_array, surface_array, perspective_table, 
                      player_x, player_y, cos_a, sin_a, 
                      texture_width, texture_height, max_distance):
    """Numba-optimized Mode 7 rendering for better performance."""
    height, width = surface_array.shape[:2]
    
    for y in range(height):
        for x in range(width):
            if y < perspective_table.shape[0] and x < perspective_table.shape[1]:
                world_x = perspective_table[y, x, 0]
                world_z = perspective_table[y, x, 1]
                
                # Apply rotation
                rotated_x = world_x * cos_a - world_z * sin_a
                rotated_z = world_x * sin_a + world_z * cos_a
                
                # Add player position
                final_x = rotated_x + player_x
                final_z = rotated_z + player_y
                
                # Calculate texture coordinates
                tex_x = int(final_x * texture_width) % texture_width
                tex_z = int(final_z * texture_height) % texture_height
                
                # Bounds checking
                if 0 <= tex_x < texture_width and 0 <= tex_z < texture_height:
                    # Get color from texture
                    color = texture_array[tex_x, tex_z]
                    
                    # Apply distance fog
                    distance = np.sqrt(world_x * world_x + world_z * world_z)
                    fog_factor = max(0.3, 1.0 - distance / max_distance)
                    
                    # Apply fog to color
                    surface_array[x, y, 0] = int(color[0] * fog_factor)
                    surface_array[x, y, 1] = int(color[1] * fog_factor)
                    surface_array[x, y, 2] = int(color[2] * fog_factor)
