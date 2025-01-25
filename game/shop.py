import pygame
from pathlib import Path
from PIL import Image
import random
import time

# класс магазина с улучшениями и кастомизацией
class Shop:
    def __init__(self, db):
        self.db = db
        # шрифты для интерфейса
        fonts_path = Path("assets") / "fonts"
        self.font = pygame.font.Font(fonts_path / "Tiny5-Regular.ttf", 28)
        self.small_font = pygame.font.Font(fonts_path / "Tiny5-Regular.ttf", 22)
        
        # категории товаров
        self.categories = ["Улучшения", "Скины", "Фоны", "Музыка", "Обмен"]
        self.current_category = 0
        
        # загрузка данных
        self.upgrades = self.db.load_upgrades()
        self.skins = self.db.load_skins()
        self.backgrounds = self.db.load_backgrounds()
        self.music = self.db.load_music()
        
        # кнопки навигации
        self.back_btn = pygame.Rect(20, 20, 140, 45)
        self.next_btn = pygame.Rect(380, 20, 100, 45)
        self.prev_btn = pygame.Rect(260, 20, 100, 45)
        
        # область контента и настройки
        self.items_area = pygame.Rect(20, 80, 460, 680)
        
        # состояние диалога покупки
        self.show_confirm = False
        self.confirm_item = None
        self.confirm_type = None
        self.confirm_price = 0
        
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Инициализация системы обмена
        self.last_rate_update = 0
        self.exchange_rate = self.calculate_new_rate()
        self.update_interval = 300  # 5 минут в секундах

    def calculate_new_rate(self):
        return random.randint(7, 52)
        
    def update_exchange_rate(self):
        current_time = time.time()
        if current_time - self.last_rate_update >= self.update_interval:
            self.exchange_rate = self.calculate_new_rate()
            self.last_rate_update = current_time
    
    def draw(self, screen, coins, paws):
        bg = pygame.Surface((500, 800))
        bg.fill((240, 240, 240))
        for i in range(20):
            alpha = 100 - i * 5
            if alpha > 0:
                pygame.draw.rect(bg, (230, 230, 230, alpha), (0, i*40, 500, 40))
        screen.blit(bg, (0, 0))
        
        # Верхняя панель с кнопками
        top_panel = pygame.Surface((500, 150), pygame.SRCALPHA)
        pygame.draw.rect(top_panel, (30, 30, 30, 180), (0, 0, 500, 150))
        screen.blit(top_panel, (0, 0))
        
        # Кнопки управления
        pygame.draw.rect(screen, (100, 149, 237), self.back_btn, border_radius=10)
        back_text = self.font.render("Назад", True, (255, 255, 255))
        screen.blit(back_text, (self.back_btn.centerx - back_text.get_width()//2, 
                               self.back_btn.centery - back_text.get_height()//2))
        
        pygame.draw.rect(screen, (100, 149, 237), self.prev_btn, border_radius=10)
        pygame.draw.rect(screen, (100, 149, 237), self.next_btn, border_radius=10)
        prev_text = self.font.render("<", True, (255, 255, 255))
        next_text = self.font.render(">", True, (255, 255, 255))
        screen.blit(prev_text, (self.prev_btn.centerx - prev_text.get_width()//2, 
                               self.prev_btn.centery - prev_text.get_height()//2))
        screen.blit(next_text, (self.next_btn.centerx - next_text.get_width()//2, 
                               self.next_btn.centery - next_text.get_height()//2))
        
        # Заголовок категории магазина
        cat_text = self.font.render(self.categories[self.current_category], True, (255, 255, 255))
        screen.blit(cat_text, (250 - cat_text.get_width()//2, 80))
        
        # Баланс
        balance_text = self.font.render(f"Монеты: {coins:,} | Лапки: {paws:,}", True, (255, 255, 255))
        screen.blit(balance_text, (250 - balance_text.get_width()//2, 115))
        
        # Основная область
        if self.categories[self.current_category] == "Улучшения":
            self.draw_upgrades(screen, coins, 160)
        elif self.categories[self.current_category] == "Скины":
            self.draw_skins(screen, coins, 160)
        elif self.categories[self.current_category] == "Фоны":
            self.draw_backgrounds(screen, coins, 160)
        elif self.categories[self.current_category] == "Музыка":
            self.draw_music(screen, coins, 160)
        elif self.categories[self.current_category] == "Обмен":
            self.draw_exchange(screen, coins, paws, 0)
        
        if self.show_confirm:
            self.draw_confirm_dialog(screen, coins)

    def draw_confirm_dialog(self, screen, coins):
        # Затемнение всего экрана
        overlay = pygame.Surface((500, 800))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(160)
        screen.blit(overlay, (0, 0))

        # Диалоговое окно
        dialog = pygame.Rect(50, 250, 400, 300)
        pygame.draw.rect(screen, (240, 240, 240), dialog, border_radius=15)
        
        title = self.font.render("Подтвердите покупку", True, (50, 50, 50))
        name = self.font.render(self.confirm_item[0], True, (50, 50, 50))
        price = self.font.render(f"Цена: {self.confirm_price}", True, (50, 50, 50))
        
        screen.blit(title, (dialog.centerx - title.get_width()//2, dialog.top + 40))
        screen.blit(name, (dialog.centerx - name.get_width()//2, dialog.top + 100))
        screen.blit(price, (dialog.centerx - price.get_width()//2, dialog.top + 160))
        
        confirm_btn = pygame.Rect(100, 450, 140, 50)
        cancel_btn = pygame.Rect(260, 450, 140, 50)
        
        pygame.draw.rect(screen, (100, 200, 100), confirm_btn, border_radius=10)
        pygame.draw.rect(screen, (200, 100, 100), cancel_btn, border_radius=10)
        
        confirm_text = self.font.render("Купить", True, (255, 255, 255))
        cancel_text = self.font.render("Отмена", True, (255, 255, 255))
        
        screen.blit(confirm_text, (confirm_btn.centerx - confirm_text.get_width()//2, 
                                 confirm_btn.centery - confirm_text.get_height()//2))
        screen.blit(cancel_text, (cancel_btn.centerx - cancel_text.get_width()//2, 
                                cancel_btn.centery - cancel_text.get_height()//2))

    def draw_upgrades(self, surface, coins, start_y):
        y = start_y
        for upgrade in self.upgrades:
            item_rect = pygame.Rect(20, y, 460, 110)
            color = (150, 150, 150) if upgrade[3] else (100, 149, 237)
            if upgrade[4]:
                color = (50, 205, 50)
            
            pygame.draw.rect(surface, color, item_rect, border_radius=15)
            if upgrade[4]:
                pygame.draw.rect(surface, (255, 255, 255), item_rect, 3, border_radius=15)
            
            # название улучшения
            name = self.font.render(upgrade[0], True, (255, 255, 255))
            surface.blit(name, (item_rect.left + 20, y + 15))
            
            # множитель и цена/статус покупки
            if upgrade[3]:
                status = self.small_font.render(f"Множитель: x{upgrade[2]} | Куплено", True, (255, 255, 255))
            else:
                status = self.small_font.render(f"Множитель: x{upgrade[2]} | {upgrade[1]:,} монет", True, (255, 255, 255))
            surface.blit(status, (item_rect.left + 20, y + 45))
            
            # описание эффекта
            descriptions = {
                "Мягкие лапки": "Мягкие, могут тыкать за двоих",
                "Острые когти": "Цепляют больше монеток",
                "Кошачья сила": "Сама притягивает золото",
                "Мощь тигра": "Главное, что рядом нет собак",
                "Космический кот": "А он умеет загребать монетки!"
            }
            desc = self.small_font.render(descriptions.get(upgrade[0], ""), True, (255, 255, 255))
            surface.blit(desc, (item_rect.left + 20, y + 75))
            
            # кнопка использовать
            if upgrade[3] and not upgrade[4]:
                use_rect = pygame.Rect(item_rect.right - 160, y + 40, 140, 30)
                pygame.draw.rect(surface, (100, 200, 100), use_rect, border_radius=8)
                use_text = self.small_font.render("Использовать", True, (255, 255, 255))
                surface.blit(use_text, (use_rect.centerx - use_text.get_width()//2, 
                                      use_rect.centery - use_text.get_height()//2))
            
            y += 120
        
        self.max_scroll = max(0, y - 630)

    def draw_skins(self, surface, coins, start_y):
        item_width = 220  # ширина карточки
        item_height = 140  # увеличиваем высоту карточки
        padding = 20  # отступ между карточками
        
        for i, skin in enumerate(self.skins):
            # вычисляем позицию в сетке 2x4
            row = i // 2
            col = i % 2
            
            x = padding + col * (item_width + padding)
            y = start_y + row * (item_height + padding)
            
            item_rect = pygame.Rect(x, y, item_width, item_height)
            color = (150, 150, 150) if skin[3] else (100, 149, 237)
            if skin[4]:
                color = (50, 205, 50)
            
            pygame.draw.rect(surface, color, item_rect, border_radius=15)
            if skin[4]:
                pygame.draw.rect(surface, (255, 255, 255), item_rect, 3, border_radius=15)
            
            # превью скина
            try:
                if skin[2].endswith('.gif'):
                    with Image.open(skin[2]) as gif:
                        frame = pygame.image.fromstring(
                            gif.convert('RGBA').tobytes(), gif.size, 'RGBA'
                        )
                else:
                    frame = pygame.image.load(skin[2])
                
                preview_size = 80  # увеличиваем размер превью
                preview = pygame.transform.scale(frame, (preview_size, preview_size))
                preview_x = item_rect.right - preview_size - 10
                preview_y = item_rect.top + (item_height - preview_size) // 2
                surface.blit(preview, (preview_x, preview_y))
            except:
                pass
            
            # название скина
            name = self.small_font.render(skin[0], True, (255, 255, 255))
            surface.blit(name, (item_rect.left + 15, y + 20))
            
            # статус или цена
            if skin[3]:
                status = self.small_font.render("Куплено", True, (255, 255, 255))
            else:
                status = self.small_font.render(f"{skin[1]:,} монет", True, (255, 255, 255))
            surface.blit(status, (item_rect.left + 15, y + 55))
            
            # кнопка использовать
            if skin[3] and not skin[4]:
                use_rect = pygame.Rect(item_rect.left + 15, y + 90, 100, 35)  # увеличиваем размер кнопки
                pygame.draw.rect(surface, (100, 200, 100), use_rect, border_radius=8)
                use_text = self.small_font.render("Надеть", True, (255, 255, 255))
                surface.blit(use_text, (use_rect.centerx - use_text.get_width()//2, 
                                      use_rect.centery - use_text.get_height()//2))

    def draw_backgrounds(self, surface, coins, start_y):
        y = start_y
        for bg in self.backgrounds:
            item_rect = pygame.Rect(20, y, 460, 80)
            color = (150, 150, 150) if bg[3] else (100, 149, 237)
            if bg[4]:
                color = (50, 205, 50)
            
            pygame.draw.rect(surface, color, item_rect, border_radius=15)
            if bg[4]:
                pygame.draw.rect(surface, (255, 255, 255), item_rect, 3, border_radius=15)
            
            name = self.font.render(bg[0], True, (255, 255, 255))
            if bg[3]:
                status = self.small_font.render("Куплено", True, (255, 255, 255))
            else:
                status = self.small_font.render(f"Цена: {bg[1]:,} монет", True, (255, 255, 255))
            
            surface.blit(name, (item_rect.left + 20, y + 15))
            surface.blit(status, (item_rect.left + 20, y + 45))
            
            if bg[3] and not bg[4]:
                use_rect = pygame.Rect(item_rect.right - 150, y + 25, 130, 30)
                pygame.draw.rect(surface, (100, 200, 100), use_rect, border_radius=8)
                use_text = self.small_font.render("Использовать", True, (255, 255, 255))
                surface.blit(use_text, (use_rect.centerx - use_text.get_width()//2, 
                                      use_rect.centery - use_text.get_height()//2))
            
            y += 90

    def draw_music(self, surface, coins, start_y):
        y = start_y
        for music in self.music:
            item_rect = pygame.Rect(20, y, 460, 80)
            color = (150, 150, 150) if music[3] else (100, 149, 237)
            if music[4]:
                color = (50, 205, 50)
            
            pygame.draw.rect(surface, color, item_rect, border_radius=15)
            if music[4]:
                pygame.draw.rect(surface, (255, 255, 255), item_rect, 3, border_radius=15)
            
            name = self.font.render(music[0], True, (255, 255, 255))
            if music[3]:
                status = self.small_font.render("Куплено", True, (255, 255, 255))
            else:
                status = self.small_font.render(f"Цена: {music[1]:,} монет", True, (255, 255, 255))
            
            surface.blit(name, (item_rect.left + 20, y + 15))
            surface.blit(status, (item_rect.left + 20, y + 45))
            
            if music[3] and not music[4]:
                use_rect = pygame.Rect(item_rect.right - 150, y + 25, 130, 30)
                pygame.draw.rect(surface, (100, 200, 100), use_rect, border_radius=8)
                use_text = self.small_font.render("Включить", True, (255, 255, 255))
                surface.blit(use_text, (use_rect.centerx - use_text.get_width()//2, 
                                      use_rect.centery - use_text.get_height()//2))
            
            y += 90

    def draw_exchange(self, surface, coins, paws, start_y):
        self.update_exchange_rate()
        
        # Сдвигаем весь контент ниже, чтобы избежать наложения с заголовком
        content_start = start_y + 160  # начинаем после верхней панели
        
        # Заголовок
        title = self.font.render("Обмен лапок на монетки", True, (255, 255, 255))
        surface.blit(title, (250 - title.get_width()//2, content_start))
        
        # Информационная панель
        info_rect = pygame.Rect(20, content_start + 50, 460, 120)
        pygame.draw.rect(surface, (60, 60, 60), info_rect, border_radius=15)
        
        # Текущий курс
        rate_text = self.font.render(f"Текущий курс: {self.exchange_rate} лапок = 1 монетка", True, (255, 255, 255))
        surface.blit(rate_text, (info_rect.left + 20, info_rect.top + 20))
        
        # Максимально возможный обмен
        max_exchange = paws // self.exchange_rate
        max_text = self.small_font.render(f"Можно получить: {max_exchange} монет", True, (200, 200, 200))
        surface.blit(max_text, (info_rect.left + 20, info_rect.top + 70))
        
        # Кнопка обмена
        if max_exchange > 0:
            exchange_btn = pygame.Rect(20, content_start + 190, 460, 60)
            pygame.draw.rect(surface, (100, 200, 100), exchange_btn, border_radius=15)
            btn_text = self.font.render(f"Обменять {max_exchange * self.exchange_rate} лапок на {max_exchange} монет", True, (255, 255, 255))
            surface.blit(btn_text, (exchange_btn.centerx - btn_text.get_width()//2, 
                                  exchange_btn.centery - btn_text.get_height()//2))
        else:
            # Неактивная кнопка
            exchange_btn = pygame.Rect(20, content_start + 190, 460, 60)
            pygame.draw.rect(surface, (150, 150, 150), exchange_btn, border_radius=15)
            btn_text = self.font.render("Недостаточно лапок для обмена", True, (255, 255, 255))
            surface.blit(btn_text, (exchange_btn.centerx - btn_text.get_width()//2, 
                                  exchange_btn.centery - btn_text.get_height()//2))
        
        # Большой таймер
        timer_rect = pygame.Rect(20, content_start + 270, 460, 200)
        pygame.draw.rect(surface, (60, 60, 60), timer_rect, border_radius=15)
        
        time_left = self.update_interval - (time.time() - self.last_rate_update)
        minutes = int(time_left // 60)
        seconds = int(time_left % 60)
        
        # Заголовок таймера
        timer_title = self.small_font.render("До следующего обновления курса:", True, (200, 200, 200))
        surface.blit(timer_title, (timer_rect.centerx - timer_title.get_width()//2, 
                                  timer_rect.top + 40))
        
        # Большой таймер с тем же шрифтом
        timer_text = self.font.render(f"{minutes:02d}:{seconds:02d}", True, (255, 255, 255))
        timer_text = pygame.transform.scale(timer_text, (timer_text.get_width() * 2, timer_text.get_height() * 2))
        surface.blit(timer_text, (timer_rect.centerx - timer_text.get_width()//2, 
                                 timer_rect.centery + 20))

    def handle_click(self, pos, coins, paws):
        result = {
            "coins": coins, 
            "paws": paws, 
            "multiplier": None, 
            "skin": None, 
            "background": None, 
            "close": False,
            "reload_skin": False,
            "music": None
        }
        
        if self.show_confirm:
            confirm_btn = pygame.Rect(100, 450, 140, 50)
            cancel_btn = pygame.Rect(260, 450, 140, 50)
            
            if confirm_btn.collidepoint(pos) and coins >= self.confirm_price:
                if self.confirm_type == "upgrade":
                    self.confirm_item[3] = True
                    self.db.update_upgrade(self.confirm_item[0], True)
                    result["coins"] = coins - self.confirm_price
                elif self.confirm_type == "skin":
                    self.confirm_item[3] = True
                    self.db.update_skin(self.confirm_item[0], True)
                    result["coins"] = coins - self.confirm_price
                elif self.confirm_type == "background":
                    self.confirm_item[3] = True
                    self.db.update_background(self.confirm_item[0], True)
                    result["coins"] = coins - self.confirm_price
                elif self.confirm_type == "music":
                    self.confirm_item[3] = True
                    self.db.update_music(self.confirm_item[0], True, True)
                    result["coins"] = coins - self.confirm_price
                    result["music"] = self.confirm_item[2]
            
            if confirm_btn.collidepoint(pos) or cancel_btn.collidepoint(pos):
                self.show_confirm = False
                self.confirm_item = None
                self.confirm_type = None
            
            return result
        
        if self.back_btn.collidepoint(pos):
            result["close"] = True
            return result
            
        if self.next_btn.collidepoint(pos):
            self.current_category = (self.current_category + 1) % len(self.categories)
            return result
            
        if self.prev_btn.collidepoint(pos):
            self.current_category = (self.current_category - 1) % len(self.categories)
            return result
            
        # Основная область контента начинается с y=160
        adjusted_y = pos[1] - 160
        
        if self.categories[self.current_category] == "Улучшения":
            for i, upgrade in enumerate(self.upgrades):
                item_rect = pygame.Rect(20, 160 + i * 120, 460, 110)  # обновляем размеры
                if item_rect.collidepoint(pos[0], pos[1]):
                    if not upgrade[3] and coins >= upgrade[1]:
                        self.show_confirm = True
                        self.confirm_item = upgrade
                        self.confirm_type = "upgrade"
                        self.confirm_price = upgrade[1]
                    elif upgrade[3] and not upgrade[4]:
                        for u in self.upgrades:
                            u[4] = False
                        upgrade[4] = True
                        self.db.update_upgrade(upgrade[0], True, True)
                        result["multiplier"] = upgrade[2]
                    
        elif self.categories[self.current_category] == "Скины":
            item_width = 220
            item_height = 140
            padding = 20
            
            for i, skin in enumerate(self.skins):
                row = i // 2
                col = i % 2
                
                x = padding + col * (item_width + padding)
                y = 160 + row * (item_height + padding)
                
                item_rect = pygame.Rect(x, y, item_width, item_height)
                if item_rect.collidepoint(pos[0], pos[1]):
                    if not skin[3] and coins >= skin[1]:
                        self.show_confirm = True
                        self.confirm_item = skin
                        self.confirm_type = "skin"
                        self.confirm_price = skin[1]
                    elif skin[3] and not skin[4]:
                        for s in self.skins:
                            s[4] = False
                        skin[4] = True
                        self.db.update_skin(skin[0], True, True)
                        result["skin"] = skin[2]
                        if skin[2].endswith('.gif'):
                            result["reload_skin"] = True
                    
        elif self.categories[self.current_category] == "Фоны":
            for i, bg in enumerate(self.backgrounds):
                item_rect = pygame.Rect(20, 160 + i * 90, 460, 80)
                if item_rect.collidepoint(pos[0], pos[1]):
                    if not bg[3] and coins >= bg[1]:
                        self.show_confirm = True
                        self.confirm_item = bg
                        self.confirm_type = "background"
                        self.confirm_price = bg[1]
                    elif bg[3] and not bg[4]:
                        for b in self.backgrounds:
                            b[4] = False
                        bg[4] = True
                        self.db.update_background(bg[0], True, True)
                        result["background"] = bg[2]
                    
        elif self.categories[self.current_category] == "Музыка":
            for i, music in enumerate(self.music):
                item_rect = pygame.Rect(20, 160 + i * 90, 460, 80)
                if item_rect.collidepoint(pos[0], pos[1]):
                    if not music[3] and coins >= music[1]:
                        self.show_confirm = True
                        self.confirm_item = music
                        self.confirm_type = "music"
                        self.confirm_price = music[1]
                    elif music[3] and not music[4]:
                        for m in self.music:
                            m[4] = False
                        music[4] = True
                        self.db.update_music(music[0], True, True)
                        result["music"] = music[2]
        
        elif self.categories[self.current_category] == "Обмен":
            self.update_exchange_rate()
            max_exchange = paws // self.exchange_rate
            if max_exchange > 0:
                exchange_btn = pygame.Rect(20, 350, 460, 60)  # обновленная позиция кнопки
                if exchange_btn.collidepoint(pos[0], pos[1]):
                    result["coins"] = coins + max_exchange
                    result["paws"] = paws - (max_exchange * self.exchange_rate)
        
        return result

    def handle_event(self, event, pos, coins, paws):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.handle_click(pos, coins, paws)
        
        return {
            "coins": coins,
            "paws": paws,
            "multiplier": None,
            "skin": None,
            "background": None,
            "close": False,
            "music": None
        } 