import pygame
import sys
from game.clicker import Clicker

class Game:
    def __init__(self):
        pygame.init()
        self.width = 400
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Шуфлядка")
        
        self.clock = pygame.time.Clock()
        self.FPS = 60
        
        self.clicker = Clicker()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            self.clicker.handle_event(event)
        return True

    def update(self):
        self.clicker.update()

    def draw(self):
        self.screen.fill((245, 245, 245))
        self.clicker.draw(self.screen)
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 