"""
Raycasting engine for pseudo-3D wall rendering.
Optimized with NumPy and Numba for performance.
"""

import numpy as np
from numba import jit
from config import *

class RayCaster:
    def __init__(self):
        """Initialize the raycasting engine."""
        # Pre-calculate ray angles for optimization
        self.ray_angles = np.linspace(-FOV / 2, FOV / 2, NUM_RAYS)
        
    def cast_rays(self, player_x, player_y, player_angle, world):
        """Cast all rays and return hit information using optimized Numba function."""
        rays = []
        world_array = world.get_map_array()  # Get NumPy array representation
        
        for i in range(NUM_RAYS):
            ray_angle = player_angle + self.ray_angles[i]
            dx = np.cos(ray_angle)
            dy = np.sin(ray_angle)
            
            # Use optimized Numba function
            hit, distance, texture_id, texture_x, side, map_x, map_y = fast_dda(
                player_x, player_y, dx, dy, world_array, world.width, world.height
            )
            
            ray_data = {
                'hit': hit,
                'distance': distance,
                'texture_id': texture_id,
                'texture_x': texture_x,
                'side': side,
                'map_x': map_x,
                'map_y': map_y
            }
            rays.append(ray_data)
            
        return rays
    
    def cast_single_ray(self, start_x, start_y, angle, world):
        """Cast a single ray and return hit information."""
        # Normalize angle
        angle = angle % (2 * np.pi)
        
        # Ray direction
        dx = np.cos(angle)
        dy = np.sin(angle)
        
        # DDA (Digital Differential Analyzer) algorithm
        return self.dda_raycast(start_x, start_y, dx, dy, world)
    
    def dda_raycast(self, start_x, start_y, dx, dy, world):
        """Perform DDA raycasting algorithm."""
        # Current position
        x, y = start_x, start_y
        
        # Which box of the map we're in
        map_x = int(x)
        map_y = int(y)
        
        # Length of ray from current position to x or y side
        if dx == 0:
            delta_dist_x = float('inf')
        else:
            delta_dist_x = abs(1 / dx)
            
        if dy == 0:
            delta_dist_y = float('inf')
        else:
            delta_dist_y = abs(1 / dy)
        
        # Calculate step and initial side_dist
        if dx < 0:
            step_x = -1
            side_dist_x = (x - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - x) * delta_dist_x
            
        if dy < 0:
            step_y = -1
            side_dist_y = (y - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - y) * delta_dist_y
        
        # Perform DDA
        hit = False
        side = 0  # Was a NS or a EW wall hit?
        
        while not hit:
            # Jump to next map square, either in x-direction, or in y-direction
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
            
            # Check if ray has hit a wall
            if (map_x < 0 or map_x >= world.width or 
                map_y < 0 or map_y >= world.height or
                world.get_cell(map_x, map_y) > 0):
                hit = True
        
        # Calculate distance
        if side == 0:
            perp_wall_dist = (map_x - x + (1 - step_x) / 2) / dx
        else:
            perp_wall_dist = (map_y - y + (1 - step_y) / 2) / dy
        
        # Calculate where exactly the wall was hit
        wall_x = y + perp_wall_dist * dy if side == 0 else x + perp_wall_dist * dx
        wall_x -= int(wall_x)
        
        # Get texture information
        texture_id = world.get_cell(map_x, map_y) if hit else 0
        
        return {
            'hit': hit,
            'distance': perp_wall_dist,
            'texture_id': texture_id,
            'texture_x': wall_x,
            'side': side,
            'map_x': map_x,
            'map_y': map_y
        }
    
    def cast_ray_for_collision(self, start_x, start_y, angle, world, max_distance):
        """Cast a ray for collision detection (simplified version)."""
        dx = np.cos(angle)
        dy = np.sin(angle)
        
        step_size = 0.1
        distance = 0
        
        x, y = start_x, start_y
        
        while distance < max_distance:
            x += dx * step_size
            y += dy * step_size
            distance += step_size
            
            map_x = int(x)
            map_y = int(y)
            
            if (map_x < 0 or map_x >= world.width or 
                map_y < 0 or map_y >= world.height or
                world.get_cell(map_x, map_y) > 0):
                return True, distance, map_x, map_y
                
        return False, max_distance, int(x), int(y)

@jit(nopython=True)
def fast_dda(start_x, start_y, dx, dy, world_array, world_width, world_height):
    """Numba-optimized DDA algorithm for better performance."""
    x, y = start_x, start_y
    map_x = int(x)
    map_y = int(y)
    
    if dx == 0:
        delta_dist_x = 1e30
    else:
        delta_dist_x = abs(1 / dx)
        
    if dy == 0:
        delta_dist_y = 1e30
    else:
        delta_dist_y = abs(1 / dy)
    
    if dx < 0:
        step_x = -1
        side_dist_x = (x - map_x) * delta_dist_x
    else:
        step_x = 1
        side_dist_x = (map_x + 1.0 - x) * delta_dist_x
        
    if dy < 0:
        step_y = -1
        side_dist_y = (y - map_y) * delta_dist_y
    else:
        step_y = 1
        side_dist_y = (map_y + 1.0 - y) * delta_dist_y
    
    hit = False
    side = 0
    texture_id = 0  # Initialize texture_id
    
    while not hit:
        if side_dist_x < side_dist_y:
            side_dist_x += delta_dist_x
            map_x += step_x
            side = 0
        else:
            side_dist_y += delta_dist_y
            map_y += step_y
            side = 1
        
        if (map_x < 0 or map_x >= world_width or 
            map_y < 0 or map_y >= world_height):
            hit = True
            texture_id = 1  # Default wall
        elif world_array[map_y, map_x] > 0:
            hit = True
            texture_id = world_array[map_y, map_x]
        else:
            texture_id = 0
    
    if side == 0:
        perp_wall_dist = (map_x - x + (1 - step_x) / 2) / dx
    else:
        perp_wall_dist = (map_y - y + (1 - step_y) / 2) / dy
    
    wall_x = y + perp_wall_dist * dy if side == 0 else x + perp_wall_dist * dx
    wall_x -= int(wall_x)
    
    return hit, perp_wall_dist, texture_id, wall_x, side, map_x, map_y
