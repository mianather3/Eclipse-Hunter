import pygame
import math
import sys
import random

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 1200, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Eclipse Hunter - Solar System Simulator")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (169, 169, 169)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
ORANGE = (255, 140, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (50, 50, 50)
LIGHT_BLUE = (173, 216, 230)
GOLD = (255, 215, 0)
GREEN = (50, 205, 50)

# Star class for background
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.brightness = random.randint(100, 255)
        
    def draw(self, surface):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(surface, color, (self.x, self.y), self.size)

# Planet class with additional info
class Planet:
    def __init__(self, name, distance, size, color, speed, info):
        self.name = name
        self.distance = distance
        self.size = size
        self.color = color
        self.speed = speed
        self.angle = random.uniform(0, 2 * math.pi)  # Random starting position
        self.x = 0
        self.y = 0
        self.info = info
        self.selected = False
        
    def update(self, speed_mult=1):
        self.angle += self.speed * speed_mult
        self.x = WIDTH // 2 + self.distance * math.cos(self.angle)
        self.y = HEIGHT // 2 + self.distance * math.sin(self.angle)
    
    def draw(self, surface):
        # Draw orbit path
        pygame.draw.circle(surface, DARK_GRAY, (WIDTH // 2, HEIGHT // 2), 
                         self.distance, 1)
        
        # Draw glow effect
        glow_surface = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        for i in range(3):
            alpha = 30 - i * 10
            glow_color = (*self.color, alpha)
            pygame.draw.circle(glow_surface, glow_color, 
                             (self.size * 2, self.size * 2), 
                             self.size + i * 3)
        surface.blit(glow_surface, (int(self.x) - self.size * 2, 
                                   int(self.y) - self.size * 2))
        
        # Draw planet
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 
                         self.size)
        
        # Highlight if selected
        if self.selected:
            pygame.draw.circle(surface, GOLD, (int(self.x), int(self.y)), 
                             self.size + 3, 2)
        
        # Draw planet name
        font = pygame.font.Font(None, 20)
        text = font.render(self.name, True, WHITE)
        surface.blit(text, (int(self.x) - 20, int(self.y) - 30))
    
    def is_clicked(self, pos):
        distance = math.sqrt((pos[0] - self.x)**2 + (pos[1] - self.y)**2)
        return distance <= self.size + 5

# Moon class
class Moon:
    def __init__(self, planet, distance, size, speed):
        self.planet = planet
        self.distance = distance
        self.size = size
        self.speed = speed
        self.angle = 0
        self.x = 0
        self.y = 0
        
    def update(self, speed_mult=1):
        self.angle += self.speed * speed_mult
        self.x = self.planet.x + self.distance * math.cos(self.angle)
        self.y = self.planet.y + self.distance * math.sin(self.angle)
    
    def draw(self, surface):
        # Draw moon glow
        glow_surface = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (200, 200, 200, 20), 
                         (self.size * 2, self.size * 2), self.size + 2)
        surface.blit(glow_surface, (int(self.x) - self.size * 2, 
                                   int(self.y) - self.size * 2))
        
        pygame.draw.circle(surface, GRAY, (int(self.x), int(self.y)), 
                         self.size)

# Info Panel class
class InfoPanel:
    def __init__(self, planet):
        self.planet = planet
        self.width = 300
        self.height = 200
        self.x = WIDTH - self.width - 20
        self.y = HEIGHT - self.height - 20
        
    def draw(self, surface):
        # Draw semi-transparent background
        panel_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (0, 0, 0, 200), 
                        (0, 0, self.width, self.height), border_radius=10)
        pygame.draw.rect(panel_surface, GOLD, 
                        (0, 0, self.width, self.height), 2, border_radius=10)
        
        # Draw title
        font_title = pygame.font.Font(None, 32)
        title = font_title.render(self.planet.name, True, GOLD)
        panel_surface.blit(title, (10, 10))
        
        # Draw info
        font_info = pygame.font.Font(None, 22)
        y_offset = 50
        for line in self.planet.info:
            text = font_info.render(line, True, WHITE)
            panel_surface.blit(text, (10, y_offset))
            y_offset += 30
        
        surface.blit(panel_surface, (self.x, self.y))

