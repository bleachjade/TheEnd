import arcade
import random
import time
from models import World, Player, Bullet

music = arcade.sound.load_sound('sound/bgmusic1.wav')
arcade.sound.play_sound(music)

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
SCREEN_TITLE = 'The Quake Game'
SCALE = 1

PLAYER_PIC = ['images/pp8.png',
              'images/pp7.png',
              'images/pp6.png',
              'images/pp5.png',
              'images/pp9.png',
              'images/pp3.png',
              'images/pp2.png',
              'images/pp1.png']

routes = {
    'menu':0,
    'game':1,
}
choices = {0: 'game'}

class Fpscounter:
    def __init__(self):
        import time
        import collections
        self.time = time.perf_counter
        self.frametime = collections.deque(maxlen=60)
        self.t = self.time()

    def tick(self):
        t = self.time()
        dt = t - self.t
        self.frametime.append(dt)
        self.t = t

    def fps(self):
        try:
            return 60 / sum(self.frametime)
        except ZeroDivisionError:
            return 0


class ModelSprite(arcade.Sprite):
    DELAY = 4
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model', None)
        super().__init__(*args, **kwargs)
        self.cycle = 0
        self.delay = 0
        self.player_sprite = arcade.Sprite(PLAYER_PIC[self.cycle], scale=SCALE)

    def sync_with_model(self):
        if self.model:
            self.set_position(self.model.x, self.model.y)

    def draw(self):
        self.sync_with_model()
        self.player_sprite = arcade.Sprite(PLAYER_PIC[self.cycle], scale=SCALE)
        self.player_sprite.set_position(self.model.x, self.model.y)
        self.player_sprite.draw()

    def update(self):
        self.delay +=1
        if self.delay == ModelSprite.DELAY:
            self.delay = 0
            if self.cycle != 7:
                self.cycle += 1
            else:
                self.cycle = 0

class BulletSprite(arcade.Sprite):
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model', None)
        super().__init__(*args, **kwargs)

    def sync_with_model(self):
        if self.model:
            self.set_position(self.model.x, self.model.y)

    def draw(self):
        self.sync_with_model()
        super().draw()

    def update(self):
        self.delay += 1
        if self.delay == ModelSprite.DELAY:
            self.delay = 0
            if self.cycle != 3:
                self.cycle += 1
            else:
                self.cycle = 0

class MenuChoiceSprite(arcade.AnimatedTimeSprite):
    def __init__(self, *args, **kwargs):
        self.is_select = False
        super().__init__(*args, **kwargs)

    def select(self):
        self.is_select = True

    def unselect(self):
        self.is_select = False


