import arcade
import random
import os
import time
import math
from models import World, Player, Bullet
import sys
import re
import numpy
from typing import Set, List, Dict, Optional
import pyglet

# from .data import DATA_DIR, GFX_DIR, UserDataDir
# from .gui import Menu, WindowStack,

music = arcade.sound.load_sound('sound/bgmusic1.wav')
arcade.sound.play_sound(music)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = 'The Quake Game'
SCALE = 1

SPRITE_SCALING_LASER = 0.8
BULLET_SPEED = 5

MAX_VX = 7

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
    'car':2,
    'difficult':3,
}

choices = {
    0: 'game',
    1: 'car',
    2: 'difficult'

}


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
    DELAY = 5
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
        # super().draw()
        self.player_sprite = arcade.Sprite(PLAYER_PIC[self.cycle], scale=SCALE)
        self.player_sprite.set_position(self.model.x, self.model.y)
        self.player_sprite.draw()

    def update(self):
        self.delay +=1
        if self.delay == ModelSprite.DELAY:
            self.delay = 0
            if self.cycle != 3:
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


class PlayerRunWindow(arcade.Window):
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

        self.start.center_x, self.start.center_y = self.width // 2 - 400, self.height // 2 - 30
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
        self.item_texture = arcade.load_texture('images/item.png')
        self.platback = arcade.load_texture('images/platback1.png')
        self.background = arcade.load_texture("images/city2.jpg")

    # def reset(self):
    #     self.background = arcade.load_texture("images/city.jpg")
    #     self.world = World(SCREEN_WIDTH, SCREEN_HEIGHT)
    #
    #     self.player_sprite = ModelSprite('images/player.png',
    #                                   model=self.world.player)
    #     # self.player_sprite.append_texture(arcade.load_texture('images/super_dot.png'))
    #
    #     self.item_texture = arcade.load_texture('images/item.png')
    #     # self.super_coin = arcade.load_texture('images/super_coin.png')
    #     self.start_time = 0

    def update(self, delta):
        if self.current_route == routes['menu']:
            for choice in self.choice_list:
                if choice.is_select == True:
                    choice.update()
                    choice.update_animation()
        elif self.current_route == routes['game']:
            self.world.update(delta)
        # self.world.update(delta)
        self.player_sprite.update()

        if self.world.player.die():
            self.world.die()
            # self.world.freeze()

        if self.world.state == 2:
            # arcade.sound.play_sound(self.world.bg)
            if self.start_time == 0:
                self.start_time = time.time()

    def draw_platforms(self, building):
        for b in building:
            arcade.draw_texture_rectangle(b.x + b.width // 2,
                                          b.y - b.height // 2 * 6,
                                          b.width, b.height * 6,
                                          self.platback)

    def draw_items(self, items):
        for i in items:
            if not i.is_collected:
                if i.effect != False:
                    arcade.draw_texture_rectangle(i.x, i.y, i.width, i.height,
                                                  self.item_texture)


    def on_draw(self, line_start=0):
        arcade.set_viewport(self.world.player.x - SCREEN_WIDTH // 2,
                            self.world.player.x + SCREEN_WIDTH // 2,
                            0, SCREEN_HEIGHT)

        arcade.start_render()

        arcade.draw_texture_rectangle(self.player_sprite.center_x, SCREEN_HEIGHT // 2,
                                      SCREEN_WIDTH * 2, SCREEN_HEIGHT * 1, self.background)

        if self.current_route == routes['menu']:
            self.draw_menu()


        elif self.current_route == routes['game']:
            self.fpscounter.tick()
            # self.check_state()


        self.bullet_sprite.draw()
        self.draw_platforms(self.world.building)

        self.draw_items(self.world.items)
        arcade.draw_text('*PRESS [SPACEBAR] TO JUMP        *PRESS [E] TO EXIT', -370, self.height // 1.1, arcade.color.BLACK, 25, align='left',
                         bold=True, italic=True, width=2000)
        arcade.draw_text('*PRESS [SPACEBAR] TO JUMP        *PRESS [E] TO EXIT', -375, self.height // 1.1, arcade.color.AMBER, 25, align='left',
                         bold=True, italic=True, width=2000)

        self.player_sprite.draw()

        print(self.world.state)
        if self.world.state == 1:
            return
        elif self.world.state == 3:
            arcade.draw_rectangle_filled(self.player_sprite.center_x, SCREEN_HEIGHT // 2, 1500, 130,
                                         arcade.color.AMBER)
            arcade.draw_text(f'Surviving time: {self.end_time:.2f}', self.player_sprite.center_x - 190,
                             SCREEN_HEIGHT // 1.9, arcade.color.WHITE, 40)
            arcade.draw_text('Press [E] to exit', self.player_sprite.center_x - 190, SCREEN_HEIGHT // 2.3,
                             arcade.color.WHITE, 40)

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


        elif self.current_route == routes['game']:

            if key == arcade.key.SPACE:
                if self.world.state == 1:
                    self.world.start()
                self.world.on_key_press(key, key_modifiers)
            if key == arcade.key.E:
                exit()


if __name__ == '__main__':
    window = PlayerRunWindow(SCREEN_WIDTH, SCREEN_HEIGHT)
    arcade.set_window(window)
    arcade.run()
