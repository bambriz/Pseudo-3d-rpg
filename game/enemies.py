"""
Enemy AI and management system for the pseudo-3D RPG.
Handles enemy behavior, pathfinding, and combat AI.
"""

import pygame
import numpy as np
from config import *

class Enemy:
    def __init__(self, x, y, enemy_type, sprite_id):
        """Initialize an enemy."""
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.type = enemy_type
        self.sprite_id = sprite_id
        
        # Stats based on enemy type
        stats = self.get_enemy_stats(enemy_type)
        self.max_health = stats['health']
        self.health = self.max_health
        self.damage = stats['damage']
        self.speed = stats['speed']
        self.sight_range = stats['sight_range']
        self.attack_range = stats['attack_range']
        
        # AI state
        self.state = "IDLE"  # IDLE, PATROL, CHASE, ATTACK, DEAD
        self.target = None
        self.last_seen_x = 0
        self.last_seen_y = 0
        self.patrol_points = []
        self.current_patrol_index = 0
        
        # Movement
        self.angle = 0.0
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.is_moving = False
        
        # Combat
        self.attack_cooldown = 0.0
        self.last_attack_time = 0.0
        
        # Pathfinding
        self.path = []
        self.path_index = 0
        
        # Visual
        self.color = self.get_enemy_color(enemy_type)
        self.animation_time = 0.0
        
    def get_enemy_stats(self, enemy_type):
        """Get stats for different enemy types."""
        enemy_stats = {
            'goblin': {
                'health': 20,
                'damage': 5,
                'speed': 1.2,
                'sight_range': 6.0,
                'attack_range': 1.2
            },
            'orc': {
                'health': 40,
                'damage': 12,
                'speed': 1.0,
                'sight_range': 8.0,
                'attack_range': 1.5
            },
            'skeleton': {
                'health': 15,
                'damage': 8,
                'speed': 0.8,
                'sight_range': 10.0,
                'attack_range': 2.0
            },
            'troll': {
                'health': 80,
                'damage': 20,
                'speed': 0.6,
                'sight_range': 5.0,
                'attack_range': 2.5
            },
            'spider': {
                'health': 12,
                'damage': 6,
                'speed': 1.8,
                'sight_range': 4.0,
                'attack_range': 1.0
            }
        }
        return enemy_stats.get(enemy_type, enemy_stats['goblin'])
    
    def get_enemy_color(self, enemy_type):
        """Get color for different enemy types."""
        colors = {
            'goblin': (0, 128, 0),      # Green
            'orc': (128, 64, 0),        # Brown
            'skeleton': (200, 200, 200), # Light gray
            'troll': (64, 128, 64),     # Dark green
            'spider': (64, 0, 64)       # Purple
        }
        return colors.get(enemy_type, (128, 0, 0))  # Default red
    
    def update(self, player, world, delta_time):
        """Update enemy AI and behavior."""
        if self.state == "DEAD":
            return
        
        self.animation_time += delta_time
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= delta_time
        
        # Check if player is visible
        player_visible = self.can_see_player(player, world)
        
        # Update AI state machine
        if player_visible:
            self.target = player
            self.last_seen_x = player.x
            self.last_seen_y = player.y
            
            distance_to_player = self.distance_to(player.x, player.y)
            
            if distance_to_player <= self.attack_range:
                self.state = "ATTACK"
            else:
                self.state = "CHASE"
        else:
            if self.state == "CHASE":
                # Continue to last seen position
                if self.distance_to(self.last_seen_x, self.last_seen_y) < 0.5:
                    self.state = "IDLE"
            elif self.state == "ATTACK":
                self.state = "IDLE"
        
        # Execute behavior based on state
        if self.state == "IDLE":
            self.behavior_idle(delta_time)
        elif self.state == "PATROL":
            self.behavior_patrol(world, delta_time)
        elif self.state == "CHASE":
            self.behavior_chase(world, delta_time)
        elif self.state == "ATTACK":
            self.behavior_attack(player, delta_time)
        
        # Update movement
        self.update_movement(world, delta_time)
    
    def can_see_player(self, player, world):
        """Check if the enemy can see the player."""
        distance = self.distance_to(player.x, player.y)
        if distance > self.sight_range:
            return False
        
        # Check line of sight
        steps = int(distance * 10)  # 10 steps per unit
        if steps == 0:
            return True
        
        dx = (player.x - self.x) / steps
        dy = (player.y - self.y) / steps
        
        for i in range(1, steps):
            check_x = self.x + dx * i
            check_y = self.y + dy * i
            
            if not world.is_passable(check_x, check_y):
                return False
        
        return True
    
    def behavior_idle(self, delta_time):
        """Idle behavior - stand still or wander."""
        # Occasionally start patrolling
        if np.random.random() < 0.001:  # 0.1% chance per frame
            if len(self.patrol_points) == 0:
                self.create_patrol_route()
            if len(self.patrol_points) > 0:
                self.state = "PATROL"
    
    def behavior_patrol(self, world, delta_time):
        """Patrol behavior - move between patrol points."""
        if len(self.patrol_points) == 0:
            self.state = "IDLE"
            return
        
        target_point = self.patrol_points[self.current_patrol_index]
        distance = self.distance_to(target_point[0], target_point[1])
        
        if distance < 0.5:
            # Reached patrol point, move to next
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
        else:
            # Move toward current patrol point
            self.move_toward(target_point[0], target_point[1], delta_time)
    
    def behavior_chase(self, world, delta_time):
        """Chase behavior - pursue the player."""
        # Simple direct movement toward last seen position
        if self.distance_to(self.last_seen_x, self.last_seen_y) > 0.5:
            self.move_toward(self.last_seen_x, self.last_seen_y, delta_time)
    
    def behavior_attack(self, player, delta_time):
        """Attack behavior - attack the player."""
        if self.attack_cooldown <= 0:
            # Perform attack
            damage = self.damage + np.random.randint(-2, 3)  # Damage variation
            player.take_damage(damage)
            self.attack_cooldown = 2.0  # 2 seconds between attacks
            
            # Face the player
            dx = player.x - self.x
            dy = player.y - self.y
            self.angle = np.arctan2(dy, dx)
    
    def move_toward(self, target_x, target_y, delta_time):
        """Move toward a target position."""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = np.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            # Normalize direction
            dx /= distance
            dy /= distance
            
            # Set velocity
            self.velocity_x = dx * self.speed
            self.velocity_y = dy * self.speed
            self.is_moving = True
            
            # Update facing angle
            self.angle = np.arctan2(dy, dx)
        else:
            self.velocity_x = 0
            self.velocity_y = 0
            self.is_moving = False
    
    def update_movement(self, world, delta_time):
        """Update enemy position with collision detection."""
        if not self.is_moving:
            return
        
        # Calculate new position
        new_x = self.x + self.velocity_x * delta_time
        new_y = self.y + self.velocity_y * delta_time
        
        # Check collision
        if world.is_passable(new_x, self.y):
            self.x = new_x
        else:
            self.velocity_x = 0
        
        if world.is_passable(self.x, new_y):
            self.y = new_y
        else:
            self.velocity_y = 0
        
        # Stop moving if both velocities are zero
        if self.velocity_x == 0 and self.velocity_y == 0:
            self.is_moving = False
    
    def distance_to(self, x, y):
        """Calculate distance to a point."""
        return np.sqrt((self.x - x)**2 + (self.y - y)**2)
    
    def take_damage(self, damage):
        """Apply damage to the enemy."""
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.state = "DEAD"
    
    def create_patrol_route(self):
        """Create a simple patrol route around the starting position."""
        # Create a square patrol route
        offset = 2.0
        self.patrol_points = [
            (self.start_x + offset, self.start_y),
            (self.start_x + offset, self.start_y + offset),
            (self.start_x, self.start_y + offset),
            (self.start_x, self.start_y)
        ]
        self.current_patrol_index = 0
    
    def to_dict(self):
        """Convert enemy to dictionary for saving."""
        return {
            'x': self.x,
            'y': self.y,
            'start_x': self.start_x,
            'start_y': self.start_y,
            'type': self.type,
            'sprite_id': self.sprite_id,
            'health': self.health,
            'max_health': self.max_health,
            'state': self.state,
            'patrol_points': self.patrol_points,
            'current_patrol_index': self.current_patrol_index
        }
    
    def from_dict(self, data):
        """Load enemy from dictionary."""
        self.x = data.get('x', self.x)
        self.y = data.get('y', self.y)
        self.start_x = data.get('start_x', self.start_x)
        self.start_y = data.get('start_y', self.start_y)
        self.type = data.get('type', self.type)
        self.sprite_id = data.get('sprite_id', self.sprite_id)
        self.health = data.get('health', self.health)
        self.max_health = data.get('max_health', self.max_health)
        self.state = data.get('state', self.state)
        self.patrol_points = data.get('patrol_points', [])
        self.current_patrol_index = data.get('current_patrol_index', 0)

