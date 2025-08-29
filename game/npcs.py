"""
NPC system with dialogue for the pseudo-3D RPG.
Handles NPC interactions, dialogue trees, and quest systems.
"""

import pygame
import json
from config import *

class NPC:
    def __init__(self, x, y, npc_type, name, sprite_id):
        """Initialize an NPC."""
        self.x = x
        self.y = y
        self.type = npc_type  # 'merchant', 'guard', 'villager', 'quest_giver'
        self.name = name
        self.sprite_id = sprite_id
        
        # Dialogue system
        self.dialogue_tree = {}
        self.current_dialogue_node = "start"
        self.has_talked = False
        
        # Movement and AI
        self.facing_angle = 0.0
        self.patrol_points = []
        self.current_patrol_target = 0
        self.movement_speed = 0.5
        
        # Trade system (for merchants)
        self.inventory = []
        self.gold = 100
        
        # Quest system
        self.quests = []
        self.can_give_quests = False
        
        # Generate appropriate dialogue based on type
        self.generate_dialogue()
        
    def generate_dialogue(self):
        """Generate dialogue based on NPC type."""
        if self.type == "merchant":
            self.dialogue_tree = {
                "start": {
                    "text": f"Greetings, traveler! I'm {self.name}, a humble merchant. Care to see my wares?",
                    "options": [
                        ("Show me your goods", "trade"),
                        ("Any news from the road?", "news"),
                        ("Farewell", "goodbye")
                    ]
                },
                "trade": {
                    "text": "Here's what I have for sale. Gold speaks louder than words!",
                    "options": [
                        ("I'll browse your wares", "shop"),
                        ("Maybe later", "start")
                    ],
                    "action": "open_shop"
                },
                "news": {
                    "text": "Strange creatures have been spotted in the deeper tunnels. Be careful down there!",
                    "options": [
                        ("Thanks for the warning", "start"),
                        ("Tell me more", "danger_details")
                    ]
                },
                "danger_details": {
                    "text": "I've heard tell of skeletal warriors and worse things lurking in the shadows. You'll need good weapons!",
                    "options": [
                        ("I'll be prepared", "start")
                    ]
                },
                "goodbye": {
                    "text": "Safe travels, friend!",
                    "options": [],
                    "action": "close_dialogue"
                }
            }
        
        elif self.type == "guard":
            self.dialogue_tree = {
                "start": {
                    "text": f"Halt! I am {self.name}, guardian of this place. State your business!",
                    "options": [
                        ("I'm just exploring", "exploring"),
                        ("I'm hunting monsters", "monster_hunter"),
                        ("Apologies, I'll leave", "goodbye")
                    ]
                },
                "exploring": {
                    "text": "Exploration is fine, but stay out of the restricted areas. The deeper levels are dangerous.",
                    "options": [
                        ("Where are the restricted areas?", "restricted"),
                        ("I understand", "start")
                    ]
                },
                "restricted": {
                    "text": "The prison cells and the boss arena are off-limits to civilians. Only trained warriors may enter.",
                    "options": [
                        ("I am a warrior", "prove_worth"),
                        ("I'll stay away", "start")
                    ]
                },
                "prove_worth": {
                    "text": "Prove yourself by clearing out some monsters, then we'll talk.",
                    "options": [
                        ("I'll do it", "start")
                    ]
                },
                "monster_hunter": {
                    "text": "Good! We need brave souls like you. Clear the training grounds and I'll reward you.",
                    "options": [
                        ("Consider it done", "start")
                    ],
                    "action": "give_quest"
                },
                "goodbye": {
                    "text": "Move along then.",
                    "options": [],
                    "action": "close_dialogue"
                }
            }
        
        else:  # villager or default
            self.dialogue_tree = {
                "start": {
                    "text": f"Hello there! I'm {self.name}. It's not often we see adventurers around here.",
                    "options": [
                        ("What is this place?", "about_place"),
                        ("Any dangers I should know about?", "dangers"),
                        ("Goodbye", "goodbye")
                    ]
                },
                "about_place": {
                    "text": "This is an ancient dungeon complex. Once a fortress, now overrun with monsters and mysteries.",
                    "options": [
                        ("How did it become like this?", "history"),
                        ("Interesting", "start")
                    ]
                },
                "history": {
                    "text": "Long ago, dark magic corrupted this place. Now the undead roam these halls.",
                    "options": [
                        ("I'll help clear them out", "start")
                    ]
                },
                "dangers": {
                    "text": "The deeper you go, the more dangerous it becomes. Stick to the upper levels if you value your life.",
                    "options": [
                        ("Thanks for the warning", "start")
                    ]
                },
                "goodbye": {
                    "text": "Stay safe out there!",
                    "options": [],
                    "action": "close_dialogue"
                }
            }
    
    def interact(self, player):
        """Handle interaction with player."""
        self.has_talked = True
        if self.current_dialogue_node not in self.dialogue_tree:
            self.current_dialogue_node = "start"
        
        return self.dialogue_tree[self.current_dialogue_node]
    
    def choose_dialogue_option(self, option_index):
        """Choose a dialogue option and advance conversation."""
        if self.current_dialogue_node in self.dialogue_tree:
            current_node = self.dialogue_tree[self.current_dialogue_node]
            if option_index < len(current_node["options"]):
                _, next_node = current_node["options"][option_index]
                self.current_dialogue_node = next_node
                
                # Handle any actions
                if "action" in current_node:
                    return current_node["action"]
        return None
    
    def update(self, delta_time):
        """Update NPC state."""
        # Simple patrol behavior
        if self.patrol_points:
            target = self.patrol_points[self.current_patrol_target]
            dx = target[0] - self.x
            dy = target[1] - self.y
            distance = (dx*dx + dy*dy)**0.5
            
            if distance > 0.5:
                self.x += (dx / distance) * self.movement_speed * delta_time
                self.y += (dy / distance) * self.movement_speed * delta_time
            else:
                self.current_patrol_target = (self.current_patrol_target + 1) % len(self.patrol_points)

