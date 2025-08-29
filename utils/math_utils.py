"""
Mathematical utilities for the pseudo-3D RPG.
Contains optimized functions for 3D calculations, transformations, and geometry.
"""

import numpy as np
from numba import jit
import math

# 2D Vector operations
@jit(nopython=True)
def vector2_length(x, y):
    """Calculate the length of a 2D vector."""
    return math.sqrt(x * x + y * y)

@jit(nopython=True)
def vector2_normalize(x, y):
    """Normalize a 2D vector."""
    length = vector2_length(x, y)
    if length > 0:
        return x / length, y / length
    return 0.0, 0.0

@jit(nopython=True)
def vector2_dot(x1, y1, x2, y2):
    """Calculate dot product of two 2D vectors."""
    return x1 * x2 + y1 * y2

@jit(nopython=True)
def vector2_distance(x1, y1, x2, y2):
    """Calculate distance between two 2D points."""
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx * dx + dy * dy)

@jit(nopython=True)
def vector2_angle(x, y):
    """Calculate angle of a 2D vector."""
    return math.atan2(y, x)

@jit(nopython=True)
def vector2_rotate(x, y, angle):
    """Rotate a 2D vector by an angle."""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return x * cos_a - y * sin_a, x * sin_a + y * cos_a

# 3D Vector operations
@jit(nopython=True)
def vector3_length(x, y, z):
    """Calculate the length of a 3D vector."""
    return math.sqrt(x * x + y * y + z * z)

@jit(nopython=True)
def vector3_normalize(x, y, z):
    """Normalize a 3D vector."""
    length = vector3_length(x, y, z)
    if length > 0:
        return x / length, y / length, z / length
    return 0.0, 0.0, 0.0

@jit(nopython=True)
def vector3_dot(x1, y1, z1, x2, y2, z2):
    """Calculate dot product of two 3D vectors."""
    return x1 * x2 + y1 * y2 + z1 * z2

@jit(nopython=True)
def vector3_cross(x1, y1, z1, x2, y2, z2):
    """Calculate cross product of two 3D vectors."""
    cx = y1 * z2 - z1 * y2
    cy = z1 * x2 - x1 * z2
    cz = x1 * y2 - y1 * x2
    return cx, cy, cz

# Angle utilities
@jit(nopython=True)
def normalize_angle(angle):
    """Normalize angle to [0, 2π) range."""
    while angle < 0:
        angle += 2 * math.pi
    while angle >= 2 * math.pi:
        angle -= 2 * math.pi
    return angle

@jit(nopython=True)
def angle_difference(angle1, angle2):
    """Calculate the shortest difference between two angles."""
    diff = normalize_angle(angle2 - angle1)
    if diff > math.pi:
        diff -= 2 * math.pi
    return diff

@jit(nopython=True)
def degrees_to_radians(degrees):
    """Convert degrees to radians."""
    return degrees * math.pi / 180.0

@jit(nopython=True)
def radians_to_degrees(radians):
    """Convert radians to degrees."""
    return radians * 180.0 / math.pi

# Matrix operations for 3D transformations
@jit(nopython=True)
def matrix3x3_multiply(a, b):
    """Multiply two 3x3 matrices."""
    result = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            for k in range(3):
                result[i, j] += a[i, k] * b[k, j]
    return result

@jit(nopython=True)
def create_rotation_matrix_z(angle):
    """Create a rotation matrix around the Z axis."""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    return np.array([
        [cos_a, -sin_a, 0],
        [sin_a, cos_a, 0],
        [0, 0, 1]
    ])

@jit(nopython=True)
def transform_point(x, y, z, matrix):
    """Transform a 3D point using a transformation matrix."""
    result_x = matrix[0, 0] * x + matrix[0, 1] * y + matrix[0, 2] * z
    result_y = matrix[1, 0] * x + matrix[1, 1] * y + matrix[1, 2] * z
    result_z = matrix[2, 0] * x + matrix[2, 1] * y + matrix[2, 2] * z
    return result_x, result_y, result_z

# Projection utilities
@jit(nopython=True)
def project_to_screen(world_x, world_y, world_z, camera_x, camera_y, camera_z, 
                     camera_angle, fov, screen_width, screen_height):
    """Project a 3D world point to 2D screen coordinates."""
    # Transform world coordinates to camera space
    dx = world_x - camera_x
    dy = world_y - camera_y
    dz = world_z - camera_z
    
    # Rotate by camera angle
    cos_a = math.cos(-camera_angle)
    sin_a = math.sin(-camera_angle)
    
    cam_x = dx * cos_a - dy * sin_a
    cam_y = dx * sin_a + dy * cos_a
    cam_z = dz
    
    # Skip points behind camera
    if cam_y <= 0.1:
        return -1, -1, False
    
    # Project to screen
    screen_x = screen_width // 2 + int((cam_x / cam_y) * (screen_width // 2) / math.tan(fov / 2))
    screen_y = screen_height // 2 - int((cam_z / cam_y) * (screen_height // 2) / math.tan(fov / 2))
    
    # Check if point is on screen
    visible = 0 <= screen_x < screen_width and 0 <= screen_y < screen_height
    
    return screen_x, screen_y, visible

