import json
from pathlib import Path

# менеджер для работы с сохранениями и загрузкой данных
class DataManager:
    def __init__(self):
        # пути к файлам данных
        self.player_file = Path("game/data/player.json")
        self.upgrades_file = Path("game/data/upgrades.json")
        self.skins_file = Path("game/data/skins.json")
        self.backgrounds_file = Path("game/data/backgrounds.json")
        
        self.data_path = Path("game/data")
        self.data_path.mkdir(exist_ok=True)
        
        self.init_data()
        self.show_grid = False
        self.console_enabled = True
    
    def init_data(self):
        if not self.player_file.exists():
            player_data = {
                "clicks": 0,
                "coins": 0,
                "multiplier": 1,
                "active_skin": "assets/sprites/cats/cat_gray.png",
                "active_background": "assets/sprites/backgrounds/bg_village.jpeg",
                "debug": {
                    "grid_enabled": False,
                    "console_enabled": True
                }
            }
            self.save_json(self.player_file, player_data)
        
        if not self.upgrades_file.exists():
            upgrades_data = {
                "upgrades": [
                    {
                        "name": "Мягкие лапки",
                        "price": 100,
                        "multiplier": 2,
                        "purchased": False,
                        "active": False
                    },
                    {
                        "name": "Острые когти",
                        "price": 500,
                        "multiplier": 5,
                        "purchased": False,
                        "active": False
                    },
                    {
                        "name": "Кошачья сила",
                        "price": 2000,
                        "multiplier": 10,
                        "purchased": False,
                        "active": False
                    },
                    {
                        "name": "Мощь тигра",
                        "price": 10000,
                        "multiplier": 50,
                        "purchased": False,
                        "active": False
                    },
                    {
                        "name": "Космический кот",
                        "price": 50000,
                        "multiplier": 100,
                        "purchased": False,
                        "active": False
                    }
                ]
            }
            self.save_json(self.upgrades_file, upgrades_data)
        
        if not self.skins_file.exists():
            skins_data = {
                "skins": [
                    {
                        "name": "Серый кот",
                        "price": 0,
                        "path": "assets/sprites/cats/cat_gray.png",
                        "purchased": True,
                        "active": True
                    },
                    {
                        "name": "Рыжий котик",
                        "price": 1000,
                        "path": "assets/sprites/cats/cat_orange.png",
                        "purchased": False,
                        "active": False
                    },
                    {
                        "name": "Чёрный кот",
                        "price": 2000,
                        "path": "assets/sprites/cats/cat_black.png",
                        "purchased": False,
                        "active": False
                    },
                    {
                        "name": "Белая кошка",
                        "price": 3000,
                        "path": "assets/sprites/cats/cat_white.png",
                        "purchased": False,
                        "active": False
                    },
                    {
                        "name": "Сиамский кот",
                        "price": 7500,
                        "path": "assets/sprites/cats/cat_siamese.png",
                        "purchased": False,
                        "active": False
                    },
                    {
                        "name": "Персидский кот",
                        "price": 10000,
                        "path": "assets/sprites/cats/cat_persian.png",
                        "purchased": False,
                        "active": False
                    },
                    {
                        "name": "Nyan Cat",
                        "price": 50000,
                        "path": "assets/sprites/cats/cat_nyan.png",
                        "purchased": False,
                        "active": False
                    },
                    {
                        "name": "Хлебный кот",
                        "price": 100000,
                        "path": "assets/sprites/cats/cat_bread.gif",
                        "purchased": False,
                        "active": False,
                        "animated": True
                    }
                ]
            }
            self.save_json(self.skins_file, skins_data)
        
        if not self.backgrounds_file.exists():
            backgrounds_data = {
                "backgrounds": [
                    {
                        "name": "Родная деревня",
                        "price": 0,
                        "path": "assets/sprites/backgrounds/bg_village.jpeg",
                        "purchased": True,
                        "active": True
                    },
                    {
                        "name": "Ночной сад",
                        "price": 2000,
                        "path": "assets/sprites/backgrounds/bg_night.jpeg",
                        "purchased": False,
                        "active": False
                    },
                    {
                        "name": "Уютная комната",
                        "price": 2000,
                        "path": "assets/sprites/backgrounds/bg_room.jpeg",
                        "purchased": False,
                        "active": False
                    },
                    {
                        "name": "Цветущий сад",
                        "price": 2000,
                        "path": "assets/sprites/backgrounds/bg_garden.jpeg",
                        "purchased": False,
                        "active": False
                    },
                    {
                        "name": "Утренний Монштадт",
                        "price": 3000,
                        "path": "assets/sprites/backgrounds/bg_morning.jpeg",
                        "purchased": False,
                        "active": False
                    },
                    {
                        "name": "Вечерний Киото",
                        "price": 4000,
                        "path": "assets/sprites/backgrounds/bg_evening.jpeg",
                        "purchased": False,
                        "active": False
                    }
                ]
            }
            self.save_json(self.backgrounds_file, backgrounds_data)
        
        if not Path("game/data/music.json").exists():
            music_data = {
                "music": [
                    {
                        "name": "Shufladka",
                        "price": 0,
                        "path": "assets/music/main_theme.mp3",
                        "purchased": True,
                        "active": True
                    },
                    {
                        "name": "Без музыки",
                        "price": 0,
                        "path": "",
                        "purchased": True,
                        "active": False
                    },
                    {
                        "name": "Nyan Cat",
                        "price": 25000,
                        "path": "assets/music/nyan_theme.mp3",
                        "purchased": False,
                        "active": False
                    }
                ]
            }
            self.save_json(Path("game/data/music.json"), music_data)

    def save_json(self, file_path, data):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_game_state(self):
        data = self.load_json(self.player_file)
        # Загружаем состояния отладки
        debug_data = data.get("debug", {"grid_enabled": False, "console_enabled": True})
        self.show_grid = debug_data["grid_enabled"]
        self.console_enabled = debug_data["console_enabled"]
        return (
            data["clicks"],
            data["coins"],
            data["multiplier"],
            data["active_skin"],
            data["active_background"]
        )
    
    def save_game_state(self, clicks, coins, multiplier, active_skin=None, active_background=None):
        data = {
            "clicks": clicks,
            "coins": coins,
            "multiplier": multiplier,
            "active_skin": active_skin or self.load_game_state()[3],
            "active_background": active_background or self.load_game_state()[4],
            "debug": {
                "grid_enabled": self.show_grid,
                "console_enabled": self.console_enabled
            }
        }
        self.save_json(self.player_file, data)
    
    def load_upgrades(self):
        data = self.load_json(self.upgrades_file)
        return [[u["name"], u["price"], u["multiplier"], u["purchased"], u["active"]] 
                for u in data["upgrades"]]
    
    def update_upgrade(self, name, purchased, active=False):
        data = self.load_json(self.upgrades_file)
        
        if active:
            for upgrade in data["upgrades"]:
                upgrade["active"] = False
        
            current_state = self.load_game_state()
            for upgrade in data["upgrades"]:
                if upgrade["name"] == name:
                    self.save_game_state(
                        current_state[0],
                        current_state[1],
                        upgrade["multiplier"]
                    )
                    break
        
        for upgrade in data["upgrades"]:
            if upgrade["name"] == name:
                upgrade["purchased"] = purchased
                upgrade["active"] = active
        
        self.save_json(self.upgrades_file, data)
    
    def load_skins(self):
        data = self.load_json(self.skins_file)
        return [[s["name"], s["price"], s["path"], s["purchased"], s["active"]] 
                for s in data["skins"]]
    
    def update_skin(self, name, purchased, active=False):
        data = self.load_json(self.skins_file)
        
        if active:
            for skin in data["skins"]:
                skin["active"] = False
        
            current_state = self.load_game_state()
            for skin in data["skins"]:
                if skin["name"] == name:
                    self.save_game_state(
                        current_state[0],
                        current_state[1],
                        current_state[2],
                        skin["path"],
                        current_state[4]
                    )
                    break
        
        for skin in data["skins"]:
            if skin["name"] == name:
                skin["purchased"] = purchased
                skin["active"] = active
        
        self.save_json(self.skins_file, data)
    
    def load_backgrounds(self):
        data = self.load_json(self.backgrounds_file)
        return [[b["name"], b["price"], b["path"], b["purchased"], b["active"]] 
                for b in data["backgrounds"]]
    
    def update_background(self, name, purchased, active=False):
        data = self.load_json(self.backgrounds_file)
        
        if active:
            for bg in data["backgrounds"]:
                bg["active"] = False
        
            current_state = self.load_game_state()
            for bg in data["backgrounds"]:
                if bg["name"] == name:
                    self.save_game_state(
                        current_state[0],
                        current_state[1],
                        current_state[2],
                        current_state[3],
                        bg["path"]
                    )
                    break
        
        for bg in data["backgrounds"]:
            if bg["name"] == name:
                bg["purchased"] = purchased
                bg["active"] = active
        
        self.save_json(self.backgrounds_file, data)

    def save_all_unlocked(self):
        # Разблокируем все улучшения
        upgrades_data = self.load_json(self.upgrades_file)
        for upgrade in upgrades_data["upgrades"]:
            upgrade["purchased"] = True
        self.save_json(self.upgrades_file, upgrades_data)
        
        # Разблокируем все скины
        skins_data = self.load_json(self.skins_file)
        for skin in skins_data["skins"]:
            skin["purchased"] = True
        self.save_json(self.skins_file, skins_data)
        
        # Разблокируем все фоны
        backgrounds_data = self.load_json(self.backgrounds_file)
        for bg in backgrounds_data["backgrounds"]:
            bg["purchased"] = True
        self.save_json(self.backgrounds_file, backgrounds_data)

    def save_all_locked(self):
        # Сбрасываем все улучшения
        upgrades_data = self.load_json(self.upgrades_file)
        for upgrade in upgrades_data["upgrades"]:
            upgrade["purchased"] = False
            upgrade["active"] = False
        self.save_json(self.upgrades_file, upgrades_data)
        
        # Сбрасываем все скины, кроме базового
        skins_data = self.load_json(self.skins_file)
        for skin in skins_data["skins"]:
            if skin["name"] != "Серый кот":
                skin["purchased"] = False
                skin["active"] = False
            else:
                skin["active"] = True
        self.save_json(self.skins_file, skins_data)
        
        # Сбрасываем все фоны, кроме базового
        backgrounds_data = self.load_json(self.backgrounds_file)
        for bg in backgrounds_data["backgrounds"]:
            if bg["name"] != "Родная деревня":
                bg["purchased"] = False
                bg["active"] = False
            else:
                bg["active"] = True
        self.save_json(self.backgrounds_file, backgrounds_data)

    def load_music(self):
        data = self.load_json(Path("game/data/music.json"))
        return [[m["name"], m["price"], m["path"], m["purchased"], m["active"]] 
                for m in data["music"]]

    def update_music(self, name, purchased, active=False):
        data = self.load_json(Path("game/data/music.json"))
        
        if active:
            for music in data["music"]:
                music["active"] = False
        
        for music in data["music"]:
            if music["name"] == name:
                music["purchased"] = purchased
                music["active"] = active
        
        self.save_json(Path("game/data/music.json"), data)

    def load_match3_progress(self):
        match3_file = self.data_path / "match3_progress.json"
        if not match3_file.exists():
            return None
        with open(match3_file, 'r') as f:
            data = json.load(f)
            return data.get("unlocked_levels", 1)

    def save_match3_progress(self, unlocked_levels):
        match3_file = self.data_path / "match3_progress.json"
        data = {"unlocked_levels": unlocked_levels}
        with open(match3_file, 'w') as f:
            json.dump(data, f)

    def reset_progress(self):
        # Удаляем все файлы сохранений
        for file in self.data_path.glob("*.json"):
            file.unlink()
        # Инициализируем данные заново
        self.init_data() 

    def toggle_grid(self):
        self.show_grid = not self.show_grid
        # Сохраняем состояние в player.json
        data = self.load_json(self.player_file)
        data["debug"]["grid_enabled"] = self.show_grid
        self.save_json(self.player_file, data)
        return self.show_grid

    def get_grid_state(self):
        # Всегда читаем актуальное состояние из файла
        data = self.load_json(self.player_file)
        self.show_grid = data["debug"]["grid_enabled"]
        return self.show_grid 