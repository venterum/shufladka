import pygame

class Clicker:
    def __init__(self):
        self.cat_image = pygame.image.load("cat.png")
        self.cat_rect = self.cat_image.get_rect(center=(200, 350))
        
        self.click_animation = False
        self.click_scale = 1.0
        
        self.clicks = 0
        
        self.font = pygame.font.Font(None, 36)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.cat_rect.collidepoint(event.pos):
                self.clicks += 1
                self.click_animation = True
                self.click_scale = 0.9

    def update(self):
        if self.click_animation:
            self.click_scale += 0.02
            if self.click_scale >= 1.0:
                self.click_scale = 1.0
                self.click_animation = False

    def draw(self, screen):
        scaled_cat = pygame.transform.scale(
            self.cat_image,
            (int(self.cat_rect.width * self.click_scale),
             int(self.cat_rect.height * self.click_scale))
        )
        scaled_rect = scaled_cat.get_rect(center=self.cat_rect.center)
        screen.blit(scaled_cat, scaled_rect)
        
        clicks_text = self.font.render(f"Клики: {self.clicks}", True, (0, 0, 0))
        screen.blit(clicks_text, (20, 20)) 