import arcade
import random
import math
import pandas as pd

window_width = 800
window_height = 700
title = "Flight Combat"

title_font = "Kenney Future"
default_font = "Kenney Pixel"
score_font = "Kenney Mini Square"

BACKGROUND_COLOR = arcade.color.BLUE_SAPPHIRE
PANEL_COLOR = (0, 0, 0, 200)
TEXT_COLOR = arcade.color.WHITE
ACCENT_COLOR = arcade.color.GOLD
DANGER_COLOR = arcade.color.RED

keys = {
    "LEFT": False,
    "RIGHT": False,
    "UP":False,
    "DOWN":False,
}

class BulletEnemy():
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y - 25
        self.radius = 5
        self.speed = 1
        
        self.damage = 1
        self.points = 100
        
        self.width = self.radius * 2
        self.height = self.radius * 2
        self.bullet_texture = arcade.load_texture("imgs/bala_enemiga.png")
        
        self.angle = math.atan2(target_y - y, target_x - x)
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed

    def calculate_speed(self, lvl):
        speed_chosee = {
            "1": 10,
            "2": 9,
            "3": 8,
            "4": 8,
            "5": 7,
            "6": 7,
            "7": 6,
            "8": 6,
            "9": 5,
        }
        self.speed = speed_chosee[str(lvl)]
        self.angle = math.atan2(self.dy, self.dx)
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        arcade.draw_texture_rect(
            self.bullet_texture,
            arcade.rect.XYWH(self.x, self.y, self.width, self.height)
        )

    def off_screen(self):
        return self.y < 0 or self.y > window_height or self.x < 0 or self.x > window_width

    def hit(self, player):
        player_left = player.x - player.width / 2
        player_right = player.x + player.width / 2
        player_bottom = player.y - player.height / 2
        player_top = player.y + player.height / 2

        closest_x = max(player_left, min(self.x, player_right))
        closest_y = max(player_bottom, min(self.y, player_top))

        distance = math.hypot(self.x - closest_x, self.y - closest_y)

        return distance < self.radius

    
class Player:
    def __init__(self):
        self.x = window_width // 2
        self.y = 40
        self.image = arcade.load_texture("imgs/avion_player.png")
        self.width = 50  
        self.height = 50
        self.speed = 6  

        self.lives = 3
        self.score = 0

    def draw(self):
        arcade.draw_texture_rect(self.image, arcade.rect.XYWH(self.x, self.y, self.width, self.height))

    def move(self):
        if keys["LEFT"] and self.x - self.width/2 > 200:
            self.x -= self.speed 
        elif keys["RIGHT"] and self.x + self.width/2 < 600:
            self.x += self.speed

        if keys["UP"] and window_height > self.y + self.height/2:
            self.y += self.speed
        elif keys["DOWN"] and self.y > self.height / 2:
            self.y -= self.speed


class Enemy():
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.width = 50
        self.height = 50
        self.speed = 5   

        self.damage = 1
        self.points = 200
        
        self.enemy_texture = arcade.load_texture("imgs/avion_enemy.png")

    def draw(self):
        arcade.draw_texture_rect(
            self.enemy_texture,
            arcade.rect.XYWH(self.x, self.y, self.width, self.height)
        )

    def move(self):
        self.y -= self.speed

    def off_screen(self):
        return self.y < -self.height

    def shoot(self, target_x, target_y):
        return BulletEnemy(self.x, self.y, target_x, target_y)

    def collision(self, player: Player):
        enemy_left = self.x - self.width // 2
        enemy_right = self.x + self.width // 2
        enemy_top = self.y + self.height // 2
        enemy_bottom = self.y - self.height // 2

        player_left = player.x - player.width // 2
        player_right = player.x + player.width // 2
        player_top = player.y + player.height // 2
        player_bottom = player.y - player.height // 2

        return not (
            enemy_right < player_left or
            enemy_left > player_right or
            enemy_top < player_bottom or
            enemy_bottom > player_top
        )


class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y + 25

        self.width = 5
        self.height = 10
        
        self.speed = 7

        self.bullet_texture = arcade.load_texture("imgs/bala.png")

    def draw(self):
        arcade.draw_texture_rect(
            self.bullet_texture,
            arcade.rect.XYWH(self.x, self.y, self.width, self.height)
        )

    def move(self):
        self.y += self.speed

    def off_screen(self):
        return self.y > window_height + self.height

    def hit(self, enemy: Enemy):
        extra = 20
        enemy_left = enemy.x - extra
        enemy_right = enemy.x + enemy.width - extra
        enemy_bottom = enemy.y
        enemy_top = enemy.y + enemy.height

        bullet_left = self.x
        bullet_right = self.x + self.width
        bullet_bottom = self.y
        bullet_top = self.y + self.height

        return (bullet_right > enemy_left and
                bullet_left < enemy_right and
                bullet_top > enemy_bottom and
                bullet_bottom < enemy_top)


