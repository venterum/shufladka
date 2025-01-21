import pygame
from pathlib import Path

class Shop:
    def __init__(self, db):
        self.db = db
        fonts_path = Path("assets") / "fonts"
        self.font = pygame.font.Font(fonts_path / "Tiny5-Regular.ttf", 24)
        self.small_font = pygame.font.Font(fonts_path / "Tiny5-Regular.ttf", 18)
        
        self.categories = ["Улучшения", "Скины", "Фоны", "Обмен"]
        self.current_category = 0
        
        self.upgrades = self.db.load_upgrades()
        self.skins = self.db.load_skins()
        self.backgrounds = self.db.load_backgrounds()
        
        self.back_btn = pygame.Rect(20, 20, 120, 40)
        self.next_btn = pygame.Rect(300, 20, 80, 40)
        self.prev_btn = pygame.Rect(200, 20, 80, 40)
        self.items_area = pygame.Rect(20, 80, 360, 580)
        self.exchange_rate = 10
        self.show_confirm = False
        self.confirm_item = None
        self.confirm_type = None  # "upgrade", "skin", "background"
        self.confirm_price = 0

    def draw(self, screen, coins, paws):
        bg = pygame.Surface((400, 700))
        bg.fill((240, 240, 240))
        for i in range(20):
            alpha = 100 - i * 5
            if alpha > 0:
                pygame.draw.rect(bg, (230, 230, 230, alpha), (0, i*35, 400, 35))
        screen.blit(bg, (0, 0))
        
        pygame.draw.rect(screen, (100, 149, 237), self.back_btn, border_radius=10)
        back_text = self.font.render("Назад", True, (255, 255, 255))
        screen.blit(back_text, (self.back_btn.centerx - back_text.get_width()//2, 
                               self.back_btn.centery - back_text.get_height()//2))
        
        pygame.draw.rect(screen, (100, 149, 237), self.prev_btn, border_radius=10)
        pygame.draw.rect(screen, (100, 149, 237), self.next_btn, border_radius=10)
        prev_text = self.font.render("<", True, (255, 255, 255))
        next_text = self.font.render(">", True, (255, 255, 255))
        cat_text = self.font.render(self.categories[self.current_category], True, (50, 50, 50))
        screen.blit(prev_text, (230, 25))
        screen.blit(next_text, (330, 25))
        screen.blit(cat_text, (220 - cat_text.get_width()//2, 60))
        
        balance_text = self.font.render(f"Монеты: {coins} | Лапки: {paws}", True, (50, 50, 50))
        screen.blit(balance_text, (20, 100))
        
        if self.categories[self.current_category] == "Улучшения":
            self.draw_upgrades(screen, coins)
        elif self.categories[self.current_category] == "Скины":
            self.draw_skins(screen, coins)
        elif self.categories[self.current_category] == "Фоны":
            self.draw_backgrounds(screen, coins)
        elif self.categories[self.current_category] == "Обмен":
            self.draw_exchange(screen, paws)
        
        if self.show_confirm:
            confirm_btn, cancel_btn = self.draw_confirm_dialog(screen, coins)
            return confirm_btn, cancel_btn
        return None, None

    def draw_confirm_dialog(self, screen, coins):
        overlay = pygame.Surface((400, 700))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))

        dialog = pygame.Rect(50, 250, 300, 200)
        pygame.draw.rect(screen, (240, 240, 240), dialog, border_radius=15)
        
        title = self.font.render("Подтвердите покупку", True, (50, 50, 50))
        name = self.font.render(self.confirm_item[0], True, (50, 50, 50))
        price = self.font.render(f"Цена: {self.confirm_price}", True, (50, 50, 50))
        
        screen.blit(title, (dialog.centerx - title.get_width()//2, dialog.top + 20))
        screen.blit(name, (dialog.centerx - name.get_width()//2, dialog.top + 60))
        screen.blit(price, (dialog.centerx - price.get_width()//2, dialog.top + 100))
        
        confirm_btn = pygame.Rect(70, 380, 120, 50)
        cancel_btn = pygame.Rect(210, 380, 120, 50)
        
        pygame.draw.rect(screen, (100, 200, 100), confirm_btn, border_radius=10)
        pygame.draw.rect(screen, (200, 100, 100), cancel_btn, border_radius=10)
        
        confirm_text = self.font.render("Купить", True, (255, 255, 255))
        cancel_text = self.font.render("Отмена", True, (255, 255, 255))
        
        screen.blit(confirm_text, (confirm_btn.centerx - confirm_text.get_width()//2, 
                                 confirm_btn.centery - confirm_text.get_height()//2))
        screen.blit(cancel_text, (cancel_btn.centerx - cancel_text.get_width()//2, 
                                cancel_btn.centery - cancel_text.get_height()//2))
        
        return confirm_btn, cancel_btn

    def draw_upgrades(self, screen, coins):
        y = 150
        for upgrade in self.upgrades:
            item_rect = pygame.Rect(30, y, 340, 60)
            color = (150, 150, 150) if upgrade[3] else (100, 149, 237)
            if upgrade[4]:  # Активное улучшение
                color = (50, 205, 50)
                pygame.draw.rect(screen, color, item_rect, border_radius=15)
                pygame.draw.rect(screen, (255, 255, 255), item_rect, 3, border_radius=15)
            else:
                pygame.draw.rect(screen, color, item_rect, border_radius=15)
            
            name = self.font.render(upgrade[0], True, (255, 255, 255))
            if upgrade[3]:
                status = self.small_font.render("Куплено", True, (255, 255, 255))
            else:
                status = self.small_font.render(f"Цена: {upgrade[1]} монет", True, (255, 255, 255))
            mult = self.small_font.render(f"x{upgrade[2]} к клику", True, (255, 255, 255))
            
            screen.blit(name, (40, y + 8))
            screen.blit(status, (40, y + 32))
            screen.blit(mult, (200, y + 32))
            
            if upgrade[3] and not upgrade[4]:
                use_rect = pygame.Rect(200, y + 40, 120, 30)
                pygame.draw.rect(screen, (100, 200, 100), use_rect, border_radius=8)
                use_text = self.small_font.render("Использовать", True, (255, 255, 255))
                screen.blit(use_text, (use_rect.centerx - use_text.get_width()//2, 
                                     use_rect.centery - use_text.get_height()//2))
            
            y += 80

    def draw_skins(self, screen, coins):
        y = 150
        for skin in self.skins:
            item_rect = pygame.Rect(30, y, 340, 80)
            color = (150, 150, 150) if skin[3] else (100, 149, 237)
            if skin[4]:  # Активный скин
                color = (50, 205, 50)
                pygame.draw.rect(screen, color, item_rect, border_radius=15)
                pygame.draw.rect(screen, (255, 255, 255), item_rect, 3, border_radius=15)
            else:
                pygame.draw.rect(screen, color, item_rect, border_radius=15)
            
            name = self.font.render(skin[0], True, (255, 255, 255))
            if skin[3]:
                status = self.small_font.render("Куплено", True, (255, 255, 255))
            else:
                status = self.small_font.render(f"Цена: {skin[1]} монет", True, (255, 255, 255))
            
            screen.blit(name, (40, y + 10))
            screen.blit(status, (40, y + 40))
            
            if skin[3] and not skin[4]:
                use_rect = pygame.Rect(200, y + 40, 120, 30)
                pygame.draw.rect(screen, (100, 200, 100), use_rect, border_radius=8)
                use_text = self.small_font.render("Использовать", True, (255, 255, 255))
                screen.blit(use_text, (use_rect.centerx - use_text.get_width()//2, 
                                     use_rect.centery - use_text.get_height()//2))
            
            y += 100

    def draw_backgrounds(self, screen, coins):
        y = 150
        for bg in self.backgrounds:
            item_rect = pygame.Rect(30, y, 340, 80)
            color = (150, 150, 150) if bg[3] else (100, 149, 237)
            if bg[4]:  # Активный фон
                color = (50, 205, 50)
                pygame.draw.rect(screen, color, item_rect, border_radius=15)
                pygame.draw.rect(screen, (255, 255, 255), item_rect, 3, border_radius=15)
            else:
                pygame.draw.rect(screen, color, item_rect, border_radius=15)
            
            name = self.font.render(bg[0], True, (255, 255, 255))
            if bg[3]:
                status = self.small_font.render("Куплено", True, (255, 255, 255))
            else:
                status = self.small_font.render(f"Цена: {bg[1]} монет", True, (255, 255, 255))
            
            screen.blit(name, (40, y + 10))
            screen.blit(status, (40, y + 40))
            
            if bg[3] and not bg[4]:
                use_rect = pygame.Rect(200, y + 40, 120, 30)
                pygame.draw.rect(screen, (100, 200, 100), use_rect, border_radius=8)
                use_text = self.small_font.render("Использовать", True, (255, 255, 255))
                screen.blit(use_text, (use_rect.centerx - use_text.get_width()//2, 
                                     use_rect.centery - use_text.get_height()//2))
            
            y += 100

    def draw_exchange(self, screen, paws):
        exchange_text = self.font.render(f"Курс обмена: {self.exchange_rate} лапок = 1 монета", True, (50, 50, 50))
        screen.blit(exchange_text, (20, 150))
        
        max_exchange = paws // self.exchange_rate
        if max_exchange > 0:
            self.exchange_btn = pygame.Rect(30, 200, 340, 60)
            pygame.draw.rect(screen, (100, 149, 237), self.exchange_btn, border_radius=15)
            exchange_btn_text = self.font.render(f"Обменять {max_exchange * self.exchange_rate} → {max_exchange}", True, (255, 255, 255))
            screen.blit(exchange_btn_text, (40, 215))

    def handle_click(self, pos, coins, paws):
        result = {
            "coins": coins, 
            "paws": paws, 
            "multiplier": None, 
            "skin": None, 
            "background": None, 
            "close": False
        }
        
        if self.show_confirm:
            confirm_btn = pygame.Rect(70, 380, 120, 50)
            cancel_btn = pygame.Rect(210, 380, 120, 50)
            
            if confirm_btn.collidepoint(pos) and coins >= self.confirm_price:
                if self.confirm_type == "upgrade":
                    self.confirm_item[3] = True
                    self.db.update_upgrade(self.confirm_item[0], True)
                    result["coins"] = coins - self.confirm_price
                    result["multiplier"] = self.confirm_item[2]
                elif self.confirm_type == "skin":
                    self.confirm_item[3] = True
                    self.db.update_skin(self.confirm_item[0], True)
                    result["coins"] = coins - self.confirm_price
                elif self.confirm_type == "background":
                    self.confirm_item[3] = True
                    self.db.update_background(self.confirm_item[0], True)
                    result["coins"] = coins - self.confirm_price
            
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
            
        if self.categories[self.current_category] == "Улучшения":
            y = 150
            for upgrade in self.upgrades:
                item_rect = pygame.Rect(30, y, 340, 60)
                if item_rect.collidepoint(pos):
                    if not upgrade[3] and coins >= upgrade[1]:
                        self.show_confirm = True
                        self.confirm_item = upgrade
                        self.confirm_type = "upgrade"
                        self.confirm_price = upgrade[1]
                    elif upgrade[3] and not upgrade[4]:
                        for u in self.upgrades:
                            u[4] = False
                        upgrade[4] = True
                        self.db.update_upgrade(upgrade[0], True)
                        result["multiplier"] = upgrade[2]
                y += 80
                    
        elif self.categories[self.current_category] == "Скины":
            y = 150
            for skin in self.skins:
                item_rect = pygame.Rect(30, y, 340, 80)
                if item_rect.collidepoint(pos):
                    if not skin[3] and coins >= skin[1]:
                        self.show_confirm = True
                        self.confirm_item = skin
                        self.confirm_type = "skin"
                        self.confirm_price = skin[1]
                    elif skin[3] and not skin[4]:
                        for s in self.skins:
                            s[4] = False
                        skin[4] = True
                        self.db.update_skin(skin[0], True)
                        result["skin"] = skin[2]
                y += 100
                    
        elif self.categories[self.current_category] == "Фоны":
            y = 150
            for bg in self.backgrounds:
                item_rect = pygame.Rect(30, y, 340, 80)
                if item_rect.collidepoint(pos):
                    if not bg[3] and coins >= bg[1]:
                        self.show_confirm = True
                        self.confirm_item = bg
                        self.confirm_type = "background"
                        self.confirm_price = bg[1]
                    elif bg[3] and not bg[4]:
                        for b in self.backgrounds:
                            b[4] = False
                        bg[4] = True
                        self.db.update_background(bg[0], True)
                        result["background"] = bg[2]
                y += 100
                    
        elif self.categories[self.current_category] == "Обмен":
            max_exchange = paws // self.exchange_rate
            if max_exchange > 0:
                exchange_btn = pygame.Rect(30, 200, 340, 60)
                if exchange_btn.collidepoint(pos):
                    result["coins"] = coins + max_exchange
                    result["paws"] = paws - (max_exchange * self.exchange_rate)
                    
        return result 