"""
Procedural texture generation for the pseudo-3D RPG.
Generates wall textures, sprites, and other visual assets.
"""

import pygame
import numpy as np
from config import *

class TextureGenerator:
    def __init__(self):
        """Initialize the texture generator."""
        self.texture_size = 64  # Standard texture size
        self.sprite_size = 32   # Standard sprite size
    
    def generate_wall_texture(self, texture_name):
        """Generate a procedural wall texture."""
        texture = pygame.Surface((self.texture_size, self.texture_size))
        
        if texture_name == "stone_wall":
            self.generate_stone_texture(texture)
        elif texture_name == "brick_wall":
            self.generate_brick_texture(texture)
        elif texture_name == "wood_wall":
            self.generate_wood_texture(texture)
        elif texture_name == "metal_wall":
            self.generate_metal_texture(texture)
        else:
            # Default stone texture
            self.generate_stone_texture(texture)
        
        return texture
    
    def generate_stone_texture(self, surface):
        """Generate a stone wall texture."""
        base_color = (120, 120, 120)
        
        # Fill with base color
        surface.fill(base_color)
        
        # Add noise for stone texture
        for y in range(self.texture_size):
            for x in range(self.texture_size):
                # Perlin-like noise simulation
                noise = (
                    np.sin(x * 0.1) * np.cos(y * 0.1) * 20 +
                    np.sin(x * 0.3) * np.cos(y * 0.3) * 10 +
                    np.random.randint(-15, 15)
                )
                
                # Apply noise to base color
                r = max(0, min(255, base_color[0] + noise))
                g = max(0, min(255, base_color[1] + noise))
                b = max(0, min(255, base_color[2] + noise))
                
                surface.set_at((x, y), (int(r), int(g), int(b)))
        
        # Add some cracks/lines
        self.add_stone_details(surface)
    
    def add_stone_details(self, surface):
        """Add cracks and details to stone texture."""
        # Horizontal mortar lines
        for y in [15, 31, 47]:
            for x in range(self.texture_size):
                if np.random.random() < 0.8:  # Not every pixel
                    color = (80, 80, 80)
                    surface.set_at((x, y), color)
        
        # Vertical mortar lines
        for x in [20, 42]:
            for y in range(self.texture_size):
                if np.random.random() < 0.7:
                    color = (85, 85, 85)
                    surface.set_at((x, y), color)
    
    def generate_brick_texture(self, surface):
        """Generate a brick wall texture."""
        mortar_color = (100, 90, 80)
        brick_color = (150, 80, 60)
        
        # Fill with mortar color
        surface.fill(mortar_color)
        
        # Draw bricks
        brick_height = 8
        brick_width = 16
        mortar_thickness = 2
        
        for row in range(0, self.texture_size, brick_height + mortar_thickness):
            offset = (brick_width // 2) if (row // (brick_height + mortar_thickness)) % 2 else 0
            
            for col in range(-offset, self.texture_size, brick_width + mortar_thickness):
                # Draw brick rectangle
                brick_rect = pygame.Rect(
                    col + mortar_thickness, 
                    row + mortar_thickness,
                    brick_width - mortar_thickness,
                    brick_height - mortar_thickness
                )
                
                # Clip to surface bounds
                brick_rect = brick_rect.clip(surface.get_rect())
                
                if brick_rect.width > 0 and brick_rect.height > 0:
                    # Fill brick with base color plus noise
                    for y in range(brick_rect.top, brick_rect.bottom):
                        for x in range(brick_rect.left, brick_rect.right):
                            noise = np.random.randint(-20, 20)
                            r = max(0, min(255, brick_color[0] + noise))
                            g = max(0, min(255, brick_color[1] + noise))
                            b = max(0, min(255, brick_color[2] + noise))
                            surface.set_at((x, y), (r, g, b))
    
    def generate_wood_texture(self, surface):
        """Generate a wood wall texture."""
        base_color = (139, 115, 85)
        
        # Fill with base color
        surface.fill(base_color)
        
        # Add wood grain
        for y in range(self.texture_size):
            for x in range(self.texture_size):
                # Wood grain pattern
                grain = (
                    np.sin(y * 0.3 + x * 0.1) * 15 +
                    np.sin(y * 0.1) * 20 +
                    np.random.randint(-10, 10)
                )
                
                # Apply grain to base color
                r = max(0, min(255, base_color[0] + grain))
                g = max(0, min(255, base_color[1] + grain * 0.8))
                b = max(0, min(255, base_color[2] + grain * 0.6))
                
                surface.set_at((x, y), (int(r), int(g), int(b)))
        
        # Add wood planks
        self.add_wood_planks(surface)
    
    def add_wood_planks(self, surface):
        """Add plank lines to wood texture."""
        plank_height = 16
        
        for y in range(plank_height, self.texture_size, plank_height):
            for x in range(self.texture_size):
                if np.random.random() < 0.6:
                    color = (100, 85, 65)
                    surface.set_at((x, y), color)
                    if y + 1 < self.texture_size:
                        surface.set_at((x, y + 1), color)
    
    def generate_metal_texture(self, surface):
        """Generate a metal wall texture."""
        base_color = (160, 160, 180)
        
        # Fill with base color
        surface.fill(base_color)
        
        # Add metallic sheen
        for y in range(self.texture_size):
            for x in range(self.texture_size):
                # Metallic reflection pattern
                reflection = (
                    np.sin(x * 0.2) * np.cos(y * 0.2) * 30 +
                    np.sin((x + y) * 0.1) * 15 +
                    np.random.randint(-10, 10)
                )
                
                # Apply reflection to base color
                r = max(0, min(255, base_color[0] + reflection))
                g = max(0, min(255, base_color[1] + reflection))
                b = max(0, min(255, base_color[2] + reflection * 0.8))
                
                surface.set_at((x, y), (int(r), int(g), int(b)))
        
        # Add metal panel lines
        self.add_metal_panels(surface)
    
    def add_metal_panels(self, surface):
        """Add panel lines to metal texture."""
        # Horizontal lines
        for y in [21, 42]:
            for x in range(self.texture_size):
                color = (120, 120, 140)
                surface.set_at((x, y), color)
        
        # Vertical lines
        for x in [21, 42]:
            for y in range(self.texture_size):
                color = (140, 140, 160)
                surface.set_at((x, y), color)
        
        # Add rivets
        rivet_positions = [(10, 10), (32, 10), (54, 10), (10, 32), (32, 32), (54, 32), (10, 54), (32, 54), (54, 54)]
        for rx, ry in rivet_positions:
            if 0 <= rx < self.texture_size and 0 <= ry < self.texture_size:
                # Draw simple rivet
                rivet_color = (200, 200, 220)
                surface.set_at((rx, ry), rivet_color)
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = rx + dx, ry + dy
                    if 0 <= nx < self.texture_size and 0 <= ny < self.texture_size:
                        surface.set_at((nx, ny), (180, 180, 200))
    
    def generate_floor_texture(self):
        """Generate a floor texture with stone tiles."""
        texture = pygame.Surface((FLOOR_TEXTURE_SIZE, FLOOR_TEXTURE_SIZE))
        base_color = (101, 67, 33)  # Brown stone
        
        # Fill with base color
        texture.fill(base_color)
        
        # Create tile pattern
        tile_size = FLOOR_TEXTURE_SIZE // 4
        
        for ty in range(0, FLOOR_TEXTURE_SIZE, tile_size):
            for tx in range(0, FLOOR_TEXTURE_SIZE, tile_size):
                # Add variation to each tile
                for y in range(ty, min(ty + tile_size, FLOOR_TEXTURE_SIZE)):
                    for x in range(tx, min(tx + tile_size, FLOOR_TEXTURE_SIZE)):
                        # Add noise
                        noise = np.random.randint(-15, 15)
                        r = max(0, min(255, base_color[0] + noise))
                        g = max(0, min(255, base_color[1] + noise))
                        b = max(0, min(255, base_color[2] + noise))
                        texture.set_at((x, y), (r, g, b))
                
                # Add tile borders
                border_color = (80, 50, 20)
                
                # Top border
                for x in range(tx, min(tx + tile_size, FLOOR_TEXTURE_SIZE)):
                    if ty < FLOOR_TEXTURE_SIZE:
                        texture.set_at((x, ty), border_color)
                
                # Left border
                for y in range(ty, min(ty + tile_size, FLOOR_TEXTURE_SIZE)):
                    if tx < FLOOR_TEXTURE_SIZE:
                        texture.set_at((tx, y), border_color)
        
        return texture
    
    def generate_ceiling_texture(self):
        """Generate a ceiling texture with stone pattern."""
        texture = pygame.Surface((CEILING_TEXTURE_SIZE, CEILING_TEXTURE_SIZE))
        base_color = (64, 64, 64)  # Dark gray
        
        # Fill with base color
        texture.fill(base_color)
        
        # Add texture variation
        for y in range(CEILING_TEXTURE_SIZE):
            for x in range(CEILING_TEXTURE_SIZE):
                # Stone-like pattern
                noise = (
                    np.sin(x * 0.2) * np.cos(y * 0.2) * 15 +
                    np.random.randint(-10, 10)
                )
                
                r = max(30, min(100, base_color[0] + noise))
                g = max(30, min(100, base_color[1] + noise))
                b = max(30, min(100, base_color[2] + noise))
                
                texture.set_at((x, y), (int(r), int(g), int(b)))
        
        return texture
    
    def generate_enemy_sprite(self, sprite_name):
        """Generate a procedural enemy sprite."""
        sprite = pygame.Surface((self.sprite_size, self.sprite_size), pygame.SRCALPHA)
        
        if "goblin" in sprite_name:
            self.draw_goblin(sprite)
        elif "orc" in sprite_name:
            self.draw_orc(sprite)
        elif "skeleton" in sprite_name:
            self.draw_skeleton(sprite)
        elif "troll" in sprite_name:
            self.draw_troll(sprite)
        elif "spider" in sprite_name:
            self.draw_spider(sprite)
        else:
            # Default enemy shape
            self.draw_generic_enemy(sprite)
        
        return sprite
    
    def draw_goblin(self, surface):
        """Draw a simple goblin sprite."""
        # Green body
        body_color = (0, 128, 0)
        pygame.draw.ellipse(surface, body_color, (8, 16, 16, 12))
        
        # Head
        head_color = (0, 150, 0)
        pygame.draw.circle(surface, head_color, (16, 12), 6)
        
        # Eyes
        eye_color = (255, 0, 0)
        pygame.draw.circle(surface, eye_color, (14, 10), 1)
        pygame.draw.circle(surface, eye_color, (18, 10), 1)
        
        # Ears
        ear_color = (0, 100, 0)
        pygame.draw.polygon(surface, ear_color, [(10, 8), (8, 6), (12, 10)])
        pygame.draw.polygon(surface, ear_color, [(20, 10), (24, 6), (22, 8)])
        
        # Arms and legs (simple lines)
        limb_color = (0, 100, 0)
        pygame.draw.line(surface, limb_color, (8, 20), (4, 24), 2)  # Left arm
        pygame.draw.line(surface, limb_color, (24, 20), (28, 24), 2)  # Right arm
        pygame.draw.line(surface, limb_color, (12, 28), (10, 32), 2)  # Left leg
        pygame.draw.line(surface, limb_color, (20, 28), (22, 32), 2)  # Right leg
    
    def draw_orc(self, surface):
        """Draw a simple orc sprite."""
        # Brown body
        body_color = (128, 64, 0)
        pygame.draw.ellipse(surface, body_color, (6, 16, 20, 14))
        
        # Head
        head_color = (100, 60, 0)
        pygame.draw.circle(surface, head_color, (16, 12), 8)
        
        # Eyes
        eye_color = (255, 255, 0)
        pygame.draw.circle(surface, eye_color, (13, 10), 2)
        pygame.draw.circle(surface, eye_color, (19, 10), 2)
        
        # Tusks
        tusk_color = (255, 255, 255)
        pygame.draw.polygon(surface, tusk_color, [(12, 14), (11, 16), (13, 16)])
        pygame.draw.polygon(surface, tusk_color, [(20, 14), (19, 16), (21, 16)])
        
        # Arms and legs
        limb_color = (80, 40, 0)
        pygame.draw.line(surface, limb_color, (6, 22), (2, 26), 3)
        pygame.draw.line(surface, limb_color, (26, 22), (30, 26), 3)
        pygame.draw.line(surface, limb_color, (12, 30), (10, 34), 3)
        pygame.draw.line(surface, limb_color, (20, 30), (22, 34), 3)
    
    def draw_skeleton(self, surface):
        """Draw a simple skeleton sprite."""
        # Bone white color
        bone_color = (200, 200, 200)
        
        # Skull
        pygame.draw.circle(surface, bone_color, (16, 12), 7)
        
        # Eye sockets
        socket_color = (0, 0, 0)
        pygame.draw.circle(surface, socket_color, (13, 10), 2)
        pygame.draw.circle(surface, socket_color, (19, 10), 2)
        pygame.draw.circle(surface, (255, 0, 0), (13, 10), 1)  # Glowing eyes
        pygame.draw.circle(surface, (255, 0, 0), (19, 10), 1)
        
        # Spine
        pygame.draw.line(surface, bone_color, (16, 19), (16, 28), 3)
        
        # Ribcage
        for i in range(3):
            y_pos = 20 + i * 2
            pygame.draw.arc(surface, bone_color, (10, y_pos - 2, 12, 4), 0, 3.14, 2)
        
        # Arms
        pygame.draw.line(surface, bone_color, (10, 22), (4, 26), 2)
        pygame.draw.line(surface, bone_color, (22, 22), (28, 26), 2)
        
        # Legs
        pygame.draw.line(surface, bone_color, (12, 28), (10, 34), 2)
        pygame.draw.line(surface, bone_color, (20, 28), (22, 34), 2)
    
    def draw_troll(self, surface):
        """Draw a simple troll sprite."""
        # Large dark green body
        body_color = (64, 128, 64)
        pygame.draw.ellipse(surface, body_color, (4, 14, 24, 18))
        
        # Large head
        head_color = (80, 140, 80)
        pygame.draw.circle(surface, head_color, (16, 10), 10)
        
        # Small beady eyes
        eye_color = (255, 255, 0)
        pygame.draw.circle(surface, eye_color, (12, 8), 1)
        pygame.draw.circle(surface, eye_color, (20, 8), 1)
        
        # Large mouth
        mouth_color = (0, 0, 0)
        pygame.draw.ellipse(surface, mouth_color, (12, 12, 8, 4))
        
        # Thick arms and legs
        limb_color = (60, 120, 60)
        pygame.draw.line(surface, limb_color, (4, 20), (0, 28), 4)
        pygame.draw.line(surface, limb_color, (28, 20), (32, 28), 4)
        pygame.draw.line(surface, limb_color, (10, 32), (8, 38), 4)
        pygame.draw.line(surface, limb_color, (22, 32), (24, 38), 4)
    
    def draw_spider(self, surface):
        """Draw a simple spider sprite."""
        # Dark purple body
        body_color = (64, 0, 64)
        pygame.draw.ellipse(surface, body_color, (10, 14, 12, 8))
        
        # Head section
        head_color = (80, 0, 80)
        pygame.draw.circle(surface, head_color, (16, 12), 4)
        
        # Eyes
        eye_color = (255, 0, 0)
        pygame.draw.circle(surface, eye_color, (15, 11), 1)
        pygame.draw.circle(surface, eye_color, (17, 11), 1)
        
        # Spider legs (8 legs)
        leg_color = (40, 0, 40)
        leg_positions = [
            # Left side legs
            ((6, 16), (2, 12)),
            ((8, 18), (4, 20)),
            ((8, 20), (4, 24)),
            ((10, 22), (6, 26)),
            # Right side legs
            ((26, 16), (30, 12)),
            ((24, 18), (28, 20)),
            ((24, 20), (28, 24)),
            ((22, 22), (26, 26))
        ]
        
        for start, end in leg_positions:
            pygame.draw.line(surface, leg_color, start, end, 2)
    
    def draw_generic_enemy(self, surface):
        """Draw a generic enemy sprite."""
        # Red body
        body_color = (128, 0, 0)
        pygame.draw.ellipse(surface, body_color, (8, 16, 16, 12))
        
        # Head
        pygame.draw.circle(surface, body_color, (16, 12), 6)
        
        # Eyes
        eye_color = (255, 255, 255)
        pygame.draw.circle(surface, eye_color, (14, 10), 2)
        pygame.draw.circle(surface, eye_color, (18, 10), 2)
        pygame.draw.circle(surface, (0, 0, 0), (14, 10), 1)
        pygame.draw.circle(surface, (0, 0, 0), (18, 10), 1)
        
        # Simple limbs
        pygame.draw.line(surface, body_color, (8, 20), (4, 24), 2)
        pygame.draw.line(surface, body_color, (24, 20), (28, 24), 2)
        pygame.draw.line(surface, body_color, (12, 28), (10, 32), 2)
        pygame.draw.line(surface, body_color, (20, 28), (22, 32), 2)
    
    def generate_weapon_texture(self, weapon_type):
        """Generate a weapon texture for first-person view."""
        if weapon_type == "shield":
            size = (64, 64)
        else:
            size = (48, 96)  # Tall for weapons
        
        texture = pygame.Surface(size, pygame.SRCALPHA)
        
        if weapon_type == "sword":
            self.draw_sword(texture)
        elif weapon_type == "dagger":
            self.draw_dagger(texture)
        elif weapon_type == "axe":
            self.draw_axe(texture)
        elif weapon_type == "spear":
            self.draw_spear(texture)
        elif weapon_type == "bow":
            self.draw_bow(texture)
        elif weapon_type == "wand":
            self.draw_wand(texture)
        elif weapon_type == "staff":
            self.draw_staff(texture)
        elif weapon_type == "shield":
            self.draw_shield(texture)
        
        return texture
    
    def draw_sword(self, surface):
        """Draw a sword weapon."""
        # Handle
        handle_color = (139, 69, 19)  # Brown
        pygame.draw.rect(surface, handle_color, (20, 60, 8, 30))
        
        # Guard
        guard_color = (192, 192, 192)  # Silver
        pygame.draw.rect(surface, guard_color, (16, 55, 16, 8))
        
        # Blade
        blade_color = (211, 211, 211)  # Light gray
        pygame.draw.polygon(surface, blade_color, [(24, 10), (26, 55), (22, 55)])
        
        # Blade edge (highlight)
        edge_color = (255, 255, 255)
        pygame.draw.line(surface, edge_color, (24, 10), (24, 55), 1)
    
    def draw_dagger(self, surface):
        """Draw a dagger weapon."""
        # Handle
        handle_color = (64, 64, 64)  # Dark gray
        pygame.draw.rect(surface, handle_color, (21, 65, 6, 25))
        
        # Guard
        guard_color = (128, 128, 128)
        pygame.draw.rect(surface, guard_color, (18, 62, 12, 6))
        
        # Blade
        blade_color = (192, 192, 192)
        pygame.draw.polygon(surface, blade_color, [(24, 20), (26, 62), (22, 62)])
        
        # Blade highlight
        pygame.draw.line(surface, (255, 255, 255), (24, 20), (24, 62), 1)
    
    def draw_axe(self, surface):
        """Draw an axe weapon."""
        # Handle
        handle_color = (139, 69, 19)
        pygame.draw.rect(surface, handle_color, (22, 40, 4, 50))
        
        # Axe head
        head_color = (169, 169, 169)
        # Axe blade shape
        pygame.draw.polygon(surface, head_color, [
            (24, 30), (35, 25), (38, 35), (35, 45), (24, 40)
        ])
        
        # Axe edge
        edge_color = (211, 211, 211)
        pygame.draw.line(surface, edge_color, (35, 25), (38, 35), 2)
    
    def draw_spear(self, surface):
        """Draw a spear weapon."""
        # Shaft
        shaft_color = (160, 82, 45)  # Saddle brown
        pygame.draw.rect(surface, shaft_color, (22, 20, 4, 70))
        
        # Spear point
        point_color = (192, 192, 192)
        pygame.draw.polygon(surface, point_color, [(24, 5), (28, 20), (20, 20)])
        
        # Point highlight
        pygame.draw.line(surface, (255, 255, 255), (24, 5), (24, 20), 1)
    
    def draw_bow(self, surface):
        """Draw a bow weapon."""
        # Bow body
        bow_color = (139, 69, 19)
        
        # Draw bow curve
        pygame.draw.arc(surface, bow_color, (16, 10, 16, 80), 0, 3.14, 4)
        
        # Bowstring
        string_color = (245, 245, 220)  # Beige
        pygame.draw.line(surface, string_color, (18, 15), (18, 85), 1)
        
        # Grip area
        grip_color = (101, 67, 33)
        pygame.draw.rect(surface, grip_color, (22, 45, 8, 15))
    
    def draw_wand(self, surface):
        """Draw a magic wand."""
        # Wand shaft
        wand_color = (139, 69, 19)
        pygame.draw.rect(surface, wand_color, (22, 30, 4, 60))
        
        # Magic crystal
        crystal_color = (138, 43, 226)  # Blue violet
        pygame.draw.polygon(surface, crystal_color, [
            (24, 20), (28, 28), (24, 35), (20, 28)
        ])
        
        # Crystal glow
        glow_color = (255, 255, 255)
        pygame.draw.circle(surface, glow_color, (24, 27), 2)
    
    def draw_staff(self, surface):
        """Draw a magic staff."""
        # Staff shaft
        staff_color = (160, 82, 45)
        pygame.draw.rect(surface, staff_color, (22, 25, 4, 65))
        
        # Staff head
        head_color = (184, 134, 11)  # Dark golden rod
        pygame.draw.circle(surface, head_color, (24, 20), 8)
        
        # Magic orb
        orb_color = (0, 191, 255)  # Deep sky blue
        pygame.draw.circle(surface, orb_color, (24, 20), 5)
        
        # Orb glow
        glow_color = (255, 255, 255)
        pygame.draw.circle(surface, glow_color, (24, 20), 2)
    
    def draw_shield(self, surface):
        """Draw a shield."""
        # Shield body
        shield_color = (139, 69, 19)  # Brown
        pygame.draw.ellipse(surface, shield_color, (8, 8, 48, 48))
        
        # Shield rim
        rim_color = (169, 169, 169)  # Dark gray
        pygame.draw.ellipse(surface, rim_color, (8, 8, 48, 48), 3)
        
        # Shield boss (center)
        boss_color = (192, 192, 192)
        pygame.draw.circle(surface, boss_color, (32, 32), 8)
        
        # Shield design (simple cross)
        design_color = (160, 82, 45)
        pygame.draw.line(surface, design_color, (32, 16), (32, 48), 3)
        pygame.draw.line(surface, design_color, (16, 32), (48, 32), 3)
