import arcade
from models import World

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class ModelSprite(arcade.Sprite):
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model', None)

        super().__init__(*args, **kwargs)

    def sync_with_model(self):
        if self.model:
            self.set_position(self.model.x, self.model.y)

    def draw(self):
        self.sync_with_model()
        super().draw()


class PlayerRunWindow(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height)

        arcade.set_background_color(arcade.color.BLACK)

        self.world = World(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.player_sprite = ModelSprite('images/player.png',
                                      model=self.world.player)

        self.background = arcade.load_texture("images/city.jpg")

    def update(self, delta):
        self.world.update(delta)


    def draw_platforms(self, building):
        for b in building:
            arcade.draw_rectangle_filled(b.x + b.width // 2,
                                         b.y - b.height // 2,
                                         b.width, b.height,
                                         arcade.color.DARK_BROWN)

    def on_draw(self, line_start=0):
        arcade.set_viewport(self.world.player.x - SCREEN_WIDTH // 2,
                            self.world.player.x + SCREEN_WIDTH // 2,
                            0, SCREEN_HEIGHT)

        arcade.start_render()

        arcade.draw_texture_rectangle(self.player_sprite.center_x, SCREEN_HEIGHT // 2,
                                        SCREEN_WIDTH*2, SCREEN_HEIGHT*1, self.background)
        self.draw_platforms(self.world.building)

        self.player_sprite.draw()

        arcade.draw_text(str(self.world.score),
                         self.world.player.x + (SCREEN_WIDTH // 2) - 100,
                         self.height - 30,
                         arcade.color.WHITE, 30)

    def on_key_press(self, key, key_modifiers):
        if not self.world.is_started():
            self.world.start()
        self.world.on_key_press(key, key_modifiers)


if __name__ == '__main__':
    window = PlayerRunWindow(SCREEN_WIDTH, SCREEN_HEIGHT)
    arcade.set_window(window)
    arcade.run()