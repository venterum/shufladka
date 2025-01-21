import csv
from pathlib import Path

class DataManager:
    def __init__(self):
        self.data_path = Path("game/data")
        self.data_path.mkdir(exist_ok=True)
        
        self.player_file = self.data_path / "player.csv"
        self.upgrades_file = self.data_path / "upgrades.csv"
        self.skins_file = self.data_path / "skins.csv"
        self.backgrounds_file = self.data_path / "backgrounds.csv"
        
        self.init_data()
    
    def init_data(self):
        if not self.player_file.exists():
            with open(self.player_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['clicks', 'coins', 'multiplier', 'active_skin', 'active_background'])
                writer.writerow([0, 0, 1, 'assets/sprites/cats/cat_gray.png', 'assets/sprites/backgrounds/bg_village.jpeg'])
        
        if not self.upgrades_file.exists():
            with open(self.upgrades_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['name', 'price', 'multiplier', 'purchased', 'active'])
                upgrades = [
                    ["Мягкие лапки", 100, 2, "False", "False"],
                    ["Острые когти", 500, 5, "False", "False"],
                    ["Кошачья сила", 2000, 10, "False", "False"],
                    ["Мощь тигра", 10000, 50, "False", "False"],
                    ["Космический кот", 50000, 100, "False", "False"],
                    ["Легендарный мурлык", 100000, 200, "False", "False"]
                ]
                writer.writerows(upgrades)
        
        if not self.skins_file.exists():
            with open(self.skins_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['name', 'price', 'path', 'purchased', 'active'])
                skins = [
                    ["Серый кот", 0, "assets/sprites/cats/cat_gray.png", "True", "True"],
                    ["Рыжий котик", 1000, "assets/sprites/cats/cat_orange.png", "False", "False"],
                    ["Чёрный кот", 2000, "assets/sprites/cats/cat_black.png", "False", "False"],
                    ["Белая кошка", 3000, "assets/sprites/cats/cat_white.png", "False", "False"],
                    ["Сиамский кот", 7500, "assets/sprites/cats/cat_siamese.png", "False", "False"],
                    ["Персидский кот", 10000, "assets/sprites/cats/cat_persian.png", "False", "False"]
                ]
                writer.writerows(skins)
        
        if not self.backgrounds_file.exists():
            with open(self.backgrounds_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['name', 'price', 'path', 'purchased', 'active'])
                backgrounds = [
                    ["Родная деревня", 0, "assets/sprites/backgrounds/bg_village.jpeg", "True", "True"],
                    ["Ночной сад", 2000, "assets/sprites/backgrounds/bg_night.jpeg", "False", "False"],
                    ["Уютная комната", 2000, "assets/sprites/backgrounds/bg_room.jpeg", "False", "False"],
                    ["Цветущий сад", 2000, "assets/sprites/backgrounds/bg_garden.jpeg", "False", "False"],
                    ["Утренний Монштадт", 3000, "assets/sprites/backgrounds/bg_morning.jpeg", "False", "False"],
                    ["Вечерний Киото", 4000, "assets/sprites/backgrounds/bg_evening.jpeg", "False", "False"]
                ]
                writer.writerows(backgrounds)
    
    def load_game_state(self):
        with open(self.player_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = next(reader)
            return (
                int(data['clicks']),
                int(data['coins']),
                int(data['multiplier']),
                data['active_skin'],
                data['active_background']
            )
    
    def save_game_state(self, clicks, coins, multiplier, active_skin=None, active_background=None):
        data = self.load_game_state()
        with open(self.player_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['clicks', 'coins', 'multiplier', 'active_skin', 'active_background'])
            writer.writerow([
                clicks,
                coins,
                multiplier,
                active_skin if active_skin else data[3],
                active_background if active_background else data[4]
            ])
    
    def load_upgrades(self):
        upgrades = []
        with open(self.upgrades_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                upgrades.append([
                    row['name'],
                    int(row['price']),
                    int(row['multiplier']),
                    row['purchased'].lower() == 'true',
                    row['active'].lower() == 'true'
                ])
        return upgrades
    
    def update_upgrade(self, name, purchased, active=False):
        upgrades = []
        with open(self.upgrades_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            upgrades = list(reader)
        
        if active:
            for upgrade in upgrades:
                upgrade['active'] = 'False'
        
            current_state = self.load_game_state()
            self.save_game_state(
                current_state[0],
                current_state[1],
                int(next(u['multiplier'] for u in upgrades if u['name'] == name))
            )
        else:
            current_state = self.load_game_state()
            self.save_game_state(
                current_state[0],
                current_state[1],
                current_state[2]
            )
        
        for upgrade in upgrades:
            if upgrade['name'] == name:
                upgrade['purchased'] = str(purchased)
                upgrade['active'] = str(active)
        
        with open(self.upgrades_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'price', 'multiplier', 'purchased', 'active'])
            writer.writeheader()
            writer.writerows(upgrades)
    
    def load_skins(self):
        skins = []
        with open(self.skins_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                skins.append([
                    row['name'],
                    int(row['price']),
                    row['path'],
                    row['purchased'].lower() == 'true',
                    row['active'].lower() == 'true'
                ])
        return skins
    
    def update_skin(self, name, purchased, active=False):
        skins = []
        with open(self.skins_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            skins = list(reader)
        
        if active:
            for skin in skins:
                skin['active'] = 'False'
        
            current_state = self.load_game_state()
            self.save_game_state(
                current_state[0],
                current_state[1],
                current_state[2],
                next(s['path'] for s in skins if s['name'] == name),
                current_state[4]
            )
        else:
            current_state = self.load_game_state()
            self.save_game_state(
                current_state[0],
                current_state[1],
                current_state[2]
            )
        
        for skin in skins:
            if skin['name'] == name:
                skin['purchased'] = str(purchased)
                skin['active'] = str(active)
        
        with open(self.skins_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'price', 'path', 'purchased', 'active'])
            writer.writeheader()
            writer.writerows(skins)
    
    def load_backgrounds(self):
        backgrounds = []
        with open(self.backgrounds_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                backgrounds.append([
                    row['name'],
                    int(row['price']),
                    row['path'],
                    row['purchased'].lower() == 'true',
                    row['active'].lower() == 'true'
                ])
        return backgrounds
    
    def update_background(self, name, purchased, active=False):
        backgrounds = []
        with open(self.backgrounds_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            backgrounds = list(reader)
        
        if active:
            for bg in backgrounds:
                bg['active'] = 'False'
        
            current_state = self.load_game_state()
            self.save_game_state(
                current_state[0],
                current_state[1],
                current_state[2],
                current_state[3],
                next(b['path'] for b in backgrounds if b['name'] == name)
            )
        else:
            current_state = self.load_game_state()
            self.save_game_state(
                current_state[0],
                current_state[1],
                current_state[2]
            )
        
        for bg in backgrounds:
            if bg['name'] == name:
                bg['purchased'] = str(purchased)
                bg['active'] = str(active)
        
        with open(self.backgrounds_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'price', 'path', 'purchased', 'active'])
            writer.writeheader()
            writer.writerows(backgrounds) 