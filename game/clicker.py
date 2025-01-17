import pygame

class Clicker:
    def __init__(self):
        self.cat_image = pygame.image.load("assets\sprites\cat.png")
        self.cat_image = pygame.transform.scale(self.cat_image, (200, 200))
        self.cat_rect = self.cat_image.get_rect(center=(200, 350))
        
        self.paw_image = pygame.image.load("assets\sprites\paw.png")
        self.paw_image = pygame.transform.scale(self.paw_image, (30, 30))
        
        self.coin_image = pygame.image.load("assets\sprites\coin.png")
        self.coin_image = pygame.transform.scale(self.coin_image, (30, 30))
        
        self.shop_image = pygame.image.load("assets\sprites\shop_sign.png")
        self.shop_image = pygame.transform.scale(self.shop_image, (1024, 600))
        
        self.cat_animation = False
        self.cat_scale = 1.0
        
        self.shop_animation = False
        self.shop_scale = 1.0
        
        self.clicks = 0
        self.coins = 0
        
        self.font = pygame.font.Font(None, 36)
        self.plus_animations = []
        
        self.shop_rect = pygame.Rect(0, 500, 400, 200)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.cat_rect.collidepoint(event.pos):
                self.clicks += 1
                self.cat_animation = True
                self.cat_scale = 0.9
                self.plus_animations.append([event.pos[0], event.pos[1], 255])
            elif self.shop_rect.collidepoint(event.pos):
                self.shop_animation = True
                self.shop_scale = 0.9

    def update(self):
        if self.cat_animation:
            self.cat_scale += 0.02
            if self.cat_scale >= 1.0:
                self.cat_scale = 1.0
                self.cat_animation = False
                
        if self.shop_animation:
            self.shop_scale += 0.02
            if self.shop_scale >= 1.0:
                self.shop_scale = 1.0
                self.shop_animation = False
        
        for anim in self.plus_animations[:]:
            anim[1] -= 1
            anim[2] -= 5 
            if anim[2] <= 0:
                self.plus_animations.remove(anim)

    def draw(self, screen):
        scaled_cat = pygame.transform.scale(
            self.cat_image,
            (int(200 * self.cat_scale),
             int(200 * self.cat_scale))
        )
        scaled_rect = scaled_cat.get_rect(center=self.cat_rect.center)
        screen.blit(scaled_cat, scaled_rect)
        
        # монетки
        coin_rect = self.coin_image.get_rect(topleft=(20, 20))
        screen.blit(self.coin_image, coin_rect)
        coins_text = self.font.render(f"{self.coins}", True, (0, 0, 0))
        screen.blit(coins_text, (coin_rect.right + 10, 20))
        
        # отображение лапок
        paw_rect = self.paw_image.get_rect(topleft=(20, coin_rect.bottom + 10))
        screen.blit(self.paw_image, paw_rect)
        clicks_text = self.font.render(f"{self.clicks}", True, (0, 0, 0))
        screen.blit(clicks_text, (paw_rect.right + 10, paw_rect.top))
        
        # +1 при тыке
        for anim in self.plus_animations:
            plus_text = self.font.render("+1", True, (0, 0, 0))
            plus_text.set_alpha(anim[2])
            screen.blit(plus_text, (anim[0], anim[1]))
        
        scaled_shop = pygame.transform.scale(
            self.shop_image,
            (int(400 * self.shop_scale),
             int(200 * self.shop_scale))
        )
        scaled_shop_rect = scaled_shop.get_rect(center=self.shop_rect.center)
        screen.blit(scaled_shop, scaled_shop_rect)