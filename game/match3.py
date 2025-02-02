import pygame
import random
import sys
from pathlib import Path
from game.debug_tools import DebugConsole, DebugGrid

class Match3Game:
    def __init__(self, return_callback):
        self.return_callback = return_callback
        pygame.init()
        self.WIDTH = 500
        self.HEIGHT = 800
        self.GRID_SIZE = 8
        self.TILE_SIZE = self.WIDTH // self.GRID_SIZE
        self.FPS = 30
        
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Кот-в-ряд")
        self.clock = pygame.time.Clock()
        
        # Загружаем фон из сохранения
        from game.data_manager import DataManager
        self.db = DataManager()
        game_state = self.db.load_game_state()
        self.background_image = pygame.image.load(game_state[4])
        self.background_image = pygame.transform.scale(self.background_image, (self.WIDTH, self.HEIGHT))
        
        # шрифт
        fonts_path = Path("assets") / "fonts"
        self.font = pygame.font.Font(fonts_path / "Tiny5-Regular.ttf", 32)
        self.small_font = pygame.font.Font(fonts_path / "Tiny5-Regular.ttf", 24)
        
        self.image_paths = [
            'assets/sprites/match3/cat1.png',
            'assets/sprites/match3/cat2.png',
            'assets/sprites/match3/cat3.png',
            'assets/sprites/match3/cat4.png'
        ]
        self.IMAGES = self.load_and_scale_images()
        
        self.match_animations = []  # для анимации исчезновения совпадений
        self.selected_scale = 1.0  # для анимации выбранного котика
        
        # Настройки уровней
        self.levels = [
            {"target": 30, "moves": 20, "name": "Котёнок"},
            {"target": 50, "moves": 18, "name": "Кот"},
            {"target": 70, "moves": 16, "name": "Пушистик"},
            {"target": 90, "moves": 15, "name": "Мурзик"},
            {"target": 120, "moves": 14, "name": "Тигр"},
            {"target": 150, "moves": 12, "name": "Лев"}
        ]
        self.current_level = 0

        # Загружаем прогресс уровней
        self.unlocked_levels = self.db.load_match3_progress()
        if self.unlocked_levels is None:
            self.unlocked_levels = 1  # если первый запуск, открыт только первый уровень
            self.db.save_match3_progress(1)

        self.debug_console = DebugConsole(self.db)
        self.debug_grid = DebugGrid(self.db)

    def load_and_scale_images(self):
        images = []
        for path in self.image_paths:
            image = pygame.image.load(path)
            image = pygame.transform.scale(image, (self.TILE_SIZE, self.TILE_SIZE))
            images.append(image)
        return images

    def create_grid(self):
        grid = [[random.choice(self.IMAGES) for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        while self.check_matches(grid):
            grid = [[random.choice(self.IMAGES) for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        return grid

    def draw_grid(self, grid):
        # Отступ сверху для центрирования сетки
        top_margin = (self.HEIGHT - self.GRID_SIZE * self.TILE_SIZE) // 2
        
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                pygame.draw.rect(self.screen, (0, 0, 0), 
                               (x * self.TILE_SIZE, y * self.TILE_SIZE + top_margin, 
                                self.TILE_SIZE, self.TILE_SIZE), 2)
                image = grid[y][x]
                if image is not None:
                    self.screen.blit(image, (x * self.TILE_SIZE, y * self.TILE_SIZE + top_margin))

        # Отрисовка сетки если включена
        if self.db.get_grid_state():
            self.draw_debug_grid()

    def draw_debug_grid(self):
        grid = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        for x in range(0, self.WIDTH, 50):
            pygame.draw.line(grid, (0, 255, 0, 64), (x, 0), (x, self.HEIGHT))
        for y in range(0, self.HEIGHT, 50):
            pygame.draw.line(grid, (0, 255, 0, 64), (0, y), (self.WIDTH, y))
        self.screen.blit(grid, (0, 0))

    def check_matches(self, grid):
        matches = []
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE - 2):
                if grid[y][x] == grid[y][x + 1] == grid[y][x + 2] and grid[y][x] is not None:
                    matches.append((y, x))
                    matches.append((y, x + 1))
                    matches.append((y, x + 2))
        for x in range(self.GRID_SIZE):
            for y in range(self.GRID_SIZE - 2):
                if grid[y][x] == grid[y + 1][x] == grid[y + 2][x] and grid[y][x] is not None:
                    matches.append((y, x))
                    matches.append((y + 1, x))
                    matches.append((y + 2, x))
        return set(matches)

    def remove_matches(self, grid):
        collected_kittens = 0
        top_margin = (self.HEIGHT - self.GRID_SIZE * self.TILE_SIZE) // 2  # Определяем в начале метода
        
        while True:
            matches = self.check_matches(grid)
            if not matches:
                break
            
            # Анимация исчезновения совпадений
            self.match_animations = list(matches)
            
            # Анимация увеличения и исчезновения
            for scale in range(10, -1, -1):  # от 10 до 0
                self.screen.blit(self.background_image, (0, 0))
                
                # Отрисовка обычных котиков
                for y in range(self.GRID_SIZE):
                    for x in range(self.GRID_SIZE):
                        if (y, x) not in matches:
                            pygame.draw.rect(self.screen, (0, 0, 0), 
                                           (x * self.TILE_SIZE, y * self.TILE_SIZE + top_margin, 
                                            self.TILE_SIZE, self.TILE_SIZE), 2)
                            if grid[y][x] is not None:
                                self.screen.blit(grid[y][x], 
                                               (x * self.TILE_SIZE, y * self.TILE_SIZE + top_margin))
                
                # Отрисовка исчезающих котиков
                for y, x in matches:
                    if grid[y][x] is not None:
                        # Увеличиваем размер и уменьшаем прозрачность
                        scale_factor = 1 + (10 - scale) * 0.1  # от 1.0 до 2.0
                        alpha = int(255 * scale / 10)  # от 255 до 0
                        
                        scaled_size = int(self.TILE_SIZE * scale_factor)
                        scaled_img = pygame.transform.scale(grid[y][x], (scaled_size, scaled_size))
                        scaled_img.set_alpha(alpha)
                        
                        # Центрируем увеличенное изображение
                        pos_x = x * self.TILE_SIZE + (self.TILE_SIZE - scaled_size) // 2
                        pos_y = y * self.TILE_SIZE + top_margin + (self.TILE_SIZE - scaled_size) // 2
                        
                        self.screen.blit(scaled_img, (pos_x, pos_y))
                
                pygame.display.flip()
                pygame.time.wait(30)
            
            for y, x in matches:
                collected_kittens += 1
                grid[y][x] = None

            falling = True
            while falling:
                falling = False
                self.screen.blit(self.background_image, (0, 0))
                
                for x in range(self.GRID_SIZE):
                    for y in range(self.GRID_SIZE-1, -1, -1):
                        if grid[y][x] is None:
                            for above in range(y-1, -1, -1):
                                if grid[above][x] is not None:
                                    grid[y][x] = grid[above][x]
                                    grid[above][x] = None
                                    falling = True
                                    break
                
                for y in range(self.GRID_SIZE):
                    for x in range(self.GRID_SIZE):
                        if grid[y][x] is not None:
                            pygame.draw.rect(self.screen, (0, 0, 0), 
                                           (x * self.TILE_SIZE, y * self.TILE_SIZE + top_margin, 
                                            self.TILE_SIZE, self.TILE_SIZE), 2)
                            self.screen.blit(grid[y][x], 
                                           (x * self.TILE_SIZE, y * self.TILE_SIZE + top_margin))
                
                pygame.display.flip()
                pygame.time.wait(50)
            
            for x in range(self.GRID_SIZE):
                for y in range(self.GRID_SIZE):
                    if grid[y][x] is None:
                        grid[y][x] = random.choice(self.IMAGES)
                        # Анимация появления нового котика
                        for scale in range(5):
                            self.screen.blit(self.background_image, (0, 0))
                            self.draw_grid(grid)
                            scaled = pygame.transform.scale(
                                grid[y][x],
                                (int(self.TILE_SIZE * scale/4), int(self.TILE_SIZE * scale/4))
                            )
                            scaled_rect = scaled.get_rect(
                                center=(x * self.TILE_SIZE + self.TILE_SIZE//2,
                                      y * self.TILE_SIZE + self.TILE_SIZE//2 + top_margin)
                            )
                            self.screen.blit(scaled, scaled_rect)
                            pygame.display.flip()
                            pygame.time.wait(30)
                
        return collected_kittens

    def display_game_over_screen(self, result):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)
        self.screen.blit(overlay, (0, 0))
        title_y = self.HEIGHT // 2 - 120
        reward_y = self.HEIGHT // 2 - 60
        buttons_start_y = self.HEIGHT // 2

        message = "Уровень пройден!" if result == "win" else "Поражение!"
        text_surface = self.font.render(message, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.WIDTH // 2, title_y))
        self.screen.blit(text_surface, text_rect)

        if result == "win":
            # Начисляем награду
            reward = random.randint(10, 50)
            reward_text = self.font.render(f"Награда: {reward} монет!", True, (255, 255, 0))
            reward_rect = reward_text.get_rect(center=(self.WIDTH // 2, reward_y))
            self.screen.blit(reward_text, reward_rect)
            
            # Обновляем прогресс и монеты
            if self.current_level + 1 > self.unlocked_levels:
                self.unlocked_levels = self.current_level + 1
                self.db.save_match3_progress(self.unlocked_levels)
            
            # Получаем текущее состояние и обновляем только монеты
            game_state = self.db.load_game_state()
            new_coins = game_state[1] + reward
            self.db.save_game_state(
                clicks=game_state[0],
                coins=new_coins,
                multiplier=game_state[2]
            )
            # Возвращаем новое количество монет в callback
            return_data = {"coins": new_coins}
            self.return_callback(return_data)

        # Кнопки
        button_width = 200
        button_height = 50
        spacing = 20

        # Позиционируем кнопки
        if result == "win" and self.current_level < len(self.levels) - 1:
            next_btn = pygame.Rect(self.WIDTH//2 - button_width//2, 
                                 buttons_start_y,
                                 button_width, button_height)
            pygame.draw.rect(self.screen, (50, 200, 50), next_btn)
            next_text = self.font.render("Следующий", True, (255, 255, 255))
            next_rect = next_text.get_rect(center=next_btn.center)
            self.screen.blit(next_text, next_rect)
            buttons_start_y += button_height + spacing

        retry_btn = pygame.Rect(self.WIDTH//2 - button_width//2,
                              buttons_start_y,
                              button_width, button_height)
        pygame.draw.rect(self.screen, (200, 150, 50), retry_btn)
        retry_text = self.font.render("Повторить", True, (255, 255, 255))
        retry_rect = retry_text.get_rect(center=retry_btn.center)
        self.screen.blit(retry_text, retry_rect)
        buttons_start_y += button_height + spacing

        exit_btn = pygame.Rect(self.WIDTH//2 - button_width//2,
                             buttons_start_y,
                             button_width, button_height)
        pygame.draw.rect(self.screen, (200, 50, 50), exit_btn)
        exit_text = self.font.render("Выход", True, (255, 255, 255))
        exit_rect = exit_text.get_rect(center=exit_btn.center)
        self.screen.blit(exit_text, exit_rect)

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if exit_btn.collidepoint(event.pos):
                        return "exit"
                    if retry_btn.collidepoint(event.pos):
                        return "retry"
                    if result == "win" and self.current_level < len(self.levels) - 1:
                        if next_btn.collidepoint(event.pos):
                            self.current_level += 1
                            return "next"

    def draw_level_selection(self):
        self.screen.blit(self.background_image, (0, 0))
        
        title = self.font.render("Выберите уровень", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.WIDTH//2, 50))
        self.screen.blit(title, title_rect)

        button_width = 400
        button_height = 70
        spacing = 20
        start_y = 120

        buttons = []
        for i, level in enumerate(self.levels):
            btn = pygame.Rect(self.WIDTH//2 - button_width//2,
                            start_y + i*(button_height + spacing),
                            button_width, button_height)
            
            # Определяем цвет кнопки в зависимости от доступности уровня
            if i < self.unlocked_levels:
                pygame.draw.rect(self.screen, (60, 60, 80), btn, border_radius=15)
                pygame.draw.rect(self.screen, (80, 80, 100), btn, 2, border_radius=15)
                text_color = (255, 255, 255)
                desc_color = (200, 200, 200)
            else:
                pygame.draw.rect(self.screen, (40, 40, 40), btn, border_radius=15)
                pygame.draw.rect(self.screen, (60, 60, 60), btn, 2, border_radius=15)
                text_color = (100, 100, 100)
                desc_color = (80, 80, 80)
            
            name_text = self.small_font.render(f"Уровень {i+1}: {level['name']}", True, text_color)
            desc_text = self.small_font.render(f"{level['target']} котят за {level['moves']} ходов", 
                                       True, desc_color)
            
            name_rect = name_text.get_rect(center=(btn.centerx, btn.top + button_height//3))
            desc_rect = desc_text.get_rect(center=(btn.centerx, btn.bottom - button_height//3))
            
            self.screen.blit(name_text, name_rect)
            self.screen.blit(desc_text, desc_rect)
            buttons.append(btn)

        # Кнопка выхода
        exit_btn = pygame.Rect(self.WIDTH//2 - 100, self.HEIGHT - 80, 200, 50)
        pygame.draw.rect(self.screen, (200, 50, 50), exit_btn, border_radius=10)
        exit_text = self.font.render("Выход", True, (255, 255, 255))
        exit_rect = exit_text.get_rect(center=exit_btn.center)
        self.screen.blit(exit_text, exit_rect)

        pygame.display.flip()
        return buttons, exit_btn

    def level_selection(self):
        buttons, exit_btn = self.draw_level_selection()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.return_callback()
                    return False
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if exit_btn.collidepoint(event.pos):
                        self.return_callback()
                        return False
                        
                    for i, btn in enumerate(buttons):
                        if btn.collidepoint(event.pos) and i < self.unlocked_levels:
                            self.current_level = i
                            return True
            
            self.clock.tick(self.FPS)

    def play_level(self):
        level = self.levels[self.current_level]
        grid = self.create_grid()
        self.grid = grid
        selected_tile = None
        collected_kittens = 0
        attempts_left = level["moves"]
        result = None  # инициализируем переменную result

        # Создаем кнопку выхода
        exit_btn = pygame.Rect(self.WIDTH - 120, 10, 100, 40)

        # Создаем полупрозрачную панель для статистики
        stats_panel = pygame.Surface((self.WIDTH, 100), pygame.SRCALPHA)
        pygame.draw.rect(stats_panel, (30, 30, 30, 180), stats_panel.get_rect())

        def animate_swap(start_pos, end_pos, grid, start_tile, end_tile):
            steps = 10  # количество кадров анимации
            top_margin = (self.HEIGHT - self.GRID_SIZE * self.TILE_SIZE) // 2
            start_x = start_pos[1] * self.TILE_SIZE
            start_y = start_pos[0] * self.TILE_SIZE + top_margin
            end_x = end_pos[1] * self.TILE_SIZE
            end_y = end_pos[0] * self.TILE_SIZE + top_margin
            
            for step in range(steps + 1):
                progress = step / steps  # от 0 до 1
                
                # Позиции для текущего кадра
                current_x1 = start_x + (end_x - start_x) * progress
                current_y1 = start_y + (end_y - start_y) * progress
                current_x2 = end_x + (start_x - end_x) * progress
                current_y2 = end_y + (start_y - end_y) * progress
                
                # Отрисовка кадра
                self.screen.blit(self.background_image, (0, 0))
                
                # Отрисовка сетки без перемещаемых спрайтов
                for y in range(self.GRID_SIZE):
                    for x in range(self.GRID_SIZE):
                        if (y, x) != start_pos and (y, x) != end_pos:
                            pygame.draw.rect(self.screen, (0, 0, 0), 
                                           (x * self.TILE_SIZE, y * self.TILE_SIZE + top_margin, 
                                            self.TILE_SIZE, self.TILE_SIZE), 2)
                            if grid[y][x] is not None:
                                self.screen.blit(grid[y][x], 
                                               (x * self.TILE_SIZE, y * self.TILE_SIZE + top_margin))
                
                # Отрисовка перемещаемых спрайтов
                pygame.draw.rect(self.screen, (0, 0, 0), 
                               (current_x1, current_y1, self.TILE_SIZE, self.TILE_SIZE), 2)
                pygame.draw.rect(self.screen, (0, 0, 0), 
                               (current_x2, current_y2, self.TILE_SIZE, self.TILE_SIZE), 2)
                
                self.screen.blit(start_tile, (current_x1, current_y1))
                self.screen.blit(end_tile, (current_x2, current_y2))
                
                # Отрисовка интерфейса
                self.screen.blit(stats_panel, (0, 0))
                self.screen.blit(text_surface, (20, 15))
                self.screen.blit(stats_surface, (20, 55))
                pygame.draw.rect(self.screen, (200, 50, 50), exit_btn, border_radius=10)
                self.screen.blit(exit_text, exit_rect)
                
                pygame.display.flip()
                pygame.time.wait(20)  # задержка между кадрами

        running = True
        while running:
            self.screen.blit(self.background_image, (0, 0))
            self.draw_grid(grid)
            
            # Отрисовка верхней панели со статистикой
            self.screen.blit(stats_panel, (0, 0))

            # Отображение статистики
            info_text = f"Уровень {self.current_level + 1}: {level['name']}"
            stats_text = f"Котята: {collected_kittens}/{level['target']} | Ходы: {attempts_left}"
            
            text_surface = self.font.render(info_text, True, (255, 255, 255))
            stats_surface = self.font.render(stats_text, True, (255, 255, 255))
            
            self.screen.blit(text_surface, (20, 15))
            self.screen.blit(stats_surface, (20, 55))

            # Отрисовка кнопки выхода
            pygame.draw.rect(self.screen, (200, 50, 50), exit_btn, border_radius=10)
            exit_text = self.font.render("Выход", True, (255, 255, 255))
            exit_rect = exit_text.get_rect(center=exit_btn.center)
            self.screen.blit(exit_text, exit_rect)

            # Отрисовка отладочной информации
            if self.db.get_grid_state():
                mouse_pos = pygame.mouse.get_pos()
                self.debug_grid.draw(self.screen, mouse_pos)
            self.debug_console.draw(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if exit_btn.collidepoint(event.pos):
                            self.return_callback()
                            return
                        
                    x, y = event.pos
                    top_margin = (self.HEIGHT - self.GRID_SIZE * self.TILE_SIZE) // 2
                    adjusted_y = y - top_margin
                    col = x // self.TILE_SIZE
                    row = adjusted_y // self.TILE_SIZE
                    if 0 <= row < self.GRID_SIZE and 0 <= col < self.GRID_SIZE:
                        selected_tile = (row, col)

                if event.type == pygame.MOUSEBUTTONUP and selected_tile is not None:
                    x, y = event.pos
                    top_margin = (self.HEIGHT - self.GRID_SIZE * self.TILE_SIZE) // 2
                    adjusted_y = y - top_margin
                    drop_col = x // self.TILE_SIZE
                    drop_row = adjusted_y // self.TILE_SIZE
                    
                    if 0 <= drop_row < self.GRID_SIZE and 0 <= drop_col < self.GRID_SIZE:
                        if (abs(selected_tile[0] - drop_row) == 1 and selected_tile[1] == drop_col) or \
                           (abs(selected_tile[1] - drop_col) == 1 and selected_tile[0] == drop_row):
                            
                            # Сохраняем спрайты для анимации
                            start_tile = grid[selected_tile[0]][selected_tile[1]]
                            end_tile = grid[drop_row][drop_col]
                            
                            # Анимируем перемещение
                            animate_swap(selected_tile, (drop_row, drop_col), grid, start_tile, end_tile)
                            
                            # Меняем местами котиков в сетке
                            grid[selected_tile[0]][selected_tile[1]], grid[drop_row][drop_col] = \
                            grid[drop_row][drop_col], grid[selected_tile[0]][selected_tile[1]]

                            if self.check_matches(grid):
                                collected_kittens += self.remove_matches(grid)
                                attempts_left -= 1

                                if collected_kittens >= level["target"]:
                                    result = self.display_game_over_screen("win")
                                    if result == "exit":
                                        self.return_callback()
                                        return
                                    elif result == "next":
                                        self.current_level += 1
                                        return self.play_level()
                                elif result == "retry":
                                    return self.play_level()
                            else:
                                # Возвращаем обратно если нет совпадений
                                grid[selected_tile[0]][selected_tile[1]], grid[drop_row][drop_col] = \
                                grid[drop_row][drop_col], grid[selected_tile[0]][selected_tile[1]]
                                attempts_left -= 1

                            if attempts_left <= 0:
                                result = self.display_game_over_screen("lose")
                                if result == "exit":
                                    self.return_callback()
                                    return
                                elif result == "retry":
                                    return self.play_level()
                    selected_tile = None

            # Подсветка выбранной ячейки
            if selected_tile is not None:
                x = selected_tile[1] * self.TILE_SIZE
                y = selected_tile[0] * self.TILE_SIZE + top_margin
                pygame.draw.rect(self.screen, (255, 255, 0), 
                               (x, y, self.TILE_SIZE, self.TILE_SIZE), 3)

            pygame.display.flip()
            self.clock.tick(self.FPS)

        self.return_callback()

    def run(self):
        if self.level_selection():
            self.play_level()

    def add_plus_animation(self, x, y, value):
        self.plus_animations.append({
            'x': x,
            'y': y,
            'alpha': 255,
            'value': value,
            'speed': 1
        })

    def add_scale_animation(self, row, col):
        self.scale_animations[(row, col)] = {
            'scale': 0.8,
            'growing': True
        }

    def update_animations(self):
        pass  # Больше не нужен, так как анимации обрабатываются в remove_matches

    def draw_animations(self, top_margin):
        pass  # Больше не нужен, так как анимации обрабатываются в remove_matches 

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Обработка консоли
            if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKQUOTE:
                self.debug_console.toggle()
            if self.debug_console.handle_input(event):
                continue
            
            # Остальная обработка событий
            
    def draw(self):
        # ... существующий код ...
        
        # Отрисовка отладочной информации
        mouse_pos = pygame.mouse.get_pos()
        self.debug_grid.draw(self.screen, mouse_pos)
        self.debug_console.draw(self.screen) 