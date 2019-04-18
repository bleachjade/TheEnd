import arcade
import random
import os
import time
from models import World, Player

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCALE = 1

PLAYER_PIC = ['images/p8.png',
              'images/p7.png',
              'images/p6.png',
              'images/p5.png',
              'images/p4.png',
              'images/p3.png',
              'images/p2.png',
              'images/p1.png']


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


class PlayerRunWindow(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height)

        arcade.set_background_color(arcade.color.BLACK)

        self.world = World(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.cycle = 0

        self.start_time = 0
        self.end_time = 0


        for i in PLAYER_PIC:
            if i != 3:

                self.player_sprite = ModelSprite(i,
                                      model=self.world.player)
                self.cycle += 1
            else:
                self.cycle = 0
            # if PLAYER_PIC != 3:
            #     self.cycle += 1
            # else:
            #     self.cycle = 0

        self.item_texture = arcade.load_texture('images/item.png')
        self.platback = arcade.load_texture('images/platback1.png')
        self.background = arcade.load_texture("images/city.jpg")


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
        self.world.update(delta)
        self.player_sprite.update()
        if self.world.player.die():
            self.world.die()
            # self.world.freeze()

        if self.world.state == 2:
            if self.start_time == 0:
                self.start_time = time.time()



    def draw_platforms(self, building):
        for b in building:
            arcade.draw_texture_rectangle(b.x + b.width // 2,
                                         b.y - b.height // 2 * 6,
                                         b.width, b.height*6,
                                         self.platback)
    def draw_items(self, items):
        for i in items:
            if not i.is_collected:
                if i.effect != False:
                    arcade.draw_texture_rectangle(i.x, i.y, i.width, i.height,
                                              self.item_texture)

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.SPACE:
            if self.world.state == 1:
                self.world.start()
            self.world.on_key_press(key, key_modifiers)
        if key == arcade.key.E:
            exit()

    def on_draw(self, line_start=0):
        arcade.set_viewport(self.world.player.x - SCREEN_WIDTH // 2,
                            self.world.player.x + SCREEN_WIDTH // 2,
                            0, SCREEN_HEIGHT)

        arcade.start_render()

        arcade.draw_texture_rectangle(self.player_sprite.center_x, SCREEN_HEIGHT // 2,
                                        SCREEN_WIDTH*2, SCREEN_HEIGHT*1, self.background)
        self.draw_platforms(self.world.building)

        self.draw_items(self.world.items)
        arcade.draw_text('PRESS SPACE TO START.', -95, self.height // 2, arcade.color.BLACK, 30, align='left', bold=True, italic=True, width=20)
        arcade.draw_text('PRESS SPACE TO START.', -100, self.height // 2, arcade.color.BRIGHT_GREEN, 30, align='left', bold=True, italic=True, width=20)

        self.player_sprite.draw()

        # if PlayerRunWindow.on_key_press(self, key=arcade.key.SPACE, key_modifiers=None):
        # arcade.draw_text(f'time: {time.time()-self.start_time:.2f}',
        #                  self.world.player.x + (SCREEN_WIDTH // 3) - 100,
        #                  self.height - 30,
        #                  arcade.color.WHITE, 30)
        print(self.world.state)
        if self.world.state == 1:
            return
        elif self.world.state == 3:
            arcade.draw_rectangle_filled(self.player_sprite.center_x, SCREEN_HEIGHT//2, 1500, 130, arcade.color.BRIGHT_GREEN)
            arcade.draw_text(f'Surviving time: {self.end_time:.2f}', self.player_sprite.center_x-190, SCREEN_HEIGHT//2, arcade.color.WHITE, 40)

            if self.end_time == 0:
                self.end_time = time.time() - self.start_time
            arcade.draw_text(f'time: {self.end_time:.2f}',
                             self.world.player.x + (SCREEN_WIDTH // 3)-100,
                             self.height - 30,
                             arcade.color.WHITE, 30)

        else:
            print('asbhaaj')
            arcade.draw_text(f'time: {time.time()-self.start_time:.2f}',
                             self.world.player.x + (SCREEN_WIDTH // 3) - 100,
                             self.height - 30,
                             arcade.color.WHITE, 30)

if __name__ == '__main__':
    window = PlayerRunWindow(SCREEN_WIDTH, SCREEN_HEIGHT)
    arcade.set_window(window)
    arcade.run()