# Collision detection utilities
@jit(nopython=True)
def point_in_rect(px, py, rect_x, rect_y, rect_width, rect_height):
    """Check if a point is inside a rectangle."""
    return rect_x <= px < rect_x + rect_width and rect_y <= py < rect_y + rect_height

@jit(nopython=True)
def circle_rect_collision(circle_x, circle_y, radius, rect_x, rect_y, rect_width, rect_height):
    """Check collision between a circle and a rectangle."""
    # Find closest point on rectangle to circle center
    closest_x = max(rect_x, min(circle_x, rect_x + rect_width))
    closest_y = max(rect_y, min(circle_y, rect_y + rect_height))
    
    # Calculate distance from circle center to closest point
    dx = circle_x - closest_x
    dy = circle_y - closest_y
    distance_squared = dx * dx + dy * dy
    
    return distance_squared <= radius * radius

@jit(nopython=True)
def line_circle_intersection(line_x1, line_y1, line_x2, line_y2, 
                           circle_x, circle_y, radius):
    """Check if a line segment intersects with a circle."""
    # Vector from line start to circle center
    to_circle_x = circle_x - line_x1
    to_circle_y = circle_y - line_y1
    
    # Line direction vector
    line_dx = line_x2 - line_x1
    line_dy = line_y2 - line_y1
    
    # Length of line segment
    line_length_sq = line_dx * line_dx + line_dy * line_dy
    if line_length_sq == 0:
        # Line is a point
        distance_sq = to_circle_x * to_circle_x + to_circle_y * to_circle_y
        return distance_sq <= radius * radius
    
    # Project circle center onto line
    t = max(0, min(1, (to_circle_x * line_dx + to_circle_y * line_dy) / line_length_sq))
    
    # Find closest point on line to circle center
    closest_x = line_x1 + t * line_dx
    closest_y = line_y1 + t * line_dy
    
    # Calculate distance from circle center to closest point
    dx = circle_x - closest_x
    dy = circle_y - closest_y
    distance_squared = dx * dx + dy * dy
    
    return distance_squared <= radius * radius

# Interpolation utilities
@jit(nopython=True)
def lerp(a, b, t):
    """Linear interpolation between two values."""
    return a + (b - a) * t

@jit(nopython=True)
def smooth_step(t):
    """Smooth step function for smooth interpolation."""
    return t * t * (3 - 2 * t)

@jit(nopython=True)
def clamp(value, min_val, max_val):
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, value))

@jit(nopython=True)
def remap(value, old_min, old_max, new_min, new_max):
    """Remap a value from one range to another."""
    t = (value - old_min) / (old_max - old_min)
    return new_min + t * (new_max - new_min)

# Raycasting utilities
@jit(nopython=True)
def ray_plane_intersection(ray_start_x, ray_start_y, ray_start_z,
                          ray_dir_x, ray_dir_y, ray_dir_z,
                          plane_point_x, plane_point_y, plane_point_z,
                          plane_normal_x, plane_normal_y, plane_normal_z):
    """Calculate intersection point between a ray and a plane."""
    # Calculate denominator
    denom = vector3_dot(ray_dir_x, ray_dir_y, ray_dir_z,
                       plane_normal_x, plane_normal_y, plane_normal_z)
    
    if abs(denom) < 1e-6:
        # Ray is parallel to plane
        return 0, 0, 0, False
    
    # Calculate t parameter
    to_plane_x = plane_point_x - ray_start_x
    to_plane_y = plane_point_y - ray_start_y
    to_plane_z = plane_point_z - ray_start_z
    
    t = vector3_dot(to_plane_x, to_plane_y, to_plane_z,
                   plane_normal_x, plane_normal_y, plane_normal_z) / denom
    
    if t < 0:
        # Intersection is behind ray start
        return 0, 0, 0, False
    
    # Calculate intersection point
    hit_x = ray_start_x + t * ray_dir_x
    hit_y = ray_start_y + t * ray_dir_y
    hit_z = ray_start_z + t * ray_dir_z
    
    return hit_x, hit_y, hit_z, True

