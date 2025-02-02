import pygame
import random
import time
from pathlib import Path
from game.debug_tools import DebugConsole, DebugGrid

class RoadGame:
    def __init__(self, return_callback):
        self.return_callback = return_callback
        pygame.init()
        self.WIDTH = 500
        self.HEIGHT = 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Кот переходит дорогу")
        
        # Загружаем фон из сохранения
        from game.data_manager import DataManager
        self.db = DataManager()
        game_state = self.db.load_game_state()
        
        # Загружаем спрайты
        sprites_path = Path("assets") / "sprites"
        road_path = sprites_path / "road"
        fonts_path = Path("assets") / "fonts"
        
        self.road_image = pygame.image.load(road_path / "fon_road.jpeg")
        self.road_image = pygame.transform.scale(self.road_image, (self.WIDTH, self.HEIGHT))
        
        # Используем активный скин кота или стандартный для игры
        try:
            self.cat_image = pygame.image.load(game_state[3])
        except:
            self.cat_image = pygame.image.load(road_path / "black_cat.png")
        self.cat_image = pygame.transform.scale(self.cat_image, (50, 50))
        
        # Загружаем спрайты машин с увеличенным размером
        self.car_slow = pygame.image.load(road_path / "yellow_car.png")
        self.car_fast = pygame.image.load(road_path / "red_car.png")
        self.car_slow = pygame.transform.scale(self.car_slow, (90, 90))  # Увеличено с 70 до 90
        self.car_fast = pygame.transform.scale(self.car_fast, (90, 90))  # Увеличено с 70 до 90
        
        self.coin_image = pygame.image.load(sprites_path / "coin.png")
        self.coin_image = pygame.transform.scale(self.coin_image, (50, 50))
        
        # Загружаем шрифт
        self.font = pygame.font.Font(fonts_path / "Tiny5-Regular.ttf", 32)
        
        # Статистика
        self.coins_collected = 0
        self.start_time = time.time()
        self.end_time = None  # добавляем время окончания игры
        self.high_score_time = 0
        self.game_over = False
        self.last_coin_spawn = time.time()
        
        # Настройки дороги
        self.START_Y = 500   # высота появления машин
        self.END_Y = 700    # высота исчезновения машин
        
        # Размеры кота и его позиционирование
        self.CAT_SIZE = 50  # размер кота
        self.cat_image = pygame.transform.scale(self.cat_image, (self.CAT_SIZE, self.CAT_SIZE))
        
        # Позиции полос (конечные точки)
        self.lane_positions = [70, 190, 310, 420]  # позиции для машин
        self.cat_positions = [140, 210, 290, 350]  # позиции для кота
        self.lanes_count = len(self.lane_positions)
        self.cat_lane_index = 2  # начинаем с предпоследней полосы
        
        # Начальная позиция кота
        self.cat_x = self.cat_positions[self.cat_lane_index] - self.CAT_SIZE // 2  # центрируем кота
        self.cat_y = self.END_Y - 70  # чуть выше конца дороги
        self.target_cat_x = self.cat_x
        
        # Настройки скорости
        self.initial_slow_speed = 1.5  # начальная медленная скорость
        self.initial_fast_speed = 2.5  # начальная быстрая скорость
        self.speed_increment = 0.2     # прирост скорости
        self.speed_increase_interval = 10  # интервал увеличения скорости (секунды)
        self.max_speed = 8.0          # максимальная скорость
        
        # Настройки спавна
        self.coin_spawn_interval = 4.0  # интервал появления монеток (секунды)
        self.max_cars = 2              # максимум машин на экране
        self.car_spawn_delay = 2       # задержка между появлением машин
        
        self.cars = []
        self.coins = []
        self.last_speed_increase = time.time()
        self.last_car_spawn = [0, 0, 0, 0]
        
        # Кнопка рестарта
        self.button_width = 200
        self.button_height = 50
        self.button_x = (self.WIDTH - self.button_width) // 2
        self.button_y = self.HEIGHT // 2 + 90
        self.button_rect = pygame.Rect(self.button_x, self.button_y, self.button_width, self.button_height)
        
        # Кнопка выхода
        self.exit_btn = pygame.Rect(380, 20, 100, 40)
        
        self.debug_console = DebugConsole(self.db)
        self.debug_grid = DebugGrid(self.db)

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.show_game_over()  # Сохраняем награду при закрытии окна
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_over:
                        # Проверяем нажатие на кнопки в game over экране
                        if self.button_rect.collidepoint(event.pos):
                            self.reset_game()
                        # Проверяем нажатие на кнопку выхода
                        exit_btn = pygame.Rect(
                            self.button_x,
                            self.button_y + self.button_height + 20,
                            self.button_width,
                            self.button_height
                        )
                        if exit_btn.collidepoint(event.pos):
                            self.show_game_over()  # Сохраняем награду перед выходом
                            return
                    elif self.exit_btn.collidepoint(event.pos):
                        self.game_over = True  # Помечаем игру как оконченную
                        self.end_time = time.time()  # Фиксируем время окончания
                        self.show_game_over()  # Сохраняем награду перед выходом
                        return
                elif event.type == pygame.KEYDOWN and not self.game_over:
                    if event.key == pygame.K_RIGHT and self.cat_lane_index < self.lanes_count - 1:
                        self.cat_lane_index += 1
                        self.target_cat_x = self.cat_positions[self.cat_lane_index] - self.CAT_SIZE // 2  # центрируем кота
                    elif event.key == pygame.K_LEFT and self.cat_lane_index > 0:
                        self.cat_lane_index -= 1
                        self.target_cat_x = self.cat_positions[self.cat_lane_index] - self.CAT_SIZE // 2  # центрируем кота

            if not self.game_over:
                self.update()
            self.draw()
            clock.tick(60)

    def update(self):
        if not self.game_over:
            current_time = time.time()
            elapsed_time = current_time - self.start_time

            # Плавное перемещение кота
            if self.cat_x != self.target_cat_x:
                dx = (self.target_cat_x - self.cat_x) / 4  # увеличена скорость перемещения
                self.cat_x += dx

            # Увеличение скорости со временем
            if current_time - self.last_speed_increase >= self.speed_increase_interval:
                if self.initial_slow_speed < self.max_speed:
                    self.initial_slow_speed += self.speed_increment
                    self.initial_fast_speed += self.speed_increment
                self.last_speed_increase = current_time

            # Спавн машин
            if len(self.cars) < self.max_cars:
                for lane in range(self.lanes_count):
                    if current_time - self.last_car_spawn[lane] > self.car_spawn_delay:
                        if random.randint(0, 100) < 25:  # увеличена вероятность спавна
                            if self.can_spawn_car(lane):
                                self.generate_car(lane)
                                self.last_car_spawn[lane] = current_time
                                break

            # Обновление машин
            for car in self.cars[:]:
                car.move()
                if car.y > car.end_y:  # Используем индивидуальную точку исчезновения
                    self.cars.remove(car)
                
                # Проверяем столкновения только если машина не проехала линию кота
                if car.y <= self.cat_y:
                    cat_rect = pygame.Rect(
                        self.cat_x + self.CAT_SIZE // 4,
                        self.cat_y + self.CAT_SIZE // 4,
                        self.CAT_SIZE // 2,
                        self.CAT_SIZE // 2
                    )
                    car_rect = car.rect.inflate(-20, -20)
                    if cat_rect.colliderect(car_rect):
                        self.game_over = True
                        self.end_time = time.time()
                        if elapsed_time > self.high_score_time:
                            self.high_score_time = elapsed_time

            # Спавн монеток чаще
            if current_time - self.last_coin_spawn >= self.coin_spawn_interval:
                self.last_coin_spawn = current_time
                lane = random.randint(0, self.lanes_count - 1)
                target_x = self.lane_positions[lane]
                start_x = self.cat_positions[lane]
                self.coins.append(Bag(start_x, self.coin_image))

            for coin in self.coins[:]:
                coin.move()
                cat_rect = pygame.Rect(
                    self.cat_x + self.CAT_SIZE // 4,  # уменьшаем область коллизии
                    self.cat_y + self.CAT_SIZE // 4,
                    self.CAT_SIZE // 2,
                    self.CAT_SIZE // 2
                )
                if cat_rect.colliderect(coin.rect) and not coin.collected:
                    coin.collected = True
                    self.coins_collected += coin.value
                if coin.y > self.HEIGHT:
                    self.coins.remove(coin)

    def draw(self):
        self.screen.blit(self.road_image, (0, 0))
        
        # Отрисовка машин и монет
        for car in self.cars:
            car.draw(self.screen)
        for coin in self.coins:
            coin.draw(self.screen)
        
        # Отрисовка кота
        self.screen.blit(self.cat_image, (self.cat_x, self.cat_y))
        
        # Отрисовка статистики
        if not self.game_over:
            elapsed_time = int(time.time() - self.start_time)
        else:
            elapsed_time = int(self.end_time - self.start_time)
        time_text = self.font.render(f"Время: {elapsed_time}", True, (255, 255, 255))
        coins_text = self.font.render(f"Монеты: {self.coins_collected}", True, (255, 255, 0))
        self.screen.blit(time_text, (10, 10))
        self.screen.blit(coins_text, (10, 50))
        
        # Кнопка выхода
        pygame.draw.rect(self.screen, (200, 50, 50), self.exit_btn, border_radius=10)
        exit_text = self.font.render("Выход", True, (255, 255, 255))
        exit_rect = exit_text.get_rect(center=self.exit_btn.center)
        self.screen.blit(exit_text, exit_rect)
        
        if self.game_over:
            self.draw_game_over()

        # Отрисовка сетки если включена (перемещено в конец, чтобы отрисовывалось поверх всего)
        if self.db.get_grid_state():
            self.draw_grid()

        # Отрисовка отладочной информации
        if self.db.get_grid_state():
            mouse_pos = pygame.mouse.get_pos()
            self.debug_grid.draw(self.screen, mouse_pos)
        self.debug_console.draw(self.screen)

        pygame.display.flip()

    def draw_game_over(self):
        # затемнение экрана
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(160)
        self.screen.blit(overlay, (0, 0))
        
        # вычисляем награду на основе времени и собранных монет
        base_reward = self.coins_collected * 5
        time_bonus = int((self.end_time - self.start_time) / 10)  # 1 монета за каждые 10 секунд
        total_reward = base_reward + time_bonus
        
        # отрисовка текста
        game_over_text = self.font.render("Игра окончена!", True, (255, 0, 0))
        score_text = self.font.render(f"Собрано монет: {self.coins_collected}", True, (255, 255, 255))
        time_text = self.font.render(f"Время: {int(self.end_time - self.start_time)} сек", True, (255, 255, 255))
        best_time_text = self.font.render(f"Рекорд: {int(self.high_score_time)} сек", True, (255, 255, 0))
        reward_text = self.font.render(f"Награда: {total_reward} монет!", True, (255, 255, 0))
        
        texts = [game_over_text, best_time_text, score_text, time_text, reward_text]
        for i, text in enumerate(texts):
            text_rect = text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 - 100 + i*40))
            self.screen.blit(text, text_rect)
        
        # кнопки
        pygame.draw.rect(self.screen, (0, 200, 0), self.button_rect, border_radius=10)
        restart_text = self.font.render("Рестарт", True, (0, 0, 0))
        restart_rect = restart_text.get_rect(center=self.button_rect.center)
        self.screen.blit(restart_text, restart_rect)
        
        exit_btn = pygame.Rect(
            self.button_x,
            self.button_y + self.button_height + 20,
            self.button_width,
            self.button_height
        )
        pygame.draw.rect(self.screen, (200, 50, 50), exit_btn, border_radius=10)
        exit_text = self.font.render("Выход", True, (255, 255, 255))
        exit_rect = exit_text.get_rect(center=exit_btn.center)
        self.screen.blit(exit_text, exit_rect)

    def show_game_over(self):
        if not self.end_time:  # Если время окончания не установлено
            self.end_time = time.time()  # устанавливаем его
        
        # вычисляем награду
        base_reward = self.coins_collected * 5
        time_bonus = int((self.end_time - self.start_time) / 10)
        total_reward = base_reward + time_bonus
        
        # обновляем монеты в основной игре
        game_state = self.db.load_game_state()
        new_coins = game_state[1] + total_reward
        self.db.save_game_state(
            clicks=game_state[0],
            coins=new_coins,
            multiplier=game_state[2]
        )
        
        # возвращаем новое количество монет в callback
        return_data = {"coins": new_coins}
        self.return_callback(return_data)
        return "exit"

    def reset_game(self):
        self.cat_lane_index = 2
        self.cat_x = self.cat_positions[self.cat_lane_index] - self.CAT_SIZE // 2  # центрируем кота
        self.target_cat_x = self.cat_x
        self.cars.clear()
        self.coins.clear()
        self.start_time = time.time()
        self.last_coin_spawn = time.time()
        self.coins_collected = 0
        self.last_car_spawn = [0, 0, 0, 0]
        self.game_over = False
        self.initial_slow_speed = 1.5
        self.initial_fast_speed = 2.5

    def can_spawn_car(self, lane):
        # Проверяем, нет ли машин с одинаковой скоростью
        same_speed_count = 0
        test_speed = self.initial_slow_speed if random.choice([True, False]) else self.initial_fast_speed
        
        for car in self.cars:
            if abs(car.speed - test_speed) < 0.1:
                same_speed_count += 1
        
        if same_speed_count >= 2:
            return False
        
        # Проверяем расстояние от точки спавна
        for car in self.cars:
            if abs(car.y - 500) < 100:  # Проверяем область вокруг точки спавна
                return False
        return True

    def generate_car(self, lane):
        is_fast = random.choice([True, False])
        speed_variation = random.uniform(-0.5, 0.5)
        base_speed = self.initial_fast_speed if is_fast else self.initial_slow_speed
        speed = base_speed + speed_variation
        
        car = Car(lane, speed, is_fast, 
                  self.car_fast if is_fast else self.car_slow, 
                  self.lane_positions)
        
        # Можно задать разные точки исчезновения для разных полос
        end_points = {
            0: 50,    # левая полоса уходит влево
            1: 150,   # вторая полоса чуть левее
            2: 350,   # третья полоса чуть правее
            3: 450    # правая полоса уходит вправо
        }
        car.set_end_point(end_points[lane])
        
        self.cars.append(car)

    def handle_input(self, event):
        # Обработка консоли
        if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKQUOTE:
            self.debug_console.toggle()
        if self.debug_console.handle_input(event):
            return True  # Команда выполнена

    def draw_grid(self):
        grid = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        for x in range(0, self.WIDTH, 50):
            pygame.draw.line(grid, (0, 255, 0, 64), (x, 0), (x, self.HEIGHT))
        for y in range(0, self.HEIGHT, 50):
            pygame.draw.line(grid, (0, 255, 0, 64), (0, y), (self.WIDTH, y))
        self.screen.blit(grid, (0, 0))