class ScoreView(arcade.View):
    def __init__(self, score, player_name):
        super().__init__()
        self.scores = []
        self.score = score
        self.player_name = player_name

        self.BUTTON_WIDTH = 200
        self.BUTTON_HEIGHT = 40
        self.button_x = window_width // 2 - self.BUTTON_WIDTH // 2
        self.button_y = 50

    def setup(self):
        try:
            df = pd.read_csv("scores.csv")
            existing_scores = df.values.tolist()
        except (FileNotFoundError, pd.errors.EmptyDataError):
            existing_scores = []
        
        score_exists = any(name == self.player_name and score == self.score for name, score in existing_scores)
        
        if not score_exists and (len(existing_scores) < 10 or self.score > min([score[1] for score in existing_scores], default=0)):
            existing_scores.append([self.player_name, self.score])
        
        self.scores = sorted(existing_scores, key=lambda x: x[1], reverse=True)[:10]
        
        pd.DataFrame(self.scores, columns=["Nombre", "Puntaje"]).to_csv("scores.csv", index=False)

    def on_show(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_draw(self):
        self.clear()
        arcade.draw_text("TOP 10 PUNTAJES", window_width // 2, window_height - 50,
                         arcade.color.WHITE, font_size=24, anchor_x="center")

        y = window_height - 100
        arcade.draw_text("#", window_width // 2 - 200, y, arcade.color.YELLOW, 16, anchor_x="center")
        arcade.draw_text("Jugador", window_width // 2 - 100, y, arcade.color.YELLOW, 16, anchor_x="center")
        arcade.draw_text("Puntaje", window_width // 2 + 100, y, arcade.color.YELLOW, 16, anchor_x="center")

        for i, (name, score) in enumerate(self.scores):
            y -= 30
            color = ACCENT_COLOR if name == self.player_name and score == self.score else TEXT_COLOR
            
            arcade.draw_text(f"{i+1}.", window_width // 2 - 200, y, color, 14, anchor_x="center")
            arcade.draw_text(name, window_width // 2 - 100, y, color, 14, anchor_x="center")
            arcade.draw_text(str(score), window_width // 2 + 100, y, color, 14, anchor_x="center")

        arcade.draw_rect_filled(
            arcade.rect.XYWH(window_width // 2, self.button_y + self.BUTTON_HEIGHT // 2,
                            self.BUTTON_WIDTH, self.BUTTON_HEIGHT),
            arcade.color.GRAY
        )
        arcade.draw_text("Volver", window_width // 2, self.button_y + 10,
                         arcade.color.WHITE, font_size=18, anchor_x="center")

        if len(self.scores) == 10 and self.score <= min(score[1] for score in self.scores):
            arcade.draw_text(f"Tu puntaje de {self.score} no entró en el top 10",
                           window_width // 2, 120,
                           DANGER_COLOR, font_size=16, anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        if (self.button_x <= x <= self.button_x + self.BUTTON_WIDTH and
                self.button_y <= y <= self.button_y + self.BUTTON_HEIGHT):
            game_over_view = GameOver(self.window, score=self.score, player_name=self.player_name)
            self.window.show_view(game_over_view)


class GameOver(arcade.View):
    def __init__(self, window, score, player_name):
        super().__init__(window)
        self.background = arcade.load_texture("imgs/game_over_bg.png")
        self.score = score
        self.player_name = player_name

    def on_draw(self):
        self.clear()
        
        if self.background:
            arcade.draw_texture_rect(self.background, arcade.rect.XYWH(window_width // 2, window_height // 2, window_width, window_height))
        
        arcade.draw_rect_filled(arcade.rect.XYWH(window_width // 2, window_height // 2, window_width - 100, window_height - 100),PANEL_COLOR)
        
        arcade.draw_text("GAME OVER", window_width // 2, window_height // 2 + 50,
                         DANGER_COLOR, font_size=48, font_name=title_font, anchor_x="center",
                         bold=True)
        
        arcade.draw_text(f"Jugador: {self.player_name}", window_width // 2, window_height // 2,
                         TEXT_COLOR, font_size=24, font_name=default_font, anchor_x="center")
        
        arcade.draw_text(f"Puntuación: {self.score}", window_width // 2, window_height // 2 - 40,
                         ACCENT_COLOR, font_size=36, font_name=score_font, anchor_x="center")
        
        arcade.draw_text("Presiona 'R' para Reiniciar", window_width // 2,
                         window_height // 2 - 100, TEXT_COLOR, font_size=20, 
                         font_name=default_font, anchor_x="center")
    
        arcade.draw_text("Presiona 'Q' para ver los scores", window_width // 2,
                         window_height // 2 - 140, TEXT_COLOR, font_size=20,
                         font_name=default_font, anchor_x="center")
        
        arcade.draw_text("Presiona 'ESC' para salir", window_width // 2,
                         window_height // 2 - 180, TEXT_COLOR, font_size=20,
                         font_name=default_font, anchor_x="center")

    def on_key_release(self, key, modifiers):
        if key == arcade.key.R:
            for key in keys:
                keys[key] = False
            self.window.show_view(GameView(self.player_name))
        elif key == arcade.key.ESCAPE:
            arcade.close_window()
        elif key == arcade.key.Q:
            score_view = ScoreView(self.score, self.player_name)
            score_view.setup()
            self.window.show_view(score_view)


class GameView(arcade.View):
    def __init__(self, player_name="Jugador"):
        super().__init__()
        self.background = arcade.load_texture("imgs/mar_bg.png") 
        self.player_name = player_name
        
        self.player = Player()
        self.enemys_list = []
        self.bullet_enemy_list = []
        self.bullet_player_list = []

        self.controll_time_show_enemys = 2
        self.controll_time_shoot_enemy = 2
        self.time_show_enemys = 0
        self.time_shoot_enemy = 0

        self.dead = True
        self.position_lives = (30, 90, 160)
        
        self.lvl = 1
        self.lvl_up = 3000
        self.lvl_count = 0

        self.life_texture = arcade.load_texture("imgs/vidas.png")
        self.life_icon_size = 30

        self.life_positions = []
        self.update_life_positions()

        self.background_music = arcade.load_sound("musica_de_fondo_1.mp3", streaming=True)
        self.music_player = None  

        self.efect_bullet = arcade.load_sound("gunshot_smg_shot_1-203471.mp3")
        self.efect_destroy_enemys = arcade.load_sound("electronic-element-burn-spark-1-248606.mp3")

    def on_draw(self):
        self.clear()
        
        if not self.music_player or not self.music_player.playing:
            self.music_player = arcade.play_sound(self.background_music, volume=0.5, loop=True)

        if self.background:
            arcade.draw_texture_rect(self.background, arcade.rect.XYWH(window_width // 2, window_height // 2, window_width, window_height)
)
        else:
            arcade.set_background_color(BACKGROUND_COLOR)
        
        arcade.draw_rect_filled(arcade.rect.XYWH(100, window_height , 200, 180),PANEL_COLOR)

        arcade.draw_rect_filled(arcade.rect.XYWH(700, window_height , 200, 180),PANEL_COLOR)
        
        arcade.draw_rect_outline(arcade.rect.XYWH(400, window_height // 2, 400, window_height), arcade.color.WHITE, 2)
        
        self.player.draw()

        for bullet_p in self.bullet_player_list:
            bullet_p.draw()

        for bullet_e in self.bullet_enemy_list:
            bullet_e.draw()

        for enemy in self.enemys_list:
            enemy.draw()

        self.draw_score()
        self.draw_lives()
        self.draw_lvl()
        self.draw_times()

    def on_update(self, delta_time):
        if self.player.lives  <= 0: self.dead_player()
        if self.player.lives >= 1:
            self.player.move()
            
        self.time_show_enemys += delta_time

        for bullet_p in self.bullet_player_list:
            bullet_p.move()
            for enemy in self.enemys_list:
                if bullet_p.hit(enemy):
                    arcade.play_sound(self.efect_destroy_enemys)
                    self.lvl_count += enemy.points
                    self.update_lvl()
                    self.player.score += enemy.points
                    self.bullet_player_list.remove(bullet_p)
                    self.enemys_list.remove(enemy)
                    break

        if self.time_show_enemys >= self.controll_time_show_enemys:
            x = random.randrange(200 + self.player.width, 600, 150)
            y = random.randrange(window_height + self.player.height, window_height + 100, 10)
            self.enemys_list.append(Enemy(x, y))
            self.time_show_enemys = 0

        for enemy in self.enemys_list:
            enemy.move()
            if enemy.collision(self.player) and self.player.lives >= 1:
                self.player.score -= enemy.points
                self.player.lives -= enemy.damage
                self.enemys_list.remove(enemy)
                self.update_life_positions()
                self.position_lives = self.position_lives[:self.player.lives]


        self.time_shoot_enemy += delta_time
        if self.time_shoot_enemy >= self.controll_time_shoot_enemy and self.player.lives >= 1:
            for enemy in self.enemys_list:
                self.bullet_enemy_list.append(BulletEnemy(enemy.x, enemy.y, self.player.x, self.player.y))
            self.time_shoot_enemy = 0

        for bullet_e in self.bullet_enemy_list:
            bullet_e.calculate_speed(self.lvl)
            bullet_e.move()
            if bullet_e.hit(self.player) and self.player.lives >= 1:
                self.player.score -= bullet_e.points 
                self.player.lives -= bullet_e.damage
                self.bullet_enemy_list.remove(bullet_e)
                self.update_life_positions()
                self.position_lives = self.position_lives[:self.player.lives]


        self.bullet_player_list = [bullet for bullet in self.bullet_player_list if not bullet.off_screen()]
        self.enemys_list = [ene for ene in self.enemys_list if not ene.off_screen()] 

    def on_hide_view(self):
        if self.music_player:
            self.music_player.pause()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            keys["LEFT"] = True
        elif key == arcade.key.RIGHT:
            keys["RIGHT"] = True

        if key == arcade.key.UP:
            keys["UP"] = True
        elif key == arcade.key.DOWN:
            keys["DOWN"] = True

        if key == arcade.key.M:
            if self.music_player.playing:
                self.music_player.pause()
            else:
                self.music_player.play()

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            keys["LEFT"] = False
        elif key == arcade.key.RIGHT:
            keys["RIGHT"] = False
        
        if key == arcade.key.UP:
            keys["UP"] = False
        elif key == arcade.key.DOWN:
            keys["DOWN"] = False
        
        if key == arcade.key.SPACE and self.player.lives >= 1:
            if len(self.bullet_player_list) < 6:
                bullet = Bullet(self.player.x, self.player.y)
                self.bullet_player_list.append(bullet)
                arcade.play_sound(self.efect_bullet)
            else:
                pass

    def update_life_positions(self):
        spacing = 40 
        start_x = 30 
        self.life_positions = [start_x + i * spacing for i in range(self.player.lives)]

    def draw_lives(self):
        x_base = int(self.window.width * 0.03)  
        y_text = int(self.window.height * 0.95)  
        y_icons = int(self.window.height * 0.91)

        arcade.draw_text("VIDAS", x_base, y_text, ACCENT_COLOR, font_size=16, font_name=default_font)
        for i, _ in enumerate(self.life_positions[:self.player.lives]):
            arcade.draw_texture_rect(
                self.life_texture,
                arcade.rect.XYWH(x_base + i * 40, y_icons, self.life_icon_size, self.life_icon_size)
            )

    def draw_line_sections(self):
        for x in (200, 600):
            arcade.draw_line(x, 0, x, window_height, arcade.color.WHITE)
 
    def draw_score(self):
        x = int(self.window.width * 0.82)  
        y_label = int(self.window.height * 0.95)  
        y_value = int(self.window.height * 0.90)  

        arcade.draw_text("PUNTUACIÓN", x, y_label, ACCENT_COLOR, font_size=16, font_name=default_font)
        arcade.draw_text(f"{self.player.score}", x, y_value, TEXT_COLOR, font_size=24, font_name=score_font)

    def dead_player(self):
        if self.dead: 
            self.dead = False
            self.window.show_view(GameOver(self.window, self.player.score, self.player_name))

    def calculatew_score(self):
        try:
            df = pd.read_csv("scores.csv")
        except FileNotFoundError:
            df = pd.DataFrame(columns=["Nombre", "Puntaje"])
        
        new_score = pd.DataFrame([[self.player_name, self.player.score]], columns=["Nombre", "Puntaje"])
        df = pd.concat([df, new_score], ignore_index=True)
        
        df = df.sort_values("Puntaje", ascending=False).head(10)
        df.to_csv("scores.csv", index=False)

    def draw_lvl(self):
        x = int(self.window.width * 0.82)
        y_label = int(self.window.height * 0.80)
        y_value = int(self.window.height * 0.75)

        arcade.draw_text("NIVEL", x, y_label, ACCENT_COLOR, font_size=16, font_name=default_font)
        arcade.draw_text(f"{self.lvl}", x, y_value, TEXT_COLOR, font_size=24, font_name=score_font)

    def update_lvl(self):
        if self.lvl_count >= self.lvl_up and not self.controll_time_show_enemys <= 0.8:
            self.controll_time_shoot_enemy -= 0.15
            self.controll_time_show_enemys -= 0.2
            self.lvl += 1
            self.lvl_count = 0

    def draw_times(self):
        x = int(self.window.width * 0.03)
        y_label1 = int(self.window.height * 0.82)
        y_value1 = int(self.window.height * 0.77)

        y_label2 = int(self.window.height * 0.74)
        y_value2 = int(self.window.height * 0.69)

        arcade.draw_text("TIEMPO APARICIÓN", x, y_label1, ACCENT_COLOR, font_size=12, font_name=default_font)
        arcade.draw_text(f"{round(self.controll_time_show_enemys, 1)}s", x, y_value1, TEXT_COLOR, font_size=18, font_name=default_font)

        arcade.draw_text("TIEMPO DISPARO", x, y_label2, ACCENT_COLOR, font_size=12, font_name=default_font)
        arcade.draw_text(f"{round(self.controll_time_shoot_enemy, 1)}s", x, y_value2, TEXT_COLOR, font_size=18, font_name=default_font)


class Menu(arcade.View):
    def __init__(self):
        super().__init__()
        self.background = arcade.load_texture("imgs/menu_bg.png")
        self.logo = arcade.load_texture("imgs/game_logo.png") 
        self.player_name = ""
        self.asking_name = True
        self.name_prompt = "Ingresa tu nombre:"
        self.error_message = ""

    def on_draw(self):
        self.clear()
        if self.background:
            arcade.draw_texture_rect(self.background, arcade.rect.XYWH(window_width // 2, window_height // 2, window_width, window_height))
        else:
            arcade.set_background_color(BACKGROUND_COLOR)
        
        arcade.draw_rect_filled(arcade.rect.XYWH(window_width // 2, window_height // 2, window_width - 200, window_height - 200), PANEL_COLOR)
        
        if self.asking_name:
            arcade.draw_text("FLIGHT COMBAT", window_width // 2, window_height // 2 + 100,
                             ACCENT_COLOR, font_size=48, font_name=title_font, 
                             anchor_x="center", bold=True)
            
            arcade.draw_text(self.name_prompt, window_width // 2,
                             window_height // 2 + 30, TEXT_COLOR, font_size=24, 
                             font_name=default_font, anchor_x="center")
            
            arcade.draw_text(self.player_name, window_width // 2,
                             window_height // 2 - 10, TEXT_COLOR, font_size=24, 
                             font_name=default_font, anchor_x="center")
            
            if self.error_message:
                arcade.draw_text(self.error_message, window_width // 2,
                                 window_height // 2 - 50, DANGER_COLOR, font_size=18, 
                                 font_name=default_font, anchor_x="center")
                
            arcade.draw_text("Presiona ENTER para continuar", window_width // 2,
                             window_height // 2 - 100, TEXT_COLOR, font_size=20, 
                             font_name=default_font, anchor_x="center")
        else:
            arcade.draw_text("FLIGHT COMBAT", window_width // 2, window_height // 2 + 50,
                             ACCENT_COLOR, font_size=48, font_name=title_font, 
                             anchor_x="center", bold=True)
            
            arcade.draw_text(f"Jugador: {self.player_name}", window_width // 2,
                             window_height // 2, TEXT_COLOR, font_size=24, 
                             font_name=default_font, anchor_x="center")
            
            arcade.draw_text("Presiona E para comenzar", window_width // 2,
                             window_height // 2 - 50, TEXT_COLOR, font_size=24, 
                             font_name=default_font, anchor_x="center")
            
            arcade.draw_text("Controles: Flechas para mover, ESPACIO para disparar", 
                             window_width // 2, window_height // 2 - 100, 
                             TEXT_COLOR, font_size=18, font_name=default_font, 
                             anchor_x="center")
        

    def on_key_press(self, key, modifiers):
        if self.asking_name:
            if key == arcade.key.BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif key == arcade.key.ENTER:
                if len(self.player_name.strip()) > 0:
                    self.asking_name = False
                    self.error_message = ""
                else:
                    self.error_message = "El nombre no puede estar vacío"
        else:
            if key == arcade.key.E:
                self.window.show_view(GameView(self.player_name))

    def on_key_release(self, key, modifiers):
        pass

    def on_text(self, text):
        if self.asking_name:
            if text.isalnum() or text == ' ':
                self.player_name += text

if __name__ == "__main__":
    window = arcade.Window(window_width, window_height, title)
    arcade.set_background_color(BACKGROUND_COLOR)
    
    try:
        window.set_icon(arcade.load_texture("imgs/game_icon.png"))
    except:
        pass
    
    menu = Menu()
    window.show_view(menu)
    arcade.run()