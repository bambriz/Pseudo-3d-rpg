"""
World generation and management for the pseudo-3D RPG.
Handles map data, terrain, and world state persistence.
"""

import numpy as np
import json
from config import *

class World:
    def __init__(self, width=WORLD_SIZE, height=WORLD_SIZE):
        """Initialize the game world."""
        self.width = width
        self.height = height
        
        # World data as 2D array (0 = empty, 1+ = wall type)
        self.map_data = np.zeros((height, width), dtype=int)
        
        # Player spawn location
        self.spawn_x = width // 2
        self.spawn_y = height // 2
        
        # World features
        self.doors = []
        self.switches = []
        self.water_zones = []
        self.ramps = []
        self.ladders = []
        
        # World state
        self.world_name = "Test Dungeon"
        self.visited_cells = set()
        
        # Generate initial world
        self.generate_test_dungeon()
    
    def generate_test_dungeon(self):
        """Generate a larger explorable dungeon with varied areas."""
        # Clear the map
        self.map_data.fill(0)
        
        # Create outer walls
        self.map_data[0, :] = 1  # Top wall
        self.map_data[-1, :] = 1  # Bottom wall
        self.map_data[:, 0] = 1  # Left wall
        self.map_data[:, -1] = 1  # Right wall
        
        # Create multiple distinct areas for exploration
        # Starting area - safe zone
        self.create_room(5, 5, 12, 8, 2)  # Large starting room
        self.create_room(20, 5, 8, 6, 3)  # Guard house
        self.create_room(30, 8, 10, 8, 4)  # Storage area
        
        # Mid-level areas
        self.create_room(5, 20, 15, 10, 2)  # Great hall
        self.create_room(25, 20, 12, 12, 3)  # Training grounds
        self.create_room(45, 15, 15, 8, 4)  # Library
        
        # Dangerous deeper areas
        self.create_room(5, 40, 10, 12, 1)  # Prison cells
        self.create_room(25, 45, 20, 15, 4)  # Boss arena
        self.create_room(50, 45, 10, 10, 3)  # Treasure vault
        
        # Connect areas with corridors
        self.create_horizontal_corridor(17, 8, 20)  # Connect starting rooms
        self.create_vertical_corridor(10, 13, 20)  # To great hall
        self.create_horizontal_corridor(20, 25, 25)  # To training grounds
        self.create_vertical_corridor(30, 32, 45)  # To deeper areas
        self.create_horizontal_corridor(15, 25, 48)  # Connect deep areas
        
        # Add maze-like sections
        self.create_maze_section(40, 25, 15, 15)
        
        # Set spawn point in the starting room
        self.spawn_x = 10.5
        self.spawn_y = 8.5
        
        # Add many doors and interactive elements
        self.add_door(17, 8, "wooden_door")
        self.add_door(10, 19, "iron_door")
        self.add_door(25, 25, "wooden_door")
        self.add_door(15, 47, "heavy_door")
        self.add_door(45, 48, "magic_door")
        
        # Add switches and levers
        self.add_switch(8, 7, "lever", "opens_secret_passage")
        self.add_switch(35, 50, "crystal", "unlocks_treasure")
        
        # Add environmental variety
        self.add_water_zone(35, 35, 8, 6)  # Lake area
        
        # Add more complex features
        self.add_ramp(12, 12, "north")
        self.add_ladder(26, 26)
    
    def create_maze_section(self, start_x, start_y, width, height):
        """Create a maze-like section for more complex exploration."""
        # Fill area with walls
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                if x < self.width and y < self.height:
                    self.map_data[y, x] = 2
        
        # Create winding pathways
        path_points = [
            (start_x + 2, start_y + 2),
            (start_x + width - 3, start_y + 2),
            (start_x + width - 3, start_y + height - 3),
            (start_x + 2, start_y + height - 3)
        ]
        
        # Carve out paths
        for i in range(len(path_points)):
            current = path_points[i]
            next_point = path_points[(i + 1) % len(path_points)]
            self.carve_path(current[0], current[1], next_point[0], next_point[1])
    
    def carve_path(self, x1, y1, x2, y2):
        """Carve a path between two points."""
        # Simple L-shaped path
        # Go horizontal first
        start_x, end_x = (x1, x2) if x1 < x2 else (x2, x1)
        for x in range(start_x, end_x + 1):
            if 0 <= x < self.width and 0 <= y1 < self.height:
                self.map_data[y1, x] = 0
        
        # Then vertical
        start_y, end_y = (y1, y2) if y1 < y2 else (y2, y1)
        for y in range(start_y, end_y + 1):
            if 0 <= x2 < self.width and 0 <= y < self.height:
                self.map_data[y, x2] = 0
    
    def create_room(self, x, y, width, height, wall_type):
        """Create a rectangular room with the specified wall type."""
        # Top and bottom walls
        for i in range(width):
            self.map_data[y, x + i] = wall_type
            self.map_data[y + height - 1, x + i] = wall_type
        
        # Left and right walls
        for i in range(height):
            self.map_data[y + i, x] = wall_type
            self.map_data[y + i, x + width - 1] = wall_type
    
    def create_horizontal_corridor(self, x1, x2, y):
        """Create a horizontal corridor between two x coordinates."""
        start_x = min(x1, x2)
        end_x = max(x1, x2)
        
        for x in range(start_x, end_x + 1):
            self.map_data[y, x] = 0  # Clear the path
    
    def create_vertical_corridor(self, x, y1, y2):
        """Create a vertical corridor between two y coordinates."""
        start_y = min(y1, y2)
        end_y = max(y1, y2)
        
        for y in range(start_y, end_y + 1):
            self.map_data[y, x] = 0  # Clear the path
    
    def create_wall_line(self, x1, y1, x2, y2, wall_type):
        """Create a line of walls between two points."""
        # Simple implementation for horizontal and vertical lines
        if x1 == x2:  # Vertical line
            start_y = min(y1, y2)
            end_y = max(y1, y2)
            for y in range(start_y, end_y + 1):
                if 0 <= y < self.height:
                    self.map_data[y, x1] = wall_type
        elif y1 == y2:  # Horizontal line
            start_x = min(x1, x2)
            end_x = max(x1, x2)
            for x in range(start_x, end_x + 1):
                if 0 <= x < self.width:
                    self.map_data[y1, x] = wall_type
    
    def add_door(self, x, y, door_type):
        """Add a door at the specified location."""
        door = {
            'x': x,
            'y': y,
            'type': door_type,
            'is_open': False,
            'requires_key': door_type == "iron_door"
        }
        self.doors.append(door)
        
        # Remove wall at door location
        if 0 <= x < self.width and 0 <= y < self.height:
            self.map_data[y, x] = 0
    
    def add_switch(self, x, y, switch_type, action):
        """Add a switch at the specified location."""
        switch = {
            'x': x,
            'y': y,
            'type': switch_type,
            'action': action,
            'is_activated': False
        }
        self.switches.append(switch)
    
    def add_water_zone(self, x, y, width, height):
        """Add a water zone for swimming."""
        water_zone = {
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'depth': 1.0  # Swimming depth
        }
        self.water_zones.append(water_zone)
    
    def add_ramp(self, x, y, direction):
        """Add a ramp for vertical movement."""
        ramp = {
            'x': x,
            'y': y,
            'direction': direction,  # 'north', 'south', 'east', 'west'
            'height_change': 1.0
        }
        self.ramps.append(ramp)
    
    def add_ladder(self, x, y):
        """Add a ladder for vertical movement."""
        ladder = {
            'x': x,
            'y': y,
            'height': 2.0  # How high the ladder goes
        }
        self.ladders.append(ladder)
    
    def get_cell(self, x, y):
        """Get the value of a map cell."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.map_data[y, x]
        return 1  # Return wall if outside bounds
    
    def get_map_array(self):
        """Get the map data as a NumPy array for optimized operations."""
        return self.map_data
    
    def set_cell(self, x, y, value):
        """Set the value of a map cell."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.map_data[y, x] = value
    
    def is_passable(self, x, y):
        """Check if a position is passable."""
        # Check basic wall collision
        if self.get_cell(int(x), int(y)) > 0:
            return False
        
        # Check for closed doors
        for door in self.doors:
            if int(door['x']) == int(x) and int(door['y']) == int(y):
                return door['is_open']
        
        return True
    
    def is_water(self, x, y):
        """Check if a position is in water."""
        for water_zone in self.water_zones:
            if (water_zone['x'] <= x < water_zone['x'] + water_zone['width'] and
                water_zone['y'] <= y < water_zone['y'] + water_zone['height']):
                return True
        return False
    
    def get_height_at(self, x, y):
        """Get the height/elevation at a position."""
        # Check for ramps
        for ramp in self.ramps:
            if int(ramp['x']) == int(x) and int(ramp['y']) == int(y):
                return ramp['height_change']
        
        # Check for water depth
        if self.is_water(x, y):
            for water_zone in self.water_zones:
                if (water_zone['x'] <= x < water_zone['x'] + water_zone['width'] and
                    water_zone['y'] <= y < water_zone['y'] + water_zone['height']):
                    return -water_zone['depth']
        
        return 0.0  # Ground level
    
    def interact_with_door(self, x, y, player):
        """Attempt to interact with a door."""
        for door in self.doors:
            if int(door['x']) == int(x) and int(door['y']) == int(y):
                if door['requires_key']:
                    # Check if player has the required key
                    if hasattr(player, 'has_key') and player.has_key(door['type']):
                        door['is_open'] = not door['is_open']
                        return f"Door {door['type']} {'opened' if door['is_open'] else 'closed'}"
                    else:
                        return f"This door requires a key."
                else:
                    door['is_open'] = not door['is_open']
                    return f"Door {'opened' if door['is_open'] else 'closed'}"
        
        return None
    
    def interact_with_switch(self, x, y):
        """Attempt to interact with a switch."""
        for switch in self.switches:
            if int(switch['x']) == int(x) and int(switch['y']) == int(y):
                switch['is_activated'] = not switch['is_activated']
                
                # Execute switch action
                if switch['action'] == "opens_secret_door":
                    # Find and open a secret door
                    for door in self.doors:
                        if door['type'] == "secret_door":
                            door['is_open'] = switch['is_activated']
                
                return f"Switch {'activated' if switch['is_activated'] else 'deactivated'}"
        
        return None
    
    def mark_visited(self, x, y):
        """Mark a cell as visited (for mapping/exploration)."""
        self.visited_cells.add((int(x), int(y)))
    
    def is_visited(self, x, y):
        """Check if a cell has been visited."""
        return (int(x), int(y)) in self.visited_cells
    
    def get_nearby_features(self, x, y, radius=2):
        """Get nearby interactive features."""
        features = []
        
        # Check for doors
        for door in self.doors:
            distance = np.sqrt((door['x'] - x)**2 + (door['y'] - y)**2)
            if distance <= radius:
                features.append(('door', door))
        
        # Check for switches
        for switch in self.switches:
            distance = np.sqrt((switch['x'] - x)**2 + (switch['y'] - y)**2)
            if distance <= radius:
                features.append(('switch', switch))
        
        # Check for ladders
        for ladder in self.ladders:
            distance = np.sqrt((ladder['x'] - x)**2 + (ladder['y'] - y)**2)
            if distance <= radius:
                features.append(('ladder', ladder))
        
        return features
    
    def generate_procedural_area(self, center_x, center_y, size=10):
        """Generate a procedural area around a center point."""
        # Simple maze generation algorithm
        for y in range(max(0, center_y - size), min(self.height, center_y + size)):
            for x in range(max(0, center_x - size), min(self.width, center_x + size)):
                # Create a simple maze pattern
                if (x + y) % 3 == 0 and np.random.random() < 0.3:
                    self.map_data[y, x] = np.random.choice([2, 3, 4])
    
    def to_dict(self):
        """Convert world state to dictionary for saving."""
        return {
            'width': self.width,
            'height': self.height,
            'map_data': self.map_data.tolist(),
            'spawn_x': self.spawn_x,
            'spawn_y': self.spawn_y,
            'doors': self.doors,
            'switches': self.switches,
            'water_zones': self.water_zones,
            'ramps': self.ramps,
            'ladders': self.ladders,
            'world_name': self.world_name,
            'visited_cells': list(self.visited_cells)
        }
    
    def from_dict(self, data):
        """Load world state from dictionary."""
        self.width = data.get('width', self.width)
        self.height = data.get('height', self.height)
        self.map_data = np.array(data.get('map_data', self.map_data.tolist()))
        self.spawn_x = data.get('spawn_x', self.spawn_x)
        self.spawn_y = data.get('spawn_y', self.spawn_y)
        self.doors = data.get('doors', [])
        self.switches = data.get('switches', [])
        self.water_zones = data.get('water_zones', [])
        self.ramps = data.get('ramps', [])
        self.ladders = data.get('ladders', [])
        self.world_name = data.get('world_name', self.world_name)
        self.visited_cells = set(tuple(cell) for cell in data.get('visited_cells', []))