class JohnWickRunWindow(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height)

        self.current_route = routes['menu']
        self.selecting_choice = 0

        arcade.set_background_color(arcade.color.BLACK)

        self.menu_setup()
        self.game_setup(width, height)

    def menu_setup(self):
        self.choice_list = arcade.SpriteList()

        self.start = MenuChoiceSprite()
        self.start.textures.append(arcade.load_texture("images/startbut.png"))
        self.start.textures.append(arcade.load_texture("images/startbut1.png"))
        self.start.set_texture(0)
        self.start.texture_change_frames = 10

        self.start.center_x, self.start.center_y = self.width // 2 - 500, self.height // 2 - 30
        self.start.select()

        self.choice_list.append(self.start)

    def game_setup(self, width, height):
        self.world = World(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.bullet_sprite = BulletSprite('images/bullet.png', model=self.world.bullet)
        self.set_mouse_visible(False)

        self.cycle = 0

        self.start_time = 0
        self.end_time = 0

        self.fpscounter = Fpscounter()
        self.set_update_rate(1 / 70)

        for i in PLAYER_PIC:
            if i != 3:
                self.player_sprite = ModelSprite(i, model=self.world.player)
                self.cycle += 1
            else:
                self.cycle = 0
        self.platback = arcade.load_texture('images/platback2.png', scale=SCALE)
        self.background = arcade.load_texture("images/city.jpg")

    def update(self, delta):
        if self.current_route == routes['menu']:
            for choice in self.choice_list:
                if choice.is_select == True:
                    choice.update()
                    choice.update_animation()
        elif self.current_route == routes['game']:
            self.world.update(delta)
        self.player_sprite.update()

        if self.world.player.die():
            self.world.die()

        if self.world.state == 2:
            if self.start_time == 0:
                self.start_time = time.time()

    def draw_platforms(self, building):
        for b in building:
            arcade.draw_texture_rectangle(b.x + b.width // 2,
                                          b.y - b.height // 2 * 6,
                                          b.width, b.height * 6,
                                          self.platback)


    def on_draw(self, line_start=0):
        arcade.set_viewport(self.world.player.x - SCREEN_WIDTH // 2,
                            self.world.player.x + SCREEN_WIDTH // 2,
                            0, SCREEN_HEIGHT)

        arcade.start_render()

        arcade.draw_texture_rectangle(self.player_sprite.center_x, SCREEN_HEIGHT // 2,
                                      SCREEN_WIDTH * 2.5, SCREEN_HEIGHT * 1.5, self.background)

        if self.current_route == routes['menu']:
            self.draw_menu()


        elif self.current_route == routes['game']:
            self.fpscounter.tick()

        self.bullet_sprite.draw()
        self.draw_platforms(self.world.building)

        arcade.draw_text('PRESS [ENTER] TO', -100, self.height // 1.95, arcade.color.BLACK, 20, align="left",
                         bold=True, width=1000)
        arcade.draw_text('PRESS [ENTER] TO', -104, self.height // 1.95, arcade.color.AMBER, 20, align="left",
                         bold=True, width=1000)
        arcade.draw_text('*PRESS [SPACEBAR] TO JUMP        *PRESS [E] TO EXIT', -370, self.height // 1.1, arcade.color.BLACK, 25, align='left',
                         bold=True, italic=True, width=2000)
        arcade.draw_text('*PRESS [SPACEBAR] TO JUMP        *PRESS [E] TO EXIT', -375, self.height // 1.1, arcade.color.AMBER, 25, align='left',
                         bold=True, italic=True, width=2000)
        arcade.draw_text(f'*YOU CAN JUMP 3 TIMES \n  IN ONE ROW', -375, self.height // 1.19,
                         arcade.color.BLACK, 25, align='left',
                         bold=True, italic=True, width=2000)
        arcade.draw_text('*YOU CAN JUMP 3 TIMES \n   IN ONE ROW', -379, self.height // 1.19,
                         arcade.color.AMBER, 25, align='left',
                         bold=True, italic=True, width=2000)

        self.player_sprite.draw()
        if self.world.state == 1:
            return
        elif self.world.state == 3:
            arcade.draw_rectangle_filled(self.player_sprite.center_x, SCREEN_HEIGHT // 2, 1500, 130,
                                         arcade.color.AMBER)
            arcade.draw_text(f'Surviving time: {self.end_time:.2f}', self.player_sprite.center_x - 190,
                             SCREEN_HEIGHT // 1.9, arcade.color.WHITE, 40)
            arcade.draw_text('Press [R] to retry', self.player_sprite.center_x - 190, SCREEN_HEIGHT // 2.3,
                             arcade.color.WHITE, 40)
            arcade.draw_text('[E] to exit', self.player_sprite.center_x + 400, SCREEN_HEIGHT // 2.5,
                             arcade.color.WHITE, 15)

            if self.end_time == 0:
                self.end_time = time.time() - self.start_time
            arcade.draw_text(f'time: {self.end_time:.2f}',
                             self.world.player.x + (SCREEN_WIDTH // 3) - 100,
                             self.height - 30,
                             arcade.color.WHITE, 30)
        else:
            arcade.draw_text(f'time: {time.time()-self.start_time:.2f}',
                             self.world.player.x + (SCREEN_WIDTH // 3) - 100,
                             self.height - 30,
                             arcade.color.WHITE, 30)
            self.fpscounter.tick()
            arcade.draw_text(f"fps{self.fpscounter.fps():.2f}", self.world.player.x + (SCREEN_WIDTH // 3) - 10,
                             self.height - 50, arcade.color.WHITE)

    def draw_menu(self):
        self.choice_list.draw()

    def update_selected_choice(self):
        for choice in self.choice_list:
            choice.unselect()
            choice.set_texture(1)
        self.choice_list[self.selecting_choice].select()

    def on_key_press(self, key, key_modifiers):
        if self.current_route == routes['menu']:
            if key == arcade.key.DOWN:
                if self.selecting_choice < 2:
                    self.selecting_choice += 1
                else:
                    self.selecting_choice = 0
                self.update_selected_choice()
            elif key == arcade.key.UP:
                if self.selecting_choice > 0:
                    self.selecting_choice -= 1
                else:
                    self.selecting_choice = 2
                self.update_selected_choice()
            elif key == arcade.key.ENTER:
                self.current_route = routes[choices[self.selecting_choice]]
                self.world.start()


        elif self.current_route == routes['game']:

            if key == arcade.key.SPACE:
                self.world.on_key_press(key, key_modifiers)
            if key == arcade.key.R and self.world.state == World.STATE_DEAD:
                self.game_setup(SCREEN_WIDTH, SCREEN_HEIGHT)
                self.current_route = routes['menu']
            if key == arcade.key.E:
                exit()


if __name__ == '__main__':
    window = JohnWickRunWindow(SCREEN_WIDTH, SCREEN_HEIGHT)
    arcade.set_window(window)
    arcade.run()