# Statistics Panel class
class StatsPanel:
    def __init__(self):
        self.eclipse_count = 0
        self.total_frames = 0
        self.last_eclipse_frame = -1000
        
    def update(self, eclipse_detected):
        self.total_frames += 1
        if eclipse_detected and self.total_frames - self.last_eclipse_frame > 60:
            self.eclipse_count += 1
            self.last_eclipse_frame = self.total_frames
            return True  # New eclipse detected
        return False
    
    def draw(self, surface):
        # Calculate time (1 frame = 1 day in simulation at 1x speed)
        days = self.total_frames // 60
        years = days // 365
        months = (days % 365) // 30
        
        # Draw panel background in TOP-RIGHT
        panel_width = 280
        panel_height = 140
        panel_x = WIDTH - panel_width - 10  # Top-right position
        panel_y = 10  # Top position
        
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (0, 0, 50, 220), 
                        (0, 0, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(panel_surface, LIGHT_BLUE, 
                        (0, 0, panel_width, panel_height), 2, border_radius=10)
        
        # Draw stats
        font_title = pygame.font.Font(None, 28)
        font_text = pygame.font.Font(None, 24)
        
        title = font_title.render("ECLIPSE TRACKER", True, LIGHT_BLUE)
        panel_surface.blit(title, (10, 10))
        
        eclipse_text = font_text.render(f"Eclipses Detected: {self.eclipse_count}", 
                                       True, WHITE)
        panel_surface.blit(eclipse_text, (10, 45))
        
        time_text = font_text.render(f"Time Elapsed: {years}y {months}m", 
                                    True, WHITE)
        panel_surface.blit(time_text, (10, 75))
        
        if self.eclipse_count > 0:
            avg_days = days / self.eclipse_count if self.eclipse_count > 0 else 0
            avg_text = font_text.render(f"Avg: Every {int(avg_days)} days", 
                                       True, GREEN)
            panel_surface.blit(avg_text, (10, 105))
        
        surface.blit(panel_surface, (panel_x, panel_y))

# Function to check if eclipse is happening
def check_eclipse(sun_pos, planet, moon):
    sun_to_planet = math.sqrt((planet.x - sun_pos[0])**2 + 
                             (planet.y - sun_pos[1])**2)
    sun_to_moon = math.sqrt((moon.x - sun_pos[0])**2 + 
                           (moon.y - sun_pos[1])**2)
    moon_to_planet = math.sqrt((moon.x - planet.x)**2 + 
                              (moon.y - planet.y)**2)
    
    if sun_to_moon < sun_to_planet and moon_to_planet < 50:
        return True
    return False

# Create sound effect (simple beep using pygame)
def play_eclipse_sound():
    try:
        # Try to use numpy for sound generation if available
        import numpy as np
        sample_rate = 22050
        duration = 0.2
        frequency = 523  # C note
        
        # Generate sound wave
        t = np.linspace(0, duration, int(sample_rate * duration))
        wave = np.sin(2 * np.pi * frequency * t)
        
        # Apply fade out to avoid clicking
        fade = np.linspace(1, 0, len(wave))
        wave = wave * fade
        
        # Convert to 16-bit integers
        wave = np.int16(wave * 32767)
        stereo_wave = np.column_stack((wave, wave))
        
        sound = pygame.sndarray.make_sound(stereo_wave)
        sound.play()
    except ImportError:
        # Fallback: Try without numpy
        try:
            sample_rate = 22050
            duration = 0.2
            frequency = 523
            
            n_samples = int(round(duration * sample_rate))
            buf = []
            for i in range(n_samples):
                # Generate sine wave with fade out
                fade = 1 - (i / n_samples)
                value = int(32767 * fade * math.sin(2 * math.pi * frequency * i / sample_rate))
                buf.append([value, value])
            
            sound = pygame.sndarray.make_sound(buf)
            sound.play()
        except:
            # If sound still doesn't work, just skip it silently
            pass
    except:
        pass

# Create stars
stars = [Star() for _ in range(150)]

# Create celestial bodies
sun_pos = (WIDTH // 2, HEIGHT // 2)
sun_size = 35

# Planet information
mercury = Planet("Mercury", 100, 7, GRAY, 0.04, 
                ["Distance: 57.9M km", "Orbital Period: 88 days", 
                 "Smallest planet", "No atmosphere"])
venus = Planet("Venus", 150, 11, ORANGE, 0.03,
              ["Distance: 108.2M km", "Orbital Period: 225 days",
               "Hottest planet", "Thick atmosphere"])
earth = Planet("Earth", 210, 13, BLUE, 0.02,
              ["Distance: 149.6M km", "Orbital Period: 365 days",
               "Our home planet", "Has liquid water"])
mars = Planet("Mars", 280, 9, RED, 0.018,
             ["Distance: 227.9M km", "Orbital Period: 687 days",
              "The Red Planet", "Has ice caps"])

planets = [mercury, venus, earth, mars]

# Create moon for Earth
moon = Moon(earth, 35, 5, 0.08)

# Create stats panel
stats = StatsPanel()

# Game state
running = True
speed_multiplier = 1
paused = False
eclipse_detected = False
eclipse_animation_timer = 0
selected_planet = None
show_instructions = True

# Main game loop
while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_UP:
                speed_multiplier = min(10, speed_multiplier + 0.5)
            elif event.key == pygame.K_DOWN:
                speed_multiplier = max(0.5, speed_multiplier - 0.5)
            elif event.key == pygame.K_h:
                show_instructions = not show_instructions
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # Check if any planet was clicked
            for planet in planets:
                if planet.is_clicked(mouse_pos):
                    # Toggle selection
                    if selected_planet == planet:
                        selected_planet = None
                        planet.selected = False
                    else:
                        if selected_planet:
                            selected_planet.selected = False
                        selected_planet = planet
                        planet.selected = True
                    break
            else:
                # Clicked elsewhere, deselect
                if selected_planet:
                    selected_planet.selected = False
                    selected_planet = None
    
    # Clear screen with black
    screen.fill(BLACK)
    
    # Draw stars
    for star in stars:
        star.draw(screen)
    
    if not paused:
        # Update all planets
        for planet in planets:
            planet.update(speed_mult=speed_multiplier)
        
        # Update moon
        moon.update(speed_mult=speed_multiplier)
        
        # Check for eclipse
        eclipse_detected = check_eclipse(sun_pos, earth, moon)
        
        # Update stats and check for new eclipse
        new_eclipse = stats.update(eclipse_detected)
        if new_eclipse:
            eclipse_animation_timer = 60  # Show for 1 second
    
    # Countdown eclipse animation timer
    if eclipse_animation_timer > 0:
        eclipse_animation_timer -= 1
    
    # Draw sun with glow
    for i in range(5):
        alpha = 40 - i * 8
        glow_color = (255, 255, 0, alpha)
        glow_surface = pygame.Surface((sun_size * 2 + i * 10, sun_size * 2 + i * 10), 
                                      pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, glow_color, 
                         (sun_size + i * 5, sun_size + i * 5), 
                         sun_size + i * 5)
        screen.blit(glow_surface, (sun_pos[0] - sun_size - i * 5, 
                                  sun_pos[1] - sun_size - i * 5))
    
    pygame.draw.circle(screen, YELLOW, sun_pos, sun_size)
    
    # Draw planets
    for planet in planets:
        planet.draw(screen)
    
    # Draw moon
    moon.draw(screen)
    
    # Draw eclipse indicator with animation
    if eclipse_animation_timer > 0:
        pulse = 1 + 0.3 * math.sin(eclipse_animation_timer * 0.3)
        font = pygame.font.Font(None, int(60 * pulse))
        text = font.render("ECLIPSE!", True, RED)
        text_rect = text.get_rect(center=(WIDTH // 2, 80))
        
        # Draw shadow for text
        shadow = font.render("ECLIPSE!", True, (100, 0, 0))
        screen.blit(shadow, (text_rect.x + 3, text_rect.y + 3))
        screen.blit(text, text_rect)
        
        # Draw eclipse effect circle
        pygame.draw.circle(screen, (255, 0, 0, 100), 
                         (int(earth.x), int(earth.y)), 
                         int(45 * pulse), 3)
    
    # Draw instructions panel
    if show_instructions:
        inst_width = 280
        inst_height = 180
        inst_surface = pygame.Surface((inst_width, inst_height), pygame.SRCALPHA)
        pygame.draw.rect(inst_surface, (0, 50, 0, 220), 
                        (0, 0, inst_width, inst_height), border_radius=10)
        pygame.draw.rect(inst_surface, GREEN, 
                        (0, 0, inst_width, inst_height), 2, border_radius=10)
        
        font_title = pygame.font.Font(None, 26)
        font_text = pygame.font.Font(None, 22)
        
        title = font_title.render("CONTROLS", True, GREEN)
        inst_surface.blit(title, (10, 10))
        
        instructions = [
            "SPACE: Pause/Resume",
            "UP/DOWN: Change Speed",
            "CLICK: Select Planet",
            "H: Hide/Show This",
            f"Speed: {speed_multiplier}x"
        ]
        
        y = 45
        for instruction in instructions:
            text = font_text.render(instruction, True, WHITE)
            inst_surface.blit(text, (10, y))
            y += 28
        
        screen.blit(inst_surface, (10, 10))
    
    # Draw stats panel
    stats.draw(screen)
    
    # Draw info panel for selected planet
    if selected_planet:
        info_panel = InfoPanel(selected_planet)
        info_panel.draw(screen)
    
    # Update display
    pygame.display.flip()

pygame.quit()
sys.exit()