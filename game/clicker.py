import pygame
from game.data_manager import DataManager
from game.shop import Shop
from pathlib import Path

class Clicker:
    def __init__(self):
        self.db = DataManager()
        game_state = self.db.load_game_state()
        self.clicks = game_state[0]
        self.coins = game_state[1]
        self.click_multiplier = game_state[2]
        active_skin = game_state[3]
        active_background = game_state[4]
        
        assets_path = Path("assets")
        sprites_path = assets_path / "sprites"
        fonts_path = assets_path / "fonts"
        
        bg = pygame.image.load(active_background)
        bg_rect = bg.get_rect()
        crop_rect = pygame.Rect(
            (bg_rect.width - 400) // 2,
            (bg_rect.height - 700) // 2,
            400, 700
        )
        self.background = bg.subsurface(crop_rect)
        
        self.cat_image = pygame.image.load(active_skin)
        self.cat_image = pygame.transform.scale(self.cat_image, (200, 200))
        self.cat_rect = self.cat_image.get_rect(center=(200, 350))
        
        self.paw_image = pygame.image.load(sprites_path / "paw.png")
        self.paw_image = pygame.transform.scale(self.paw_image, (30, 30))
        
        self.coin_image = pygame.image.load(sprites_path / "coin.png")
        self.coin_image = pygame.transform.scale(self.coin_image, (30, 30))
        
        self.shop_image = pygame.image.load(sprites_path / "shop_sign.png")
        self.shop_image = pygame.transform.scale(self.shop_image, (400, 200))
        
        self.cat_animation = False
        self.cat_scale = 1.0
        self.shop_scale = 1.0
        
        self.font = pygame.font.Font(fonts_path / "Tiny5-Regular.ttf", 24)
        self.plus_animations = []
        
        self.shop_rect = pygame.Rect(0, 500, 400, 200)
        self.shop = Shop(self.db)
        self.in_shop = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.in_shop:
                result = self.shop.handle_click(event.pos, self.coins, self.clicks)
                self.coins = result["coins"]
                self.clicks = result["paws"]
                
                if result.get("multiplier"):
                    self.click_multiplier = result["multiplier"]
                
                if result.get("skin"):
                    self.cat_image = pygame.image.load(result["skin"])
                    self.cat_image = pygame.transform.scale(self.cat_image, (200, 200))
                
                if result.get("background"):
                    bg = pygame.image.load(result["background"])
                    bg_rect = bg.get_rect()
                    crop_rect = pygame.Rect(
                        (bg_rect.width - 400) // 2,
                        (bg_rect.height - 700) // 2,
                        400, 700
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

    def update(self):
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
        if self.in_shop:
            self.shop.draw(screen, self.coins, self.clicks)
        else:
            screen.blit(self.background, (0, 0))
            
            scaled_cat = pygame.transform.scale(
                self.cat_image,
                (int(200 * self.cat_scale),
                 int(200 * self.cat_scale))
            )
            scaled_rect = scaled_cat.get_rect(center=self.cat_rect.center)
            screen.blit(scaled_cat, scaled_rect)
            
            coin_rect = self.coin_image.get_rect(topleft=(20, 20))
            screen.blit(self.coin_image, coin_rect)
            coins_text = self.font.render(f"{self.coins}", True, (255, 255, 255))
            screen.blit(coins_text, (coin_rect.right + 10, 20))
            
            paw_rect = self.paw_image.get_rect(topleft=(20, coin_rect.bottom + 10))
            screen.blit(self.paw_image, paw_rect)
            clicks_text = self.font.render(f"{self.clicks}", True, (255, 255, 255))
            screen.blit(clicks_text, (paw_rect.right + 10, paw_rect.top))
            
            for anim in self.plus_animations:
                plus_text = self.font.render(f"+{anim[3]}", True, (255, 255, 255))
                plus_text.set_alpha(anim[2])
                screen.blit(plus_text, (anim[0], anim[1]))
            
            scaled_shop = pygame.transform.scale(
                self.shop_image,
                (int(400 * self.shop_scale),
                 int(200 * self.shop_scale))
            )
            scaled_shop_rect = scaled_shop.get_rect(center=self.shop_rect.center)
            screen.blit(scaled_shop, scaled_shop_rect)