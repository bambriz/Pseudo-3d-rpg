"""
Configuration constants for the pseudo-3D RPG game.
Contains all game settings, display parameters, and constants.
"""

import numpy as np

# Display settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TARGET_FPS = 60

# Rendering settings
FOV = np.pi / 3  # 60 degrees field of view
NUM_RAYS = SCREEN_WIDTH  # One ray per column
MAX_RENDER_DISTANCE = 20.0
WALL_HEIGHT = 1.0

# Mode 7 settings
HORIZON_HEIGHT = SCREEN_HEIGHT // 2
FLOOR_TEXTURE_SIZE = 64
CEILING_TEXTURE_SIZE = 64

# Colors
SKY_COLOR = (135, 206, 235)  # Sky blue
FLOOR_COLOR = (101, 67, 33)  # Brown
CEILING_COLOR = (64, 64, 64)  # Dark gray

# Player settings
PLAYER_MOVE_SPEED = 3.0
PLAYER_ROTATE_SPEED = 2.0
PLAYER_RADIUS = 0.3
ATTACK_RANGE = 3.0

# Combat settings
BASE_ATTACK_DAMAGE = 10
CRITICAL_HIT_CHANCE = 0.1
BLOCK_REDUCTION = 0.5

# Spell settings
SPELL_RANGE = 10.0
FIREBALL_DAMAGE = 20
HEAL_AMOUNT = 15
SHIELD_DURATION = 10.0

# World settings
WORLD_SIZE = 128  # Giant maze-like world
WALL_HEIGHT_SCALE = 1.0

# UI settings
UI_MARGIN = 10
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 20
SPIRIT_BAR_WIDTH = 200
SPIRIT_BAR_HEIGHT = 20

# Asset paths
TEXTURE_PATH = "textures/"
SOUND_PATH = "sounds/"
FONT_PATH = "fonts/"

# Performance settings
ENABLE_NUMBA = True
TEXTURE_FILTERING = True
SPRITE_LOD = True  # Level of detail for sprites

# Game balance
PLAYER_MAX_HEALTH = 100
PLAYER_MAX_SPIRIT = 50
FATIGUE_RATE = 0.1  # Health/spirit reduction per second when fatigued
HEALTH_REGEN_RATE = 0.5  # Health per second regeneration
SPIRIT_REGEN_RATE = 1.0  # Spirit per second regeneration

# Enemy settings
ENEMY_SIGHT_RANGE = 8.0
ENEMY_ATTACK_RANGE = 1.5
ENEMY_MOVE_SPEED = 1.5
ENEMY_HEALTH = 30

# Input settings
MOUSE_SENSITIVITY = 0.001
KEYBOARD_REPEAT_DELAY = 50  # Milliseconds