class Car:
    def __init__(self, lane, speed, is_fast, image, lane_positions):
        self.lane = lane
        self.speed = speed
        self.image = image
        self.scale = 0.4  # Увеличен начальный масштаб с 0.3 до 0.4
        self.lane_positions = lane_positions
        
        # Точки появления и исчезновения
        self.start_x = 250
        self.start_y = 500
        self.target_x = lane_positions[lane]
        self.end_y = 750
        self.end_x = lane_positions[lane]
        
        self.x = self.start_x
        self.y = self.start_y
        
        # Увеличенное начальное масштабирование
        scaled_size = (int(90 * self.scale), int(90 * self.scale))  # Увеличено с 70 до 90
        self.scaled_image = pygame.transform.scale(image, scaled_size)
        self.rect = self.scaled_image.get_rect(center=(self.x, self.y))

    def set_end_point(self, x, y=750):
        self.end_x = x
        self.end_y = y

    def move(self):
        self.y += self.speed
        
        total_distance_y = self.end_y - self.start_y
        progress = (self.y - self.start_y) / total_distance_y
        progress = max(0, min(1, progress))
        
        self.x = self.start_x + (self.end_x - self.start_x) * progress
        
        # Увеличен диапазон масштабирования
        self.scale = 0.4 + progress * 0.8  # От 0.4 до 1.2
        
        # Обновляем спрайт с новым размером
        scaled_size = (int(90 * self.scale), int(90 * self.scale))
        self.scaled_image = pygame.transform.scale(self.image, scaled_size)
        self.rect = self.scaled_image.get_rect(center=(self.x, self.y))

    def draw(self, screen):
        screen.blit(self.scaled_image, self.rect)


class Bag:
    def __init__(self, x, image):
        self.value = random.randint(2, 8)  # 2-8 монет за каждую собранную монетку
        self.x = x
        self.y = 0
        self.collected = False
        self.image = image
        self.scale = 0.3
        self.rect = None
        self.update_rect()

    def move(self):
        self.y += 3
        self.scale = 0.3 + (self.y / 800) * 0.7
        self.update_rect()

    def update_rect(self):
        scaled_size = (int(50 * self.scale), int(50 * self.scale))
        self.scaled_image = pygame.transform.scale(self.image, scaled_size)
        self.rect = self.scaled_image.get_rect(center=(self.x, self.y))

    def draw(self, screen):
        if not self.collected:
            screen.blit(self.scaled_image, self.rect)