class NPCManager:
    def __init__(self, world, asset_manager):
        """Initialize NPC management system."""
        self.world = world
        self.asset_manager = asset_manager
        self.npcs = []
        
    def spawn_initial_npcs(self):
        """Spawn initial NPCs in the world."""
        npc_spawns = [
            (7, 7, 'merchant', 'Gareth the Trader'),
            (22, 22, 'guard', 'Captain Marcus'),
            (48, 20, 'villager', 'Old Tom'),
            (35, 50, 'guard', 'Dungeon Keeper'),
        ]
        
        for spawn in npc_spawns:
            x, y, npc_type, name = spawn
            if self.world.is_passable(x, y):
                npc = NPC(x, y, npc_type, name, f"{npc_type}_sprite")
                
                # Add some patrol points for guards
                if npc_type == 'guard':
                    npc.patrol_points = [(x, y), (x+2, y), (x+2, y+2), (x, y+2)]
                
                self.npcs.append(npc)
    
    def get_npc_at_position(self, x, y, radius=1.0):
        """Find NPC near given position."""
        for npc in self.npcs:
            dx = npc.x - x
            dy = npc.y - y
            distance = (dx*dx + dy*dy)**0.5
            if distance <= radius:
                return npc
        return None
    
    def update(self, delta_time):
        """Update all NPCs."""
        for npc in self.npcs:
            npc.update(delta_time)
    
    def get_visible_npcs(self, player):
        """Get NPCs visible to the player."""
        visible_npcs = []
        for npc in self.npcs:
            # Simple distance check for now
            dx = npc.x - player.x
            dy = npc.y - player.y
            distance = (dx*dx + dy*dy)**0.5
            if distance <= MAX_RENDER_DISTANCE:
                visible_npcs.append(npc)
        return visible_npcs

