import pygame
from pathlib import Path

class DebugConsole:
    def __init__(self, db):
        self.db = db
        self.enabled = db.console_enabled  # Берем состояние из сохранения
        self.visible = False
        self.text = ""
        
        # Загружаем шрифт для консоли
        fonts_path = Path("assets") / "fonts"
        self.font = pygame.font.Font(fonts_path / "Tiny5-Regular.ttf", 24)
        
        # Создаем фон консоли
        self.console_bg = pygame.Surface((500, 40))
        self.console_bg.fill((0, 0, 0))
        self.console_bg.set_alpha(180)
    
    def toggle(self):
        if self.enabled:
            self.visible = not self.visible
            self.text = ""
    
    def handle_input(self, event):
        if not self.visible:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                command_executed = self.execute_command(self.text)
                self.text = ""
                self.visible = False
                return command_executed
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
        return False

    def execute_command(self, command):
        if command.upper() == "GRID":
            self.db.toggle_grid()
            return True
        return False

    def draw(self, screen):
        if self.visible:
            screen.blit(self.console_bg, (0, 0))
            text = self.font.render(f"~ {self.text}", True, (0, 255, 0))
            screen.blit(text, (10, 10))


class DebugGrid:
    def __init__(self, db):
        self.db = db
        self.font = pygame.font.Font(None, 20)
        
    def draw(self, screen, mouse_pos):
        if self.db.get_grid_state():
            # Рисуем сетку
            grid = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            width, height = screen.get_size()
            for x in range(0, width, 50):
                pygame.draw.line(grid, (0, 255, 0, 64), (x, 0), (x, height))
            for y in range(0, height, 50):
                pygame.draw.line(grid, (0, 255, 0, 64), (0, y), (width, y))
            screen.blit(grid, (0, 0))
            
            # Отображаем координаты мыши с номерами ячеек
            cell_x = mouse_pos[0] // 50
            cell_y = mouse_pos[1] // 50
            coords_text = f"X: {mouse_pos[0]} ({cell_x}), Y: {mouse_pos[1]} ({cell_y})"
            text_surface = self.font.render(coords_text, True, (0, 255, 0))
            screen.blit(text_surface, (width - 200, 10)) 