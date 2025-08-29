"""
Main menu system for the pseudo-3D RPG.
Handles title screen, main menu, and game options.
"""

import pygame
from config import *

class MainMenu:
    def __init__(self, asset_manager):
        """Initialize the main menu system."""
        self.asset_manager = asset_manager
        
        # Menu state
        self.current_menu = "MAIN"  # MAIN, OPTIONS, CREDITS
        self.selected_option = 0
        
        # Menu options
        self.main_menu_options = [
            "Start New Game",
            "Load Game",
            "Options",
            "Credits",
            "Quit"
        ]
        
        self.options_menu_items = [
            "Master Volume",
            "Music Volume",
            "SFX Volume",
            "Mouse Sensitivity",
            "Back"
        ]
        
        # Load fonts
        self.font_title = pygame.font.Font(None, 72)
        self.font_menu = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        # Colors
        self.bg_color = (20, 20, 40)
        self.title_color = (255, 255, 255)
        self.menu_color = (200, 200, 200)
        self.selected_color = (255, 255, 100)
        self.border_color = (100, 100, 100)
        
        # Animation
        self.title_pulse = 0.0
        self.menu_transition = 0.0
        
        # Settings (would normally be loaded from config file)
        self.master_volume = 0.8
        self.music_volume = 0.7
        self.sfx_volume = 0.9
        self.mouse_sensitivity = 1.0
        
        # Background animation
        self.background_stars = self.generate_background_stars()
        self.star_time = 0.0
    
    def generate_background_stars(self):
        """Generate background stars for animated background."""
        import random
        stars = []
        for _ in range(100):
            brightness = random.uniform(0.3, 1.0)
            star = {
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'brightness': brightness,
                'current_brightness': brightness,  # Initialize current brightness
                'twinkle_speed': random.uniform(1.0, 3.0),
                'size': random.choice([1, 1, 1, 2])  # Mostly small stars
            }
            stars.append(star)
        return stars
    
    def update(self, delta_time):
        """Update menu animations and state."""
        self.title_pulse += delta_time * 2
        self.menu_transition += delta_time * 3
        self.star_time += delta_time
        
        # Update star animation
        import math
        for star in self.background_stars:
            star['current_brightness'] = star['brightness'] * (
                0.7 + 0.3 * math.sin(self.star_time * star['twinkle_speed'])
            )
    
    def handle_event(self, event):
        """Handle menu input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.navigate_up()
            elif event.key == pygame.K_DOWN:
                self.navigate_down()
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self.select_current_option()
            elif event.key == pygame.K_ESCAPE:
                if self.current_menu != "MAIN":
                    self.current_menu = "MAIN"
                    self.selected_option = 0
                else:
                    return "QUIT"
        
        elif event.type == pygame.MOUSEMOTION:
            # Update selection based on mouse position
            mouse_x, mouse_y = event.pos
            self.update_selection_from_mouse(mouse_x, mouse_y)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self.select_current_option()
        
        return None
    
    def navigate_up(self):
        """Navigate up in the current menu."""
        if self.current_menu == "MAIN":
            self.selected_option = (self.selected_option - 1) % len(self.main_menu_options)
        elif self.current_menu == "OPTIONS":
            self.selected_option = (self.selected_option - 1) % len(self.options_menu_items)
    
    def navigate_down(self):
        """Navigate down in the current menu."""
        if self.current_menu == "MAIN":
            self.selected_option = (self.selected_option + 1) % len(self.main_menu_options)
        elif self.current_menu == "OPTIONS":
            self.selected_option = (self.selected_option + 1) % len(self.options_menu_items)
    
    def update_selection_from_mouse(self, mouse_x, mouse_y):
        """Update menu selection based on mouse position."""
        # Calculate which menu item the mouse is over
        menu_start_y = SCREEN_HEIGHT // 2 + 50
        item_height = 60
        
        if self.current_menu == "MAIN":
            options = self.main_menu_options
        elif self.current_menu == "OPTIONS":
            options = self.options_menu_items
        else:
            return
        
        for i, option in enumerate(options):
            item_y = menu_start_y + i * item_height
            if item_y <= mouse_y <= item_y + item_height:
                self.selected_option = i
                break
    
    def select_current_option(self):
        """Handle selection of the current menu option."""
        if self.current_menu == "MAIN":
            option = self.main_menu_options[self.selected_option]
            
            if option == "Start New Game":
                return "START_GAME"
            elif option == "Load Game":
                return "LOAD_GAME"
            elif option == "Options":
                self.current_menu = "OPTIONS"
                self.selected_option = 0
            elif option == "Credits":
                self.current_menu = "CREDITS"
                self.selected_option = 0
            elif option == "Quit":
                return "QUIT"
        
        elif self.current_menu == "OPTIONS":
            option = self.options_menu_items[self.selected_option]
            
            if option == "Master Volume":
                self.adjust_master_volume()
            elif option == "Music Volume":
                self.adjust_music_volume()
            elif option == "SFX Volume":
                self.adjust_sfx_volume()
            elif option == "Mouse Sensitivity":
                self.adjust_mouse_sensitivity()
            elif option == "Back":
                self.current_menu = "MAIN"
                self.selected_option = 0
        
        elif self.current_menu == "CREDITS":
            # Any key returns to main menu from credits
            self.current_menu = "MAIN"
            self.selected_option = 0
        
        return None
    
    def adjust_master_volume(self):
        """Adjust master volume setting."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.master_volume = max(0.0, self.master_volume - 0.1)
        elif keys[pygame.K_RIGHT]:
            self.master_volume = min(1.0, self.master_volume + 0.1)
    
    def adjust_music_volume(self):
        """Adjust music volume setting."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.music_volume = max(0.0, self.music_volume - 0.1)
        elif keys[pygame.K_RIGHT]:
            self.music_volume = min(1.0, self.music_volume + 0.1)
    
    def adjust_sfx_volume(self):
        """Adjust SFX volume setting."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.sfx_volume = max(0.0, self.sfx_volume - 0.1)
        elif keys[pygame.K_RIGHT]:
            self.sfx_volume = min(1.0, self.sfx_volume + 0.1)
    
    def adjust_mouse_sensitivity(self):
        """Adjust mouse sensitivity setting."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.mouse_sensitivity = max(0.1, self.mouse_sensitivity - 0.1)
        elif keys[pygame.K_RIGHT]:
            self.mouse_sensitivity = min(3.0, self.mouse_sensitivity + 0.1)
    
    def render(self, screen):
        """Render the current menu."""
        # Clear screen with animated background
        screen.fill(self.bg_color)
        
        # Render animated background
        self.render_background(screen)
        
        if self.current_menu == "MAIN":
            self.render_main_menu(screen)
        elif self.current_menu == "OPTIONS":
            self.render_options_menu(screen)
        elif self.current_menu == "CREDITS":
            self.render_credits(screen)
    
    def render_background(self, screen):
        """Render animated starfield background."""
        for star in self.background_stars:
            brightness = int(255 * star['current_brightness'])
            color = (brightness, brightness, brightness)
            
            if star['size'] == 1:
                screen.set_at((int(star['x']), int(star['y'])), color)
            else:
                pygame.draw.circle(screen, color, (int(star['x']), int(star['y'])), star['size'])
    
    def render_main_menu(self, screen):
        """Render the main menu."""
        # Title
        import math
        title_scale = 1.0 + 0.1 * math.sin(self.title_pulse)
        title_text = "PSEUDO-3D RPG"
        title_surface = self.font_title.render(title_text, True, self.title_color)
        
        # Scale title for pulse effect
        if title_scale != 1.0:
            title_width = int(title_surface.get_width() * title_scale)
            title_height = int(title_surface.get_height() * title_scale)
            title_surface = pygame.transform.scale(title_surface, (title_width, title_height))
        
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle_text = "A Classic RPG Experience"
        subtitle_surface = self.font_small.render(subtitle_text, True, self.menu_color)
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        screen.blit(subtitle_surface, subtitle_rect)
        
        # Menu options
        menu_start_y = SCREEN_HEIGHT // 2 + 50
        for i, option in enumerate(self.main_menu_options):
            y_pos = menu_start_y + i * 60
            
            # Determine color based on selection
            if i == self.selected_option:
                color = self.selected_color
                # Draw selection highlight
                highlight_rect = pygame.Rect(
                    SCREEN_WIDTH // 2 - 150, y_pos - 5,
                    300, 50
                )
                pygame.draw.rect(screen, (50, 50, 50), highlight_rect)
                pygame.draw.rect(screen, self.border_color, highlight_rect, 2)
            else:
                color = self.menu_color
            
            # Render menu text
            option_surface = self.font_menu.render(option, True, color)
            option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos + 15))
            screen.blit(option_surface, option_rect)
        
        # Instructions
        instructions = "Use arrow keys or mouse to navigate • Enter or click to select"
        instruction_surface = self.font_small.render(instructions, True, self.menu_color)
        instruction_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(instruction_surface, instruction_rect)
    
    def render_options_menu(self, screen):
        """Render the options menu."""
        # Title
        title_text = "Options"
        title_surface = self.font_title.render(title_text, True, self.title_color)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_surface, title_rect)
        
        # Options
        menu_start_y = 200
        for i, option in enumerate(self.options_menu_items[:-1]):  # Exclude "Back"
            y_pos = menu_start_y + i * 60
            
            # Get current value for this option
            if option == "Master Volume":
                value = f"{int(self.master_volume * 100)}%"
            elif option == "Music Volume":
                value = f"{int(self.music_volume * 100)}%"
            elif option == "SFX Volume":
                value = f"{int(self.sfx_volume * 100)}%"
            elif option == "Mouse Sensitivity":
                value = f"{self.mouse_sensitivity:.1f}"
            else:
                value = ""
            
            # Determine color based on selection
            if i == self.selected_option:
                color = self.selected_color
                # Draw selection highlight
                highlight_rect = pygame.Rect(
                    SCREEN_WIDTH // 2 - 200, y_pos - 5,
                    400, 50
                )
                pygame.draw.rect(screen, (50, 50, 50), highlight_rect)
                pygame.draw.rect(screen, self.border_color, highlight_rect, 2)
            else:
                color = self.menu_color
            
            # Render option name
            option_text = f"{option}: {value}"
            option_surface = self.font_menu.render(option_text, True, color)
            option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos + 15))
            screen.blit(option_surface, option_rect)
        
        # Back button
        back_y = menu_start_y + len(self.options_menu_items[:-1]) * 60 + 40
        back_color = self.selected_color if self.selected_option == len(self.options_menu_items) - 1 else self.menu_color
        
        if self.selected_option == len(self.options_menu_items) - 1:
            highlight_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - 100, back_y - 5,
                200, 50
            )
            pygame.draw.rect(screen, (50, 50, 50), highlight_rect)
            pygame.draw.rect(screen, self.border_color, highlight_rect, 2)
        
        back_surface = self.font_menu.render("Back", True, back_color)
        back_rect = back_surface.get_rect(center=(SCREEN_WIDTH // 2, back_y + 15))
        screen.blit(back_surface, back_rect)
        
        # Instructions
        instructions = "Use Left/Right arrows to adjust values • Enter to select"
        instruction_surface = self.font_small.render(instructions, True, self.menu_color)
        instruction_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(instruction_surface, instruction_rect)
    
    def render_credits(self, screen):
        """Render the credits screen."""
        # Title
        title_text = "Credits"
        title_surface = self.font_title.render(title_text, True, self.title_color)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_surface, title_rect)
        
        # Credits text
        credits_lines = [
            "",
            "Pseudo-3D RPG",
            "",
            "A classic-style role-playing game",
            "featuring raycasting and Mode 7 rendering",
            "",
            "Built with Python and Pygame",
            "",
            "Features:",
            "• Real-time 3D rendering",
            "• Combat and spell systems",
            "• Character progression",
            "• Procedural world generation",
            "",
            "Thank you for playing!",
            "",
            "Press any key to return to main menu"
        ]
        
        start_y = 180
        for i, line in enumerate(credits_lines):
            if line:  # Skip empty lines
                line_surface = self.font_small.render(line, True, self.menu_color)
                line_rect = line_surface.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 30))
                screen.blit(line_surface, line_rect)
