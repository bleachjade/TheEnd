import arcade.key
import sys
from random import randint

GRAVITY = -1
MAX_VX = 15
ACCX = 1
JUMP_VY = 15

DOT_RADIUS = 40
BUILDING_MARGIN = 5

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

        self.platform = None

        self.status = False

    def jump(self):
        if not self.building:
            return

        if not self.is_jump:
            self.is_jump = True
            self.vy = JUMP_VY

    def update(self, delta):
        if self.vx < MAX_VX:
            self.vx += ACCX

        self.x += self.vx

        if self.is_jump:
            self.y += self.vy
            self.vy += GRAVITY

            new_building = self.find_touching_building()
            if new_building:
                self.vy = 0
                self.set_building(new_building)
        else:
            if (self.building) and (not self.is_on_building(self.building)):
                self.building = None
                self.is_jump = True
                self.vy = 0

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

        self.status = False

    def init_building(self):
        self.building = [
            Building(self, 0, 100, 500, 50),
            Building(self, 550, 150, 500, 50),
            Building(self, 1100, 100, 500, 50),
        ]

    def update(self, delta):
        if self.state in [World.STATE_FROZEN, World.STATE_DEAD]:
            return
        self.player.update(delta)
        self.recycle_building()

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
            self.player.jump()
            self.score += 1

    def start(self):
        self.state = World.STATE_STARTED

    def freeze(self):
        self.state = World.STATE_FROZEN

    def is_started(self):
        return self.state == World.STATE_STARTED