class EnemyManager:
    def __init__(self, world, asset_manager):
        """Initialize the enemy manager."""
        self.world = world
        self.asset_manager = asset_manager
        self.enemies = []
        
        # Spawn initial enemies
        self.spawn_initial_enemies()
    
    def spawn_initial_enemies(self):
        """Spawn initial enemies in the world."""
        enemy_spawns = [
            (10, 10, 'goblin'),
            (20, 10, 'orc'),
            (10, 20, 'skeleton'),
            (25, 25, 'spider'),
            (15, 18, 'goblin'),
            (22, 8, 'skeleton')
        ]
        
        for spawn in enemy_spawns:
            x, y, enemy_type = spawn
            if self.world.is_passable(x, y):
                enemy = Enemy(x, y, enemy_type, f"{enemy_type}_sprite")
                self.enemies.append(enemy)
    
    def update(self, player, delta_time):
        """Update all enemies."""
        for enemy in self.enemies[:]:  # Copy list to avoid modification during iteration
            if enemy.state == "DEAD":
                # Remove dead enemies after a delay
                continue
            
            enemy.update(player, self.world, delta_time)
    
    def check_ray_hit(self, start_x, start_y, angle, max_distance):
        """Check if a ray hits any enemy."""
        ray_dx = np.cos(angle)
        ray_dy = np.sin(angle)
        
        closest_enemy = None
        closest_distance = max_distance
        
        for enemy in self.enemies:
            if enemy.state == "DEAD":
                continue
            
            # Vector from ray start to enemy
            to_enemy_x = enemy.x - start_x
            to_enemy_y = enemy.y - start_y
            
            # Project enemy position onto ray direction
            projection = to_enemy_x * ray_dx + to_enemy_y * ray_dy
            
            if projection < 0 or projection > max_distance:
                continue  # Enemy is behind ray start or too far
            
            # Calculate perpendicular distance from ray to enemy
            perp_distance = abs(to_enemy_x * ray_dy - to_enemy_y * ray_dx)
            
            if perp_distance <= 0.5:  # Enemy radius
                distance = projection
                if distance < closest_distance:
                    closest_distance = distance
                    closest_enemy = enemy
        
        return closest_enemy
    
    def get_visible_enemies(self, player):
        """Get enemies visible to the player."""
        visible_enemies = []
        
        for enemy in self.enemies:
            if enemy.state == "DEAD":
                continue
            
            # Calculate distance
            distance = np.sqrt((enemy.x - player.x)**2 + (enemy.y - player.y)**2)
            
            if distance <= MAX_RENDER_DISTANCE:
                visible_enemies.append(enemy)
        
        return visible_enemies
    
    def spawn_enemy(self, x, y, enemy_type):
        """Spawn a new enemy at the specified location."""
        if self.world.is_passable(x, y):
            enemy = Enemy(x, y, enemy_type, f"{enemy_type}_sprite")
            self.enemies.append(enemy)
            return enemy
        return None
    
    def remove_enemy(self, enemy):
        """Remove an enemy from the game."""
        if enemy in self.enemies:
            self.enemies.remove(enemy)
    
    def get_enemies_in_area(self, center_x, center_y, radius):
        """Get all enemies within a specified area."""
        enemies_in_area = []
        
        for enemy in self.enemies:
            if enemy.state == "DEAD":
                continue
            
            distance = np.sqrt((enemy.x - center_x)**2 + (enemy.y - center_y)**2)
            if distance <= radius:
                enemies_in_area.append(enemy)
        
        return enemies_in_area
    
    def clear_dead_enemies(self):
        """Remove all dead enemies from the game."""
        self.enemies = [enemy for enemy in self.enemies if enemy.state != "DEAD"]
    
    def to_dict(self):
        """Convert enemy manager state to dictionary for saving."""
        return {
            'enemies': [enemy.to_dict() for enemy in self.enemies]
        }
    
    def from_dict(self, data):
        """Load enemy manager state from dictionary."""
        self.enemies.clear()
        
        for enemy_data in data.get('enemies', []):
            enemy = Enemy(0, 0, 'goblin', 'goblin_sprite')  # Temporary values
            enemy.from_dict(enemy_data)
            self.enemies.append(enemy)