# Mode 7 transformation utilities
@jit(nopython=True)
def mode7_transform(screen_x, screen_y, player_x, player_y, player_angle,
                   horizon_y, scale_factor):
    """Transform screen coordinates to world coordinates using Mode 7."""
    # Distance from center of screen
    screen_center_x = 400  # Assuming 800px width
    screen_center_y = 300  # Assuming 600px height
    
    rel_x = screen_x - screen_center_x
    rel_y = screen_y - horizon_y
    
    if rel_y == 0:
        return 0, 0, False
    
    # Calculate depth
    depth = scale_factor / rel_y
    
    # Transform to world space
    world_rel_x = rel_x * depth
    world_rel_y = depth
    
    # Rotate by player angle
    cos_a = math.cos(player_angle)
    sin_a = math.sin(player_angle)
    
    rotated_x = world_rel_x * cos_a - world_rel_y * sin_a
    rotated_y = world_rel_x * sin_a + world_rel_y * cos_a
    
    # Add player position
    world_x = player_x + rotated_x
    world_y = player_y + rotated_y
    
    return world_x, world_y, True

# Fast math approximations for performance
@jit(nopython=True)
def fast_sin(x):
    """Fast sine approximation using Taylor series."""
    # Normalize to [-π, π]
    while x > math.pi:
        x -= 2 * math.pi
    while x < -math.pi:
        x += 2 * math.pi
    
    # Taylor series approximation
    x2 = x * x
    return x * (1 - x2 / 6 * (1 - x2 / 20 * (1 - x2 / 42)))

@jit(nopython=True)
def fast_cos(x):
    """Fast cosine approximation."""
    return fast_sin(x + math.pi / 2)

@jit(nopython=True)
def fast_atan2(y, x):
    """Fast atan2 approximation."""
    if x == 0:
        return math.pi / 2 if y > 0 else -math.pi / 2
    
    atan = y / x
    
    # Approximation for small angles
    if abs(atan) <= 1:
        return atan * (1 - abs(atan) * (0.2447 - 0.0663 * abs(atan)))
    else:
        return (math.pi / 2 - atan / (atan * atan + 0.28)) * (1 if atan > 0 else -1)

# Noise generation for procedural content
@jit(nopython=True)
def simple_noise(x, y, seed=0):
    """Simple noise function for procedural generation."""
    # Simple hash-based noise
    n = int(x + y * 57 + seed * 131)
    n = (n << 13) ^ n
    return (1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0)

@jit(nopython=True)
def interpolated_noise(x, y, seed=0):
    """Interpolated noise for smoother results."""
    int_x = int(x)
    frac_x = x - int_x
    int_y = int(y)
    frac_y = y - int_y
    
    # Sample noise at corners
    n00 = simple_noise(int_x, int_y, seed)
    n10 = simple_noise(int_x + 1, int_y, seed)
    n01 = simple_noise(int_x, int_y + 1, seed)
    n11 = simple_noise(int_x + 1, int_y + 1, seed)
    
    # Interpolate
    n0 = lerp(n00, n10, frac_x)
    n1 = lerp(n01, n11, frac_x)
    
    return lerp(n0, n1, frac_y)

# Utility functions for game logic
def calculate_damage_falloff(distance, max_range, min_damage_factor=0.1):
    """Calculate damage falloff based on distance."""
    if distance >= max_range:
        return min_damage_factor
    
    falloff = 1.0 - (distance / max_range)
    return max(min_damage_factor, falloff)

def calculate_line_of_sight_score(start_x, start_y, end_x, end_y, obstacles):
    """Calculate a score representing how clear the line of sight is."""
    steps = int(vector2_distance(start_x, start_y, end_x, end_y) * 10)
    if steps == 0:
        return 1.0
    
    blocked_steps = 0
    dx = (end_x - start_x) / steps
    dy = (end_y - start_y) / steps
    
    for i in range(1, steps):
        check_x = start_x + dx * i
        check_y = start_y + dy * i
        
        for obstacle in obstacles:
            if point_in_rect(check_x, check_y, obstacle[0], obstacle[1], 
                            obstacle[2], obstacle[3]):
                blocked_steps += 1
                break
    
    return 1.0 - (blocked_steps / steps)

def calculate_field_of_view_visibility(viewer_x, viewer_y, viewer_angle, viewer_fov,
                                     target_x, target_y):
    """Calculate if a target is visible within the field of view."""
    # Vector from viewer to target
    dx = target_x - viewer_x
    dy = target_y - viewer_y
    
    if dx == 0 and dy == 0:
        return True
    
    # Angle to target
    target_angle = vector2_angle(dx, dy)
    
    # Angle difference
    angle_diff = abs(angle_difference(viewer_angle, target_angle))
    
    # Check if within FOV
    return angle_diff <= viewer_fov / 2
