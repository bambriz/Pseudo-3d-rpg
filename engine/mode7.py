"""
Mode 7-style rendering for floors and ceilings.
Creates pseudo-3D depth perception for horizontal surfaces.
"""

import pygame
import numpy as np
from numba import jit, prange
from config import *

@jit(nopython=True, cache=True)
def optimized_mode7_render_numpy(width, height, player_x, player_y, cos_a, sin_a, 
                                texture_array, horizon_height, screen_height, 
                                texture_width, texture_height, max_render_distance):
    """Optimized Mode7 rendering using NumPy arrays and Numba JIT."""
    # Pre-allocate output array
    output = np.zeros((width, height, 3), dtype=np.uint8)
    
    # Calculate perspective values for all pixels in parallel
    p = screen_height // 2
    
    for y in prange(height):
        screen_y = horizon_height + y
        if screen_y >= screen_height or screen_y == p:
            continue
            
        # Distance to the floor - safe division
        pos_z = p / (screen_y - p) if abs(screen_y - p) > 0.001 else 0.001
        
        for x in prange(width):
            # Horizontal distance from camera center
            screen_x = x - width // 2
            pos_x = screen_x * pos_z / (width // 2) if width != 0 else 0
            
            # Apply rotation
            rotated_x = pos_x * cos_a - pos_z * sin_a
            rotated_z = pos_x * sin_a + pos_z * cos_a
            
            # Add player position
            final_x = rotated_x + player_x
            final_z = rotated_z + player_y
            
            # Scale for texture tiling - safe modulo
            tex_x = int(final_x * texture_width) % texture_width
            tex_z = int(final_z * texture_height) % texture_height
            
            # Ensure texture coordinates are within bounds
            tex_x = max(0, min(texture_width - 1, tex_x))
            tex_z = max(0, min(texture_height - 1, tex_z))
            
            # Sample texture
            color_r = texture_array[tex_x, tex_z, 0]
            color_g = texture_array[tex_x, tex_z, 1] 
            color_b = texture_array[tex_x, tex_z, 2]
            
            # Apply distance-based fog
            distance = pos_z
            fog_factor = max(0.2, 1.0 - distance / max_render_distance)
            
            # Apply fog to color
            output[x, y, 0] = int(color_r * fog_factor)
            output[x, y, 1] = int(color_g * fog_factor)
            output[x, y, 2] = int(color_b * fog_factor)
    
    return output

class Mode7Renderer:
    def __init__(self, asset_manager):
        """Initialize Mode 7 renderer."""
        self.asset_manager = asset_manager
        
        # Pre-calculate perspective lookup tables for optimization (disabled for now)
        # self.perspective_table = self.generate_perspective_table()
        
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
        """Render a horizontal surface with optimized Mode 7 perspective."""
        surface.fill((0, 0, 0))  # Clear surface
        
        # Rotation matrix for player angle
        cos_a = np.cos(player_angle)
        sin_a = np.sin(player_angle)
        
        texture_width = texture.get_width()
        texture_height = texture.get_height()
        
        try:
            # Try optimized NumPy/Numba rendering
            texture_array = pygame.surfarray.array3d(texture)
            
            # Use optimized function
            result_array = optimized_mode7_render_numpy(
                surface.get_width(), surface.get_height(),
                player_x, player_y, cos_a, sin_a,
                texture_array, HORIZON_HEIGHT, SCREEN_HEIGHT,
                texture_width, texture_height, MAX_RENDER_DISTANCE
            )
            
            # Convert back to surface
            pygame.surfarray.blit_array(surface, result_array)
            
        except Exception:
            # Fallback to working but slower pixel-by-pixel rendering
            self.render_fallback_mode7(surface, texture, player_x, player_y, player_angle, is_ceiling)
    
    def render_fallback_mode7(self, surface, texture, player_x, player_y, player_angle, is_ceiling):
        """Fallback Mode 7 rendering - pixel by pixel but guaranteed to work."""
        cos_a = np.cos(player_angle)
        sin_a = np.sin(player_angle)
        
        texture_width = texture.get_width()
        texture_height = texture.get_height()
        
        for y in range(surface.get_height()):
            for x in range(surface.get_width()):
                # Map screen coordinates to world space using perspective transformation
                screen_y = HORIZON_HEIGHT + y
                if screen_y >= SCREEN_HEIGHT:
                    continue
                    
                # Distance to the floor - safe division
                p = SCREEN_HEIGHT // 2
                pos_z = p / (screen_y - p) if abs(screen_y - p) > 0.001 else 0.001
                
                # Horizontal distance from camera center
                screen_x = x - SCREEN_WIDTH // 2
                pos_x = screen_x * pos_z / (SCREEN_WIDTH // 2) if SCREEN_WIDTH != 0 else 0
                
                # Apply rotation
                rotated_x = pos_x * cos_a - pos_z * sin_a
                rotated_z = pos_x * sin_a + pos_z * cos_a
                
                # Add player position
                final_x = rotated_x + player_x
                final_z = rotated_z + player_y
                
                # Scale for texture tiling - safe bounds
                tex_x = int(final_x * texture_width) % texture_width
                tex_z = int(final_z * texture_height) % texture_height
                
                tex_x = max(0, min(texture_width - 1, tex_x))
                tex_z = max(0, min(texture_height - 1, tex_z))
                
                # Sample texture
                try:
                    color = texture.get_at((tex_x, tex_z))
                    
                    # Apply distance-based fog
                    distance = pos_z
                    fog_factor = max(0.2, 1.0 - distance / MAX_RENDER_DISTANCE)
                    
                    fogged_color = (
                        int(color[0] * fog_factor),
                        int(color[1] * fog_factor),
                        int(color[2] * fog_factor)
                    )
                    
                    surface.set_at((x, y), fogged_color)
                except (IndexError, ValueError):
                    # Fallback color for invalid coordinates
                    if is_ceiling:
                        surface.set_at((x, y), CEILING_COLOR)
                    else:
                        surface.set_at((x, y), FLOOR_COLOR)
    
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
    
    def render_simple_mode7(self, surface, texture, player_x, player_y, player_angle, is_ceiling):
        """Simple Mode 7 rendering fallback without Numba."""
        cos_a = np.cos(player_angle)
        sin_a = np.sin(player_angle)
        
        texture_width = texture.get_width()
        texture_height = texture.get_height()
        
        for y in range(surface.get_height()):
            for x in range(surface.get_width()):
                # Calculate perspective values directly
                screen_y = y
                p = surface.get_height() // 2
                pos_z = p / (screen_y - p + 1)  # Avoid division by zero
                screen_x = x - surface.get_width() // 2
                pos_x = screen_x * pos_z / (surface.get_width() // 2)
                world_x = pos_x
                world_z = pos_z
                
                # Apply rotation
                rotated_x = world_x * cos_a - world_z * sin_a
                rotated_z = world_x * sin_a + world_z * cos_a
                
                # Add player position
                final_x = rotated_x + player_x
                final_z = rotated_z + player_y
                
                # Scale for texture tiling
                tex_x = int(final_x * texture_width) % texture_width
                tex_z = int(final_z * texture_height) % texture_height
                
                try:
                    color = texture.get_at((tex_x, tex_z))
                    
                    # Apply distance-based fog
                    distance = np.sqrt(world_x * world_x + world_z * world_z)
                    fog_factor = max(0.3, 1.0 - distance / MAX_RENDER_DISTANCE)
                    
                    fogged_color = (
                        int(color[0] * fog_factor),
                        int(color[1] * fog_factor),
                        int(color[2] * fog_factor)
                    )
                    
                    surface.set_at((x, y), fogged_color)
                except (IndexError, ValueError):
                    if is_ceiling:
                        surface.set_at((x, y), CEILING_COLOR)
                    else:
                        surface.set_at((x, y), FLOOR_COLOR)

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
