import arcade.key
import sys
from random import randint, random
from crash_detect import check_crash
import time
import math
import pyglet

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

GRAVITY = -1
MAX_VX = 11
ACCX = 1
JUMP_VY = 15

DOT_RADIUS = 44
BUILDING_MARGIN = 5

BACKGROUND_SPEED = 4

class Background:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self, speed, delta):
        self.y = self.y - (BACKGROUND_SPEED)

class Model:
    def __init__(self, world, x, y, angle):
        self.world = world
        self.x = x
        self.y = y
        self.angle = 0


class Player(Model):
    def __init__(self, world, x, y):
        super().__init__(world, x, y, 0)
        self.vx = 0
        self.vy = 0
        self.is_jump = False
        self.jump_count = 0
        self.platform = None
        self.jump_charge = 2

    def jump(self):
        if self.jump_count <= 2:
            self.is_jump = True
            self.vy = JUMP_VY
            self.jump_count += 1

        arcade.sound.play_sound(self.world.jump_sound)

    def update(self, delta):
        print(self.jump_charge)
        if self.building:
            self.jump_charge = 2
        self.die()
        if self.vx < MAX_VX:
            self.vx += ACCX
        self.x += self.vx

        if self.is_jump:
            self.y += self.vy
            self.vy += GRAVITY

            new_building = self.find_touching_building()
            if new_building:
                self.vy = 0
                self.jump_count = 0
                self.set_building(new_building)
        else:
            if (self.building) and (not self.is_on_building(self.building)):
                self.building = None
                self.is_jump = True
                self.jump_count = 0
                self.vy = 0

    def top_y(self):
        return self.y + (DOT_RADIUS // 2)

    def bottom_y(self):
        return self.y - (DOT_RADIUS // 2)

    def set_building(self, building):
        self.is_jump = False
        self.building = building
        self.y = building.y + (DOT_RADIUS // 2)

    def is_on_building(self, building, margin=BUILDING_MARGIN):
        if not building.in_top_range(self.x):
            return False

        if abs(building.y - self.bottom_y()) <= BUILDING_MARGIN:
            return True

        return False

    def is_falling_on_building(self, building):
        if not building.in_top_range(self.x):
            return False

        if self.bottom_y() - self.vy > building.y > self.bottom_y():
            return True

        return False

    def find_touching_building(self):
        building = self.world.building
        for b in building:
            if self.is_falling_on_building(b):
                return b
        return None

    def die(self):
        if self.top_y() < 0:
            self.world.state = 3
            return True
        return False

class Building:
    def __init__(self, world, x, y, width, height):
        self.world = world
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def in_top_range(self, x):
        return self.x <= x <= self.x + self.width

    def right_most_x(self):
        return self.x + self.width

class Bullet:
    def __init__(self, world, x, y):
        self.world = world
        self.x = x
        self.y = y
        self.is_hit = False
        self.speed = 1

    def update(self):
        if self.x < self.world.player.x-520:
            self.x = self.world.player.x+550
            self.y = randint(70, SCREEN_HEIGHT - 200)
        self.x -= self.speed

class World:
    STATE_FROZEN = 1
    STATE_STARTED = 2
    STATE_DEAD = 3

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.player = Player(self, 0, 120)
        self.init_building()

        self.player.set_building(self.building[0])

        self.score = 0

        self.state = World.STATE_FROZEN

        self.bullet = Bullet(self, SCREEN_WIDTH - 1, randint(50, SCREEN_HEIGHT - 50))
        self.bullet_list = []

        self.jump_sound = arcade.sound.load_sound('sound/jump2.wav')
        self.death_sound = arcade.sound.load_sound('sound/fuck1.wav')

    def init_building(self):
        self.building = [
            Building(self, 0, 100, 500, 50),
            Building(self, 550, 150, 500, 50),
            Building(self, 1100, 100, 500, 50),
            Building(self, 1650, 150, 500, 50),
        ]

    def update(self, delta):
        if self.state in [World.STATE_FROZEN, World.STATE_DEAD]:
            return
        self.player.update(delta)
        self.bullet.update()
        self.recycle_building()
        if check_crash(self.player.x, self.player.y, self.bullet.x, self.bullet.y) == True:
            arcade.sound.play_sound(self.death_sound)
            self.die()

    def too_far_left_x(self):
        return self.player.x - self.width


    def recycle_building(self):
        far_x = self.too_far_left_x()
        for p in self.building:
            if p.right_most_x() < far_x:
                last_x = max([pp.right_most_x() for pp in self.building])
                p.x = last_x + randint(50, 200)
                p.y = randint(100, 200)

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.SPACE:
            if self.player.jump_charge > 0:
                self.player.jump()
                self.player.jump_charge -= 1


    def start(self):
        self.state = World.STATE_STARTED
        t1 = time.time()
        return t1

    def freeze(self):
        self.state = World.STATE_FROZEN
        t2 = time.time()
        return t2

    def is_started(self):
        return self.state == World.STATE_STARTED

    def die(self):
        self.state = World.STATE_DEAD
