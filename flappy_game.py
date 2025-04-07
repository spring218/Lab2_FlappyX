import pygame
import random
import os
from PIL import Image
import json
import neat
import pickle

# Initialize pygame
pygame.init()

# Game Configuration
class GameConfig:
    def __init__(self):
        self.SCREEN_WIDTH = 400
        self.SCREEN_HEIGHT = 600
        self.GRAVITY = 0.25
        self.FLAP_STRENGTH = -7
        self.PIPE_SPEED = 3
        self.PIPE_GAP = 150
        self.PIPE_FREQUENCY = 1500  # milliseconds
        self.BIRD_WIDTH = 34
        self.BIRD_HEIGHT = 24
        self.PLAYER_NAME = "Flappy X"  # Will be customized
        self.GAME_TITLE = "Flappy Game"
        
        # Colors
        self.COLORS = {
            'WHITE': (255, 255, 255),
            'BLACK': (0, 0, 0),
            'GREEN': (0, 255, 0),
            'BLUE': (0, 0, 255),
            'BACKGROUND': (0, 0, 255)
        }
    
    def save_config(self, filename='game_config.json'):
        with open(filename, 'w') as f:
            json.dump(self.__dict__, f, indent=4)
    
    def load_config(self, filename='game_config.json'):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                config = json.load(f)
                for key, value in config.items():
                    setattr(self, key, value)

class Bird:
    def __init__(self, x, y, config, image_path=None):
        self.x = x
        self.y = y
        self.velocity = 0
        self.config = config
        self.width = config.BIRD_WIDTH
        self.height = config.BIRD_HEIGHT
        
        if image_path and os.path.exists(image_path):
            # Load and resize the profile picture
            img = Image.open(image_path)
            img = img.resize((self.width, self.height))
            self.image = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
        else:
            # Default bird image (yellow rectangle)
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((255, 255, 0))
    
    def flap(self):
        self.velocity = self.config.FLAP_STRENGTH
    
    def update(self):
        self.velocity += self.config.GRAVITY
        self.y += self.velocity
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
    
    def get_state(self):
        return {
            'y': self.y,
            'velocity': self.velocity
        }

class Pipe:
    def __init__(self, x, config):
        self.x = x
        self.width = 60
        self.gap_y = random.randint(150, config.SCREEN_HEIGHT - 150)
        self.passed = False
        self.config = config
    
    def update(self):
        self.x -= self.config.PIPE_SPEED
    
    def draw(self, screen):
        # Draw top pipe
        pygame.draw.rect(screen, self.config.COLORS['GREEN'], 
                        (self.x, 0, self.width, self.gap_y - self.config.PIPE_GAP))
        # Draw bottom pipe
        pygame.draw.rect(screen, self.config.COLORS['GREEN'], 
                        (self.x, self.gap_y + self.config.PIPE_GAP, 
                         self.width, self.config.SCREEN_HEIGHT))
    
    def get_state(self):
        return {
            'x': self.x,
            'gap_y': self.gap_y
        }

class Game:
    def __init__(self, config=None, profile_picture=None):
        self.config = config or GameConfig()
        self.screen = pygame.display.set_mode((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        pygame.display.set_caption(self.config.GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 30)
        
        self.bird = Bird(100, self.config.SCREEN_HEIGHT // 2, self.config, profile_picture)
        self.pipes = []
        self.score = 0
        self.last_pipe = pygame.time.get_ticks()
        self.game_over = False
        self.ai_controlled = False
        self.ai_network = None
        
        # Load AI if available
        if os.path.exists('winner.pkl'):
            with open('winner.pkl', 'rb') as f:
                winner = pickle.load(f)
                config_path = os.path.join(os.path.dirname(__file__), "config-feedforward.txt")
                config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                         config_path)
                self.ai_network = neat.nn.FeedForwardNetwork.create(winner, config)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over and not self.ai_controlled:
                    self.bird.flap()
                if event.key == pygame.K_r and self.game_over:
                    self.__init__(self.config)
                if event.key == pygame.K_a:  # Toggle AI control
                    self.ai_controlled = not self.ai_controlled
            # Add mouse click support
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not self.game_over and not self.ai_controlled:  # Left click
                    self.bird.flap()
        return True
    
    def update(self):
        if not self.game_over:
            self.bird.update()
            
            # AI control
            if self.ai_controlled and self.ai_network:
                pipe_ind = 0
                if len(self.pipes) > 1 and self.bird.x > self.pipes[0].x + self.pipes[0].width:
                    pipe_ind = 1
                
                output = self.ai_network.activate((
                    self.bird.y,
                    abs(self.bird.y - self.pipes[pipe_ind].gap_y),
                    abs(self.bird.y - (self.pipes[pipe_ind].gap_y + self.config.PIPE_GAP))
                ))
                
                if output[0] > 0.5:
                    self.bird.flap()
            
            # Generate new pipes
            current_time = pygame.time.get_ticks()
            if current_time - self.last_pipe > self.config.PIPE_FREQUENCY:
                self.pipes.append(Pipe(self.config.SCREEN_WIDTH, self.config))
                self.last_pipe = current_time
            
            # Update pipes
            for pipe in self.pipes:
                pipe.update()
                
                # Check for collision
                if (self.bird.x < pipe.x + pipe.width and
                    self.bird.x + self.bird.width > pipe.x):
                    if (self.bird.y < pipe.gap_y - self.config.PIPE_GAP or
                        self.bird.y + self.bird.height > pipe.gap_y + self.config.PIPE_GAP):
                        self.game_over = True
                
                # Check if pipe is passed
                if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                    pipe.passed = True
                    self.score += 1
            
            # Remove off-screen pipes
            self.pipes = [pipe for pipe in self.pipes if pipe.x > -pipe.width]
            
            # Check for ground collision
            if self.bird.y + self.bird.height > self.config.SCREEN_HEIGHT or self.bird.y < 0:
                self.game_over = True
    
    def draw(self):
        self.screen.fill(self.config.COLORS['BACKGROUND'])
        
        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)
        
        # Draw bird
        self.bird.draw(self.screen)
        
        # Draw score
        score_text = self.font.render(f'Score: {self.score}', True, self.config.COLORS['WHITE'])
        self.screen.blit(score_text, (10, 10))
        
        # Draw AI status
        ai_text = self.font.render(f'AI: {"ON" if self.ai_controlled else "OFF"}', 
                                 True, self.config.COLORS['WHITE'])
        self.screen.blit(ai_text, (10, 50))
        
        if self.game_over:
            game_over_text = self.font.render('Game Over! Press R to restart', 
                                            True, self.config.COLORS['WHITE'])
            self.screen.blit(game_over_text, 
                           (self.config.SCREEN_WIDTH//2 - 150, 
                            self.config.SCREEN_HEIGHT//2))
        
        pygame.display.flip()
    
    def get_game_state(self):
        """Return the current game state for AI processing"""
        return {
            'bird': self.bird.get_state(),
            'pipes': [pipe.get_state() for pipe in self.pipes],
            'score': self.score,
            'game_over': self.game_over
        }
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    # Create and load configuration
    config = GameConfig()
    config.load_config()
    
    # Update game title with player name
    config.GAME_TITLE = f"Flappy {config.PLAYER_NAME}"
    
    # Replace 'profile_picture.jpg' with your actual profile picture path
    game = Game(config, profile_picture='profile_picture.jpg')
    game.run() 