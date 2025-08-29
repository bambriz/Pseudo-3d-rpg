# Overview

This is a pseudo-3D first-person RPG game built with Python and Pygame that simulates a 3D experience using raycasting and Mode 7-style rendering techniques. The game features real-time combat, spell casting, enemy AI, and an open world with vertical movement capabilities. Players navigate through a grid-based world from a first-person perspective, engaging in combat with various weapons and spells while managing character stats like health, spirit, and fatigue.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Rendering Engine
The game uses a dual-rendering approach combining raycasting for walls and Mode 7 for floors/ceilings:
- **RayCaster**: Implements DDA (Digital Differential Analyzer) algorithm for wall rendering with optimized NumPy arrays
- **Mode7Renderer**: Creates pseudo-3D perspective for horizontal surfaces using pre-calculated lookup tables
- **Renderer**: Main rendering coordinator that handles z-buffering and combines both rendering techniques

## Game Systems Architecture
The architecture follows a modular entity-component pattern:
- **Player**: Manages character stats, equipment, movement, and input handling
- **World**: Grid-based map system with procedural generation capabilities
- **CombatSystem**: Handles weapon mechanics, damage calculations, and combat animations
- **SpellSystem**: Manages spell casting, magical effects, and projectile systems
- **EnemyManager**: Controls AI behavior, pathfinding, and enemy combat

## Asset Management
Uses a centralized asset management system:
- **AssetManager**: Handles loading, caching, and generation of all game assets
- **TextureGenerator**: Procedurally generates wall textures, sprites, and visual assets
- Assets are organized by type (textures, sounds, fonts) with fallback generation for missing files

## UI System
Modular UI architecture with multiple interface layers:
- **GameUI**: In-game HUD with health/spirit bars, inventory, and minimap
- **MainMenu**: Title screen and main menu navigation
- Supports multiple UI states and smooth transitions between game modes

## Save System
Robust save/load functionality with versioning:
- **SaveManager**: Handles game state serialization using JSON or binary formats
- Supports compression and backup creation for save file integrity
- Version-aware save format for backward compatibility

## Performance Optimizations
- Numba JIT compilation for critical math operations and rendering loops
- Pre-calculated lookup tables for perspective transformations
- Optimized raycasting with early termination and distance culling
- Z-buffer implementation for proper depth sorting

# External Dependencies

## Core Libraries
- **pygame**: Main game engine for graphics, audio, and input handling
- **numpy**: Mathematical operations and array processing for rendering calculations
- **numba**: Just-in-time compilation for performance-critical functions

## Standard Library Dependencies
- **json**: Save/load system data serialization
- **os**: File system operations and asset management
- **pickle**: Binary serialization for save files
- **gzip**: Save file compression
- **datetime**: Timestamp generation for save files
- **sys**: System-level operations and game exit handling
- **math**: Mathematical functions for 3D calculations

## Asset Generation
The game includes a complete procedural asset generation system that creates:
- Wall textures (stone, brick, wood, metal)
- Character and enemy sprites
- Sound effects and background music
- UI elements and fonts

This eliminates the need for external asset files and allows the game to run standalone.