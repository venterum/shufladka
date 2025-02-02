import pygame
import sys
from game.clicker import Clicker
from game.data_manager import DataManager

class GridManager:
    def __init__(self):
        self.db = DataManager()
    
    def draw_grid(self, screen):
        if self.db.get_grid_state():
            grid = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            width, height = screen.get_size()
            for x in range(0, width, 50):
                pygame.draw.line(grid, (0, 255, 0, 64), (x, 0), (x, height))
            for y in range(0, height, 50):
                pygame.draw.line(grid, (0, 255, 0, 64), (0, y), (width, y))
            screen.blit(grid, (0, 0))

class Game:
    def __init__(self):
        pygame.init()
        self.width = 500
        self.height = 800
        # создаем окно игры
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Шуфлядка")
        
        # настройка частоты обновления
        self.clock = pygame.time.Clock()
        self.FPS = 60
        
        # инициализация основного класса
        self.clicker = Clicker()
        self.grid_manager = GridManager()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            self.clicker.handle_event(event)
        return True

    def update(self):
        self.clicker.update()

    def draw(self):
        self.clicker.draw(self.screen)
        # Отрисовка сетки поверх всего
        self.grid_manager.draw_grid(self.screen)
        pygame.display.flip()

    def run(self):
        self.screen.blit(self.clicker.loading_screen, (0, 0))
        pygame.display.flip()
        
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