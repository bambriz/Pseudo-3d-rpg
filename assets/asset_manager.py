"""
Asset management system for the pseudo-3D RPG.
Handles loading, caching, and generation of game assets.
"""

import pygame
import os
from assets.texture_generator import TextureGenerator

class AssetManager:
    def __init__(self):
        """Initialize the asset manager."""
        self.textures = {}
        self.sounds = {}
        self.fonts = {}
        self.sprite_textures = {}
        self.weapon_textures = {}
        
        # Initialize texture generator for procedural assets
        self.texture_generator = TextureGenerator()
        
        # Asset directories
        self.texture_dir = "textures"
        self.sound_dir = "sounds"
        self.font_dir = "fonts"
        
        # Create directories if they don't exist
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create asset directories if they don't exist."""
        directories = [self.texture_dir, self.sound_dir, self.font_dir]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
    
    def load_all_assets(self):
        """Load all game assets."""
        print("Loading game assets...")
        
        # Load or generate textures
        self.load_textures()
        
        # Load or generate sounds
        self.load_sounds()
        
        # Load fonts
        self.load_fonts()
        
        print("Asset loading complete.")
    
    def load_textures(self):
        """Load or generate wall and floor textures."""
        # Wall textures
        wall_textures = {
            1: "stone_wall",
            2: "brick_wall",
            3: "wood_wall",
            4: "metal_wall"
        }
        
        for texture_id, texture_name in wall_textures.items():
            texture_path = os.path.join(self.texture_dir, f"{texture_name}.png")
            
            if os.path.exists(texture_path):
                # Load existing texture
                try:
                    texture = pygame.image.load(texture_path).convert()
                    self.textures[texture_id] = texture
                    print(f"Loaded texture: {texture_name}")
                except pygame.error as e:
                    print(f"Error loading texture {texture_name}: {e}")
                    # Generate fallback texture
                    self.textures[texture_id] = self.texture_generator.generate_wall_texture(texture_name)
            else:
                # Generate procedural texture
                print(f"Generating texture: {texture_name}")
                self.textures[texture_id] = self.texture_generator.generate_wall_texture(texture_name)
                
                # Save generated texture
                try:
                    pygame.image.save(self.textures[texture_id], texture_path)
                    print(f"Saved generated texture: {texture_name}")
                except pygame.error as e:
                    print(f"Error saving texture {texture_name}: {e}")
        
        # Floor and ceiling textures
        floor_path = os.path.join(self.texture_dir, "floor.png")
        if os.path.exists(floor_path):
            try:
                self.textures["floor"] = pygame.image.load(floor_path).convert()
                print("Loaded floor texture")
            except pygame.error:
                self.textures["floor"] = self.texture_generator.generate_floor_texture()
        else:
            print("Generating floor texture")
            self.textures["floor"] = self.texture_generator.generate_floor_texture()
            try:
                pygame.image.save(self.textures["floor"], floor_path)
            except pygame.error as e:
                print(f"Error saving floor texture: {e}")
        
        ceiling_path = os.path.join(self.texture_dir, "ceiling.png")
        if os.path.exists(ceiling_path):
            try:
                self.textures["ceiling"] = pygame.image.load(ceiling_path).convert()
                print("Loaded ceiling texture")
            except pygame.error:
                self.textures["ceiling"] = self.texture_generator.generate_ceiling_texture()
        else:
            print("Generating ceiling texture")
            self.textures["ceiling"] = self.texture_generator.generate_ceiling_texture()
            try:
                pygame.image.save(self.textures["ceiling"], ceiling_path)
            except pygame.error as e:
                print(f"Error saving ceiling texture: {e}")
        
        # Load sprite textures
        self.load_sprite_textures()
        
        # Load weapon textures
        self.load_weapon_textures()
    
    def load_sprite_textures(self):
        """Load or generate sprite textures for enemies and items."""
        sprite_names = [
            "goblin_sprite", "orc_sprite", "skeleton_sprite", 
            "troll_sprite", "spider_sprite", "player_sprite"
        ]
        
        for sprite_name in sprite_names:
            sprite_path = os.path.join(self.texture_dir, f"{sprite_name}.png")
            
            if os.path.exists(sprite_path):
                try:
                    texture = pygame.image.load(sprite_path).convert_alpha()
                    self.sprite_textures[sprite_name] = texture
                    print(f"Loaded sprite: {sprite_name}")
                except pygame.error as e:
                    print(f"Error loading sprite {sprite_name}: {e}")
                    # Generate fallback sprite
                    self.sprite_textures[sprite_name] = self.texture_generator.generate_enemy_sprite(sprite_name)
            else:
                # Generate procedural sprite
                print(f"Generating sprite: {sprite_name}")
                self.sprite_textures[sprite_name] = self.texture_generator.generate_enemy_sprite(sprite_name)
                
                # Save generated sprite
                try:
                    pygame.image.save(self.sprite_textures[sprite_name], sprite_path)
                    print(f"Saved generated sprite: {sprite_name}")
                except pygame.error as e:
                    print(f"Error saving sprite {sprite_name}: {e}")
    
    def load_weapon_textures(self):
        """Load or generate weapon textures."""
        weapon_types = ["sword", "dagger", "axe", "spear", "bow", "wand", "staff", "shield"]
        
        for weapon_type in weapon_types:
            weapon_path = os.path.join(self.texture_dir, f"{weapon_type}.png")
            
            if os.path.exists(weapon_path):
                try:
                    texture = pygame.image.load(weapon_path).convert_alpha()
                    self.weapon_textures[weapon_type] = texture
                    print(f"Loaded weapon: {weapon_type}")
                except pygame.error as e:
                    print(f"Error loading weapon {weapon_type}: {e}")
                    # Generate fallback weapon
                    self.weapon_textures[weapon_type] = self.texture_generator.generate_weapon_texture(weapon_type)
            else:
                # Generate procedural weapon texture
                print(f"Generating weapon texture: {weapon_type}")
                self.weapon_textures[weapon_type] = self.texture_generator.generate_weapon_texture(weapon_type)
                
                # Save generated weapon texture
                try:
                    pygame.image.save(self.weapon_textures[weapon_type], weapon_path)
                    print(f"Saved generated weapon: {weapon_type}")
                except pygame.error as e:
                    print(f"Error saving weapon {weapon_type}: {e}")
    
    def load_sounds(self):
        """Load or generate sound effects."""
        # Initialize pygame mixer if not already done
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error:
            print("Audio device not available, skipping sound loading")
            return
        
        sound_files = {
            "sword_clang.wav": "metal_clang",
            "bow_release.wav": "bow_twang",
            "magic_cast.wav": "magic_whoosh",
            "shield_block.wav": "shield_block",
            "enemy_grunt.wav": "grunt",
            "fireball_cast.wav": "fire_whoosh",
            "lightning_cast.wav": "electric_zap",
            "ice_cast.wav": "ice_crack",
            "heal_cast.wav": "magic_chime",
            "teleport_cast.wav": "teleport_whoosh"
        }
        
        for filename, sound_type in sound_files.items():
            sound_path = os.path.join(self.sound_dir, filename)
            
            if os.path.exists(sound_path):
                try:
                    sound = pygame.mixer.Sound(sound_path)
                    self.sounds[filename] = sound
                    print(f"Loaded sound: {filename}")
                except pygame.error as e:
                    print(f"Error loading sound {filename}: {e}")
                    # Generate or create a silent fallback
                    self.sounds[filename] = self.create_fallback_sound(sound_type)
            else:
                # Create simple procedural sound or silent fallback
                print(f"Creating fallback sound: {filename}")
                self.sounds[filename] = self.create_fallback_sound(sound_type)
    
    def create_fallback_sound(self, sound_type):
        """Create a simple fallback sound effect."""
        # Create a very short, quiet sound as fallback
        # In a real implementation, you might generate procedural audio
        try:
            # Create 0.1 second of silence
            sample_rate = 22050
            duration = 0.1
            frames = int(duration * sample_rate)
            
            # Create silent sound array
            import numpy as np
            sound_array = np.zeros((frames, 2), dtype=np.int16)
            
            # Convert to pygame sound
            sound = pygame.sndarray.make_sound(sound_array)
            return sound
        except:
            # If numpy/sndarray isn't available, return None
            return None
    
    def load_fonts(self):
        """Load game fonts."""
        # Default pygame font
        try:
            self.fonts["small"] = pygame.font.Font(None, 24)
            self.fonts["medium"] = pygame.font.Font(None, 32)
            self.fonts["large"] = pygame.font.Font(None, 48)
            self.fonts["title"] = pygame.font.Font(None, 72)
            print("Loaded default fonts")
        except pygame.error as e:
            print(f"Error loading fonts: {e}")
            # Fallback to basic font
            self.fonts["small"] = pygame.font.Font(None, 20)
            self.fonts["medium"] = pygame.font.Font(None, 28)
            self.fonts["large"] = pygame.font.Font(None, 36)
            self.fonts["title"] = pygame.font.Font(None, 48)
        
        # Try to load custom fonts if they exist
        font_files = {
            "pixel": "pixel_font.ttf",
            "fantasy": "fantasy_font.ttf"
        }
        
        for font_name, filename in font_files.items():
            font_path = os.path.join(self.font_dir, filename)
            if os.path.exists(font_path):
                try:
                    self.fonts[font_name] = pygame.font.Font(font_path, 32)
                    print(f"Loaded custom font: {font_name}")
                except pygame.error as e:
                    print(f"Error loading font {font_name}: {e}")
    
    def get_texture(self, texture_id):
        """Get a wall/floor texture by ID or name."""
        return self.textures.get(texture_id)
    
    def get_sprite_texture(self, sprite_id):
        """Get a sprite texture by ID."""
        return self.sprite_textures.get(sprite_id)
    
    def get_weapon_texture(self, weapon_type):
        """Get a weapon texture by type."""
        return self.weapon_textures.get(weapon_type)
    
    def get_sound(self, sound_name):
        """Get a sound effect by name."""
        return self.sounds.get(sound_name)
    
    def get_font(self, font_name):
        """Get a font by name."""
        return self.fonts.get(font_name, self.fonts.get("medium"))
    
    def preload_texture_variants(self):
        """Preload different variants of textures for different lighting conditions."""
        for texture_id, texture in self.textures.items():
            if isinstance(texture_id, int):  # Wall textures
                # Create darker variants for distance shading
                dark_texture = texture.copy()
                dark_surface = pygame.Surface(texture.get_size())
                dark_surface.fill((128, 128, 128))
                dark_texture.blit(dark_surface, (0, 0), special_flags=pygame.BLEND_MULT)
                
                very_dark_texture = texture.copy()
                very_dark_surface = pygame.Surface(texture.get_size())
                very_dark_surface.fill((64, 64, 64))
                very_dark_texture.blit(very_dark_surface, (0, 0), special_flags=pygame.BLEND_MULT)
                
                # Store variants
                self.textures[f"{texture_id}_dark"] = dark_texture
                self.textures[f"{texture_id}_very_dark"] = very_dark_texture
    
    def get_texture_variant(self, texture_id, variant="normal"):
        """Get a specific variant of a texture."""
        if variant == "normal":
            return self.get_texture(texture_id)
        else:
            variant_key = f"{texture_id}_{variant}"
            return self.textures.get(variant_key, self.get_texture(texture_id))
    
    def unload_assets(self):
        """Unload all assets to free memory."""
        self.textures.clear()
        self.sounds.clear()
        self.fonts.clear()
        self.sprite_textures.clear()
        self.weapon_textures.clear()
        print("Assets unloaded")
    
    def get_memory_usage(self):
        """Get approximate memory usage of loaded assets."""
        total_size = 0
        
        # Estimate texture memory usage
        for texture in self.textures.values():
            if texture:
                size = texture.get_width() * texture.get_height() * 4  # Assume 32-bit
                total_size += size
        
        for texture in self.sprite_textures.values():
            if texture:
                size = texture.get_width() * texture.get_height() * 4
                total_size += size
        
        for texture in self.weapon_textures.values():
            if texture:
                size = texture.get_width() * texture.get_height() * 4
                total_size += size
        
        return total_size
    
    def reload_assets(self):
        """Reload all assets (useful for development)."""
        print("Reloading assets...")
        self.unload_assets()
        self.load_all_assets()
        print("Assets reloaded")
