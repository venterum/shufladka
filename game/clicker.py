import pygame
from game.data_manager import DataManager
from game.shop import Shop
from pathlib import Path
from PIL import Image
import io
from game.match3 import Match3Game

# основной класс игры, управляет всей механикой кликера
class Clicker:
    def __init__(self):
        # загрузка экрана загрузки
        self.loading_screen = pygame.Surface((500, 800))
        self.loading_screen.fill((240, 240, 240))
        loading_font = pygame.font.SysFont('Arial', 36)
        loading_text = loading_font.render('Загрузка...', True, (100, 100, 100))
        self.loading_screen.blit(loading_text, 
                               (250 - loading_text.get_width()//2, 
                                400 - loading_text.get_height()//2))
        
        # загрузка сохранения
        self.db = DataManager()
        game_state = self.db.load_game_state()
        self.clicks = game_state[0]    # накопленные лапки
        self.coins = game_state[1]     # монетки
        self.click_multiplier = game_state[2]  # множитель клика
        active_skin = game_state[3]    # текущий скин кота
        active_background = game_state[4]  # текущий фон
        
        # пути к ресурсам
        assets_path = Path("assets")
        sprites_path = assets_path / "sprites"
        fonts_path = assets_path / "fonts"
        
        # шрифты для текста
        self.font = pygame.font.Font(fonts_path / "Tiny5-Regular.ttf", 32)
        self.small_font = pygame.font.Font(fonts_path / "Tiny5-Regular.ttf", 24)
        
        # загрузка и обрезка фона
        bg = pygame.image.load(active_background)
        bg_rect = bg.get_rect()
        crop_rect = pygame.Rect(
            (bg_rect.width - 500) // 2,
            (bg_rect.height - 800) // 2,
            500, 800
        )
        self.background = bg.subsurface(crop_rect)
        
        # загрузка скина кота
        if active_skin.endswith('.gif'):
            self.cat_frames = self.load_gif_frames(active_skin)
            self.current_frame = 0
            self.frame_delay = 0
            self.cat_image = self.cat_frames[0]
        else:
            self.cat_frames = None
            self.cat_image = pygame.image.load(active_skin)
            
        self.cat_image = pygame.transform.scale(self.cat_image, (250, 250))
        self.cat_rect = self.cat_image.get_rect(center=(250, 400))
        
        # иконки и элементы интерфейса
        self.paw_image = pygame.image.load(sprites_path / "paw.png")
        self.paw_image = pygame.transform.scale(self.paw_image, (35, 35))
        
        self.coin_image = pygame.image.load(sprites_path / "coin.png")
        self.coin_image = pygame.transform.scale(self.coin_image, (35, 35))
        
        self.shop_image = pygame.image.load(sprites_path / "shop_sign.png")
        self.shop_image = pygame.transform.scale(self.shop_image, (500, 250))
        
        # анимации и состояния
        self.cat_animation = False
        self.cat_scale = 1.0
        self.shop_scale = 1.0
        self.plus_animations = []
        
        # области кликов и кнопки
        self.shop_rect = pygame.Rect(0, 550, 500, 250)
        self.minigames_btn = pygame.Rect(280, 20, 200, 50)
        self.settings_btn = pygame.Rect(280, 80, 200, 50)  # кнопка настроек
        
        # менеджер магазина и флаги меню
        self.shop = Shop(self.db)
        self.in_shop = False
        self.in_minigames = False
        self.in_settings = False
        
        # фон для счетчиков
        self.stats_bg = pygame.Surface((250, 110), pygame.SRCALPHA)
        pygame.draw.rect(self.stats_bg, (30, 30, 30, 180), self.stats_bg.get_rect(), border_radius=15)
        
        # состояние консоли
        self.console_enabled = False  # флаг включения консоли
        self.console_open = False
        self.console_text = ""
        self.console_font = pygame.font.SysFont('Consolas', 20)
        self.console_bg = pygame.Surface((500, 100), pygame.SRCALPHA)
        pygame.draw.rect(self.console_bg, (0, 0, 0, 200), self.console_bg.get_rect())
        
        # диалоги подтверждения
        self.show_confirm = False
        self.confirm_type = None
        self.confirm_message = ""
        self.confirm_action = None
        
        pygame.mixer.init()
        self.current_music = None
        self.load_active_music()
        
        # флаг первого запуска
        self.first_launch = not Path("game/data/player.json").exists()

    def load_gif_frames(self, path):
        frames = []
        with Image.open(path) as gif:
            for frame in range(gif.n_frames):
                gif.seek(frame)
                frame_surface = pygame.image.fromstring(
                    gif.convert('RGBA').tobytes(), gif.size, 'RGBA'
                )
                frame_surface = pygame.transform.scale(frame_surface, (250, 250))
                frames.append(frame_surface)
        return frames

    def load_active_music(self):
        music_data = self.db.load_music()
        for music in music_data:
            if music[4] and music[2]:  # если активна и путь не пустой
                if self.current_music != music[2]:
                    pygame.mixer.music.load(music[2])
                    pygame.mixer.music.play(-1)  # зацикливаем
                    self.current_music = music[2]
                break
        else:  # если ничего не активно или выбрано "Без музыки"
            pygame.mixer.music.stop()
            self.current_music = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKQUOTE and self.console_enabled:  # проверяем включена ли консоль
                self.console_open = not self.console_open
                self.console_text = ""
                return
            
            if self.console_open:
                if event.key == pygame.K_RETURN:  # Enter
                    self.handle_console_command(self.console_text.upper())
                    self.console_open = False
                    self.console_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.console_text = self.console_text[:-1]
                else:
                    self.console_text += event.unicode
                return
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.show_confirm:
                confirm_btn = pygame.Rect(100, 450, 140, 50)
                cancel_btn = pygame.Rect(260, 450, 140, 50)
                
                if confirm_btn.collidepoint(event.pos):
                    if self.confirm_action:
                        self.confirm_action()
                    self.show_confirm = False
                elif cancel_btn.collidepoint(event.pos):
                    self.show_confirm = False
                return
            
            if self.in_settings:
                reset_btn = pygame.Rect(50, 200, 400, 60)
                console_btn = pygame.Rect(50, 280, 400, 60)
                tutorial_btn = pygame.Rect(50, 360, 400, 60)
                back_btn = pygame.Rect(50, 650, 400, 60)
                
                if reset_btn.collidepoint(event.pos):
                    self.show_confirm = True
                    self.confirm_type = "reset"
                    self.confirm_message = ["Вы уверены, что хотите удалить весь прогресс?",
                                          "Игра будет перезапущена, и все достижения",
                                          "будут потеряны навсегда."]
                    self.confirm_action = self.reset_progress
                elif console_btn.collidepoint(event.pos):
                    if not self.console_enabled:
                        self.show_confirm = True
                        self.confirm_type = "console"
                        self.confirm_message = ["Консоль разработчика может сделать игру",
                                              "менее интересной. Она предназначена",
                                              "для тестирования и отладки."]
                        self.confirm_action = self.toggle_console
                    else:
                        self.console_enabled = False
                elif tutorial_btn.collidepoint(event.pos):
                    self.show_tutorial()
                elif back_btn.collidepoint(event.pos):
                    self.in_settings = False
            else:
                if self.settings_btn.collidepoint(event.pos):
                    self.in_settings = True
                if self.in_shop:
                    result = self.shop.handle_event(event, event.pos, self.coins, self.clicks)
                    self.coins = result["coins"]
                    self.clicks = result["paws"]
                    
                    if result.get("multiplier"):
                        self.click_multiplier = result["multiplier"]
                    
                    if result.get("skin"):
                        if result.get("reload_skin") or result["skin"].endswith('.gif'):
                            self.cat_frames = self.load_gif_frames(result["skin"])
                            self.current_frame = 0
                            self.frame_delay = 0
                            self.cat_image = self.cat_frames[0]
                        else:
                            self.cat_frames = None
                            self.cat_image = pygame.image.load(result["skin"])
                            self.cat_image = pygame.transform.scale(self.cat_image, (250, 250))
                    
                    if result.get("background"):
                        bg = pygame.image.load(result["background"])
                        bg_rect = bg.get_rect()
                        crop_rect = pygame.Rect(
                            (bg_rect.width - 500) // 2,
                            (bg_rect.height - 800) // 2,
                            500, 800
                        )
                        self.background = bg.subsurface(crop_rect)
                    
                    if result["close"]:
                        self.in_shop = False
                    
                    self.db.save_game_state(
                        self.clicks, 
                        self.coins, 
                        self.click_multiplier,
                        result.get("skin"),
                        result.get("background")
                    )
                    
                    if "music" in result and result["music"] != self.current_music:
                        self.load_active_music()
                elif self.in_minigames:
                    match_3_btn = pygame.Rect(50, 200, 400, 100)
                    crossy_btn = pygame.Rect(50, 320, 400, 100)
                    back_btn = pygame.Rect(50, 650, 400, 60)
                    
                    if match_3_btn.collidepoint(event.pos):
                        def return_callback(data=None):
                            if data and "coins" in data:
                                self.coins = data["coins"]
                            self.state = "game"
                        
                        game = Match3Game(return_callback)
                        game.run()
                    elif crossy_btn.collidepoint(event.pos):
                        def return_callback(data=None):
                            if data and "coins" in data:
                                self.coins = data["coins"]
                            self.state = "game"
                        
                        from game.road import RoadGame
                        game = RoadGame(self.handle_minigame_return)
                        game.run()
                    elif back_btn.collidepoint(event.pos):
                        self.in_minigames = False
                else:
                    if self.cat_rect.collidepoint(event.pos):
                        earned = 1 * self.click_multiplier
                        self.clicks += earned
                        self.cat_animation = True
                        self.cat_scale = 0.9
                        self.plus_animations.append([event.pos[0], event.pos[1], 255, earned])
                        self.db.save_game_state(self.clicks, self.coins, self.click_multiplier)
                    elif self.shop_rect.collidepoint(event.pos):
                        self.in_shop = True
                        self.shop_scale = 0.9
                    elif self.minigames_btn.collidepoint(event.pos):
                        self.in_minigames = True

    def update(self):
        if self.cat_frames:
            self.frame_delay += 1
            if self.frame_delay >= 8:  # замедляем анимацию (было 3)
                self.frame_delay = 0
                self.current_frame = (self.current_frame + 1) % len(self.cat_frames)
                self.cat_image = self.cat_frames[self.current_frame]
        
        if self.cat_animation:
            self.cat_scale += 0.02
            if self.cat_scale >= 1.0:
                self.cat_scale = 1.0
                self.cat_animation = False
        
        if self.shop_scale < 1.0:
            self.shop_scale += 0.02
            if self.shop_scale >= 1.0:
                self.shop_scale = 1.0
        
        for anim in self.plus_animations[:]:
            anim[1] -= 1
            anim[2] -= 5 
            if anim[2] <= 0:
                self.plus_animations.remove(anim)

    def draw(self, screen):
        if self.in_settings:
            bg = pygame.Surface((500, 800))
            bg.fill((240, 240, 240))
            for i in range(20):
                alpha = 100 - i * 5
                if alpha > 0:
                    pygame.draw.rect(bg, (230, 230, 230, alpha), (0, i*40, 500, 40))
            screen.blit(bg, (0, 0))
            
            # верхняя панель
            top_panel = pygame.Surface((500, 100), pygame.SRCALPHA)
            pygame.draw.rect(top_panel, (30, 30, 30, 180), (0, 0, 500, 100))
            screen.blit(top_panel, (0, 0))
            
            title = self.font.render("Настройки", True, (255, 255, 255))
            screen.blit(title, (250 - title.get_width()//2, 35))
            
            # кнопки настроек
            reset_btn = pygame.Rect(50, 200, 400, 60)
            console_btn = pygame.Rect(50, 280, 400, 60)
            tutorial_btn = pygame.Rect(50, 360, 400, 60)
            
            pygame.draw.rect(screen, (200, 100, 100), reset_btn, border_radius=15)
            pygame.draw.rect(screen, (100, 149, 237), console_btn, border_radius=15)
            pygame.draw.rect(screen, (100, 149, 237), tutorial_btn, border_radius=15)
            
            reset_text = self.font.render("Удалить прогресс", True, (255, 255, 255))
            console_text = self.font.render(
                "Отключить консоль" if self.console_enabled else "Включить консоль", 
                True, (255, 255, 255)
            )
            tutorial_text = self.font.render("Показать обучение", True, (255, 255, 255))
            
            screen.blit(reset_text, (reset_btn.centerx - reset_text.get_width()//2,
                                    reset_btn.centery - reset_text.get_height()//2))
            screen.blit(console_text, (console_btn.centerx - console_text.get_width()//2,
                                     console_btn.centery - console_text.get_height()//2))
            screen.blit(tutorial_text, (tutorial_btn.centerx - tutorial_text.get_width()//2,
                                      tutorial_btn.centery - tutorial_text.get_height()//2))
            
            # кнопка назад
            back_btn = pygame.Rect(50, 650, 400, 60)
            pygame.draw.rect(screen, (100, 149, 237), back_btn, border_radius=15)
            back_text = self.font.render("Назад", True, (255, 255, 255))
            screen.blit(back_text, (back_btn.centerx - back_text.get_width()//2,
                                   back_btn.centery - back_text.get_height()//2))
        elif self.in_shop:
            self.shop.draw(screen, self.coins, self.clicks)
        elif self.in_minigames:
            bg = pygame.Surface((500, 800))
            bg.fill((240, 240, 240))
            for i in range(20):
                alpha = 100 - i * 5
                if alpha > 0:
                    pygame.draw.rect(bg, (230, 230, 230, alpha), (0, i*40, 500, 40))
            screen.blit(bg, (0, 0))
            
            # верхняя панель
            top_panel = pygame.Surface((500, 100), pygame.SRCALPHA)
            pygame.draw.rect(top_panel, (30, 30, 30, 180), (0, 0, 500, 100))
            screen.blit(top_panel, (0, 0))
            
            title = self.font.render("Мини-игры", True, (255, 255, 255))
            screen.blit(title, (250 - title.get_width()//2, 35))
            
            # кнопки игр
            match_3_btn = pygame.Rect(50, 200, 400, 100)
            crossy_btn = pygame.Rect(50, 320, 400, 100)
            
            for btn in [match_3_btn, crossy_btn]:
                pygame.draw.rect(screen, (100, 149, 237), btn, border_radius=15)
            
            match_3_text = self.font.render("Кот-в-ряд", True, (255, 255, 255))
            crossy_text = self.font.render("Котик переходит дорогу", True, (255, 255, 255))
            
            screen.blit(match_3_text, (match_3_btn.centerx - match_3_text.get_width()//2,
                                     match_3_btn.centery - match_3_text.get_height()//2))
            screen.blit(crossy_text, (crossy_btn.centerx - crossy_text.get_width()//2,
                                    crossy_btn.centery - crossy_text.get_height()//2))
            
            info_text = self.small_font.render("Играй, чтобы заработать больше монеток", True, (50, 50, 50))
            info_text2 = self.small_font.render("и получить уникальные бонусы!", True, (50, 50, 50))
            screen.blit(info_text, (250 - info_text.get_width()//2, 500))
            screen.blit(info_text2, (250 - info_text2.get_width()//2, 530))
            
            # кнопка назад
            back_btn = pygame.Rect(50, 650, 400, 60)
            pygame.draw.rect(screen, (200, 100, 100), back_btn, border_radius=15)
            back_text = self.font.render("Назад", True, (255, 255, 255))
            screen.blit(back_text, (back_btn.centerx - back_text.get_width()//2,
                                  back_btn.centery - back_text.get_height()//2))
        else:
            screen.blit(self.background, (0, 0))
            
            pygame.draw.rect(screen, (100, 149, 237), self.minigames_btn, border_radius=10)
            minigames_text = self.font.render("Мини-игры", True, (255, 255, 255))
            screen.blit(minigames_text, (self.minigames_btn.centerx - minigames_text.get_width()//2,
                                       self.minigames_btn.centery - minigames_text.get_height()//2))
            
            pygame.draw.rect(screen, (100, 149, 237), self.settings_btn, border_radius=10)
            settings_text = self.font.render("Настройки", True, (255, 255, 255))
            screen.blit(settings_text, (self.settings_btn.centerx - settings_text.get_width()//2,
                                      self.settings_btn.centery - settings_text.get_height()//2))
            
            scaled_cat = pygame.transform.scale(
                self.cat_image,
                (int(250 * self.cat_scale),
                 int(250 * self.cat_scale))
            )
            scaled_rect = scaled_cat.get_rect(center=self.cat_rect.center)
            screen.blit(scaled_cat, scaled_rect)
            
            screen.blit(self.stats_bg, (20, 20))
            
            coin_rect = self.coin_image.get_rect(topleft=(35, 30))
            screen.blit(self.coin_image, coin_rect)
            coins_text = self.font.render(f"{self.coins:,}", True, (255, 255, 255))
            screen.blit(coins_text, (coin_rect.right + 15, 30))
            
            paw_rect = self.paw_image.get_rect(topleft=(35, coin_rect.bottom + 5))
            screen.blit(self.paw_image, paw_rect)
            clicks_text = self.font.render(f"{self.clicks:,}", True, (255, 255, 255))
            screen.blit(clicks_text, (paw_rect.right + 15, paw_rect.top))
            
            for anim in self.plus_animations:
                plus_text = self.font.render(f"+{anim[3]}", True, (255, 255, 255))
                plus_text.set_alpha(anim[2])
                screen.blit(plus_text, (anim[0], anim[1]))
            
            scaled_shop = pygame.transform.scale(
                self.shop_image,
                (int(500 * self.shop_scale),
                 int(250 * self.shop_scale))
            )
            scaled_shop_rect = scaled_shop.get_rect(center=self.shop_rect.center)
            screen.blit(scaled_shop, scaled_shop_rect)
        
        # отрисовка консоли поверх всего
        if self.console_open:
            screen.blit(self.console_bg, (0, 0))
            text = self.console_font.render(f"~ {self.console_text}", True, (0, 255, 0))
            screen.blit(text, (10, 10))

        # отрисовка диалога подтверждения
        if self.show_confirm:
            self.draw_confirm_dialog(screen)

        # Отрисовка сетки если включена
        if self.db.get_grid_state():
            self.draw_grid(screen)

    def handle_console_command(self, command):
        if command == "MOTHERLODE":
            self.clicks += 50000
            self.db.save_game_state(self.clicks, self.coins, self.click_multiplier)
        elif command == "HESOYAM":
            self.clicks += 250000
            self.db.save_game_state(self.clicks, self.coins, self.click_multiplier)
        elif command == "101111":
            self.coins += 100
            self.db.save_game_state(self.clicks, self.coins, self.click_multiplier)
        elif command == "ROSEBUD":  # код из The Sims
            # Разблокируем все улучшения, скины и фоны
            for upgrade in self.shop.upgrades:
                upgrade[3] = True  # purchased = True
            for skin in self.shop.skins:
                skin[3] = True
            for bg in self.shop.backgrounds:
                bg[3] = True
            self.db.save_all_unlocked()
        elif command == "POORINME":
            # Забираем все улучшения, скины и фоны
            for upgrade in self.shop.upgrades:
                upgrade[3] = False
                upgrade[4] = False
            for skin in self.shop.skins:
                if skin[0] != "Серый кот":  # оставляем базовый скин
                    skin[3] = False
                    skin[4] = False
            for bg in self.shop.backgrounds:
                if bg[0] != "Родная деревня":  # оставляем базовый фон
                    bg[3] = False
                    bg[4] = False
            self.clicks = 0
            self.coins = 0
            self.click_multiplier = 1
            self.db.save_all_locked()
        elif command.upper() == "GRID":
            self.db.toggle_grid()
            return True
        return False

    def reset_progress(self):
        import os
        data_path = Path("game/data")
        for file in data_path.glob("*.json"):
            os.remove(file)
        # перезапускаем игру
        import sys
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def toggle_console(self):
        self.console_enabled = True
        self.show_confirm = False

    def draw_confirm_dialog(self, screen):
        # затемнение фона
        overlay = pygame.Surface((500, 800))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(160)
        screen.blit(overlay, (0, 0))
        
        # диалоговое окно
        dialog = pygame.Rect(50, 250, 400, 300)
        pygame.draw.rect(screen, (240, 240, 240), dialog, border_radius=15)
        
        # многострочное сообщение
        if isinstance(self.confirm_message, list):
            messages = self.confirm_message
        else:
            messages = [self.confirm_message]
        
        for i, line in enumerate(messages):
            text = self.small_font.render(line, True, (50, 50, 50))
            screen.blit(text, (dialog.centerx - text.get_width()//2, dialog.top + 40 + i*30))
        
        # кнопки
        confirm_btn = pygame.Rect(100, 450, 140, 50)
        cancel_btn = pygame.Rect(260, 450, 140, 50)
        
        pygame.draw.rect(screen, (200, 100, 100), confirm_btn, border_radius=10)
        pygame.draw.rect(screen, (100, 149, 237), cancel_btn, border_radius=10)
        
        confirm_text = self.font.render("Да", True, (255, 255, 255))
        cancel_text = self.font.render("Отмена", True, (255, 255, 255))
        
        screen.blit(confirm_text, (confirm_btn.centerx - confirm_text.get_width()//2,
                                  confirm_btn.centery - confirm_text.get_height()//2))
        screen.blit(cancel_text, (cancel_btn.centerx - cancel_text.get_width()//2,
                                 cancel_btn.centery - cancel_text.get_height()//2))

    def show_tutorial(self):
        # здесь будет логика показа обучения
        # можно использовать тот же механизм диалогов
        self.show_confirm = True
        self.confirm_type = "tutorial"
        self.confirm_message = ["Кликай по коту, чтобы получать лапки",
                               "Обменивай лапки на монетки",
                               "Покупай улучшения в магазине",
                               "Открывай новых котиков и фоны"]
        self.confirm_action = lambda: None  # просто закрыть диалог

    def return_from_minigame(self):
        # Восстанавливаем окно и состояние основной игры
        self.screen = pygame.display.set_mode((500, 800))
        pygame.display.set_caption("Шуфлядка")
        self.in_minigames = False

    def draw_grid(self, screen):
        grid = pygame.Surface((500, 800), pygame.SRCALPHA)
        for x in range(0, 500, 50):
            pygame.draw.line(grid, (0, 255, 0, 64), (x, 0), (x, 800))
        for y in range(0, 800, 50):
            pygame.draw.line(grid, (0, 255, 0, 64), (0, y), (500, y))
        screen.blit(grid, (0, 0))

    def handle_minigame_return(self, data=None):
        if data and "coins" in data:
            # Обновляем отображение монет после возврата из мини-игры
            self.coins = data["coins"]
            # Сохраняем новое состояние
            self.db.save_game_state(
                self.clicks, 
                self.coins, 
                self.click_multiplier
            )