class DialogueUI:
    def __init__(self, asset_manager):
        """Initialize dialogue UI system."""
        self.asset_manager = asset_manager
        self.active = False
        self.current_npc = None
        self.current_dialogue = None
        self.selected_option = 0
        
        # UI appearance
        self.dialogue_bg_color = (20, 20, 30)
        self.dialogue_border_color = (100, 100, 120)
        self.text_color = (255, 255, 255)
        self.option_color = (200, 200, 200)
        self.selected_option_color = (255, 255, 100)
        
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 32)
        
    def start_dialogue(self, npc, player):
        """Start dialogue with an NPC."""
        self.active = True
        self.current_npc = npc
        self.current_dialogue = npc.interact(player)
        self.selected_option = 0
        
    def handle_input(self, event):
        """Handle dialogue input."""
        if not self.active:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = max(0, self.selected_option - 1)
            elif event.key == pygame.K_DOWN:
                max_options = len(self.current_dialogue.get("options", []))
                self.selected_option = min(max_options - 1, self.selected_option + 1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.choose_option()
            elif event.key == pygame.K_ESCAPE:
                self.close_dialogue()
    
    def choose_option(self):
        """Choose the selected dialogue option."""
        if not self.current_dialogue or not self.current_npc:
            return
            
        options = self.current_dialogue.get("options", [])
        if self.selected_option < len(options):
            action = self.current_npc.choose_dialogue_option(self.selected_option)
            
            if action == "close_dialogue":
                self.close_dialogue()
            else:
                self.current_dialogue = self.current_npc.interact(None)
                self.selected_option = 0
        else:
            self.close_dialogue()
    
    def close_dialogue(self):
        """Close dialogue interface."""
        self.active = False
        self.current_npc = None
        self.current_dialogue = None
        self.selected_option = 0
        
    def render(self, screen):
        """Render dialogue interface."""
        if not self.active or not self.current_dialogue:
            return
            
        # Dialogue box
        dialogue_width = 600
        dialogue_height = 200
        dialogue_x = (SCREEN_WIDTH - dialogue_width) // 2
        dialogue_y = SCREEN_HEIGHT - dialogue_height - 50
        
        dialogue_rect = pygame.Rect(dialogue_x, dialogue_y, dialogue_width, dialogue_height)
        
        # Background
        pygame.draw.rect(screen, self.dialogue_bg_color, dialogue_rect)
        pygame.draw.rect(screen, self.dialogue_border_color, dialogue_rect, 3)
        
        # NPC name
        if self.current_npc:
            name_surface = self.font_medium.render(self.current_npc.name, True, self.text_color)
            screen.blit(name_surface, (dialogue_x + 10, dialogue_y + 5))
        
        # Dialogue text (wrap text)
        text = self.current_dialogue.get("text", "")
        wrapped_lines = self.wrap_text(text, dialogue_width - 20)
        
        y_offset = 35
        for line in wrapped_lines:
            text_surface = self.font_small.render(line, True, self.text_color)
            screen.blit(text_surface, (dialogue_x + 10, dialogue_y + y_offset))
            y_offset += 25
        
        # Options
        options = self.current_dialogue.get("options", [])
        if options:
            y_offset += 10
            for i, (option_text, _) in enumerate(options):
                color = self.selected_option_color if i == self.selected_option else self.option_color
                option_surface = self.font_small.render(f"{i+1}. {option_text}", True, color)
                screen.blit(option_surface, (dialogue_x + 20, dialogue_y + y_offset))
                y_offset += 25
        
        # Instructions
        instruction = "Use arrows and Enter to select, ESC to close"
        instruction_surface = self.font_small.render(instruction, True, (150, 150, 150))
        screen.blit(instruction_surface, (dialogue_x + 10, dialogue_rect.bottom - 20))
    
    def wrap_text(self, text, max_width):
        """Wrap text to fit within max width."""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            text_width = self.font_small.size(test_line)[0]
            
            if text_width <= max_width - 20:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines