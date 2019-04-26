
import arcade
from arcade import Color
from typing import List


class WindowStack:
    def __init__(self):
        self.stack = []  # type: List[Window]

    def is_visible(self):
        return len(self.stack) > 0

    def draw(self):
        for window in self.stack:
            window.draw()

    def switch_focus(self, relative=1):
        self.stack[-1].switch_focus(relative=relative)

    def do_action(self):
        self.stack[-1].do_action()

    def on_key_escape(self):
        self.stack[-1].on_key_escape()

    def on_text(self, text):
        self.stack[-1].on_text(text)

    def on_text_motion(self, motion):
        self.stack[-1].on_text_motion(motion)

    def on_mouse_motion(self, x, y):
        self.stack[-1].on_mouse_motion(x, y)

    def on_mouse_press(self, x, y, button):
        self.stack[-1].on_mouse_press(x, y, button)


class Window:
    def __init__(self, window_stack, title=None):
        """
        :param WindowStack window_stack:
        :param str title:
        """
        self.window_stack = window_stack
        self.border_size = 20
        self.title = title
        self.title_label = None
        if title:
            self.title_label = create_html_text(
                title, color=arcade.color.BLACK, anchor_y="center", font_size=20)
        self.title_step_size = self.border_size

    def open(self):
        self.window_stack.stack.append(self)

    def close(self):
        self.window_stack.stack.remove(self)

    def get_size(self):
        raise NotImplementedError

    def draw(self):
        self.draw_background()
        return self.draw_title()

    def draw_background(self):
        from .app import app
        width, height = self.get_size()
        background_size_args = dict(
            center_x=app.window.width // 2, center_y=app.window.height // 2,
            width=width, height=height)
        arcade.draw_rectangle_filled(color=arcade.color.WHITE, **background_size_args)
        arcade.draw_rectangle_outline(color=arcade.color.BLUE, **background_size_args)

    def draw_title(self):
        from .app import app
        width, height = self.get_size()
        center_x = app.window.width // 2
        y = (app.window.height - height) // 2
        y += self.border_size
        if self.title_label:
            arcade.render_text(
                self.title_label,
                start_x=center_x - self.title_label.content_width // 2,
                start_y=app.window.height - y - self.title_label.content_height // 2)
            y += self.title_label.content_height + self.title_step_size
        return y

    def do_action(self):
        raise NotImplementedError

    def switch_focus(self, relative=1):
        pass

    def on_key_escape(self):
        self.close()

    def on_text(self, text):
        pass

    def on_text_motion(self, motion):
        pass

    def on_mouse_motion(self, x, y):
        pass

    def on_mouse_press(self, x, y, button):
        pass


class Menu(Window):
    def __init__(self, actions, initial_selected_action_index=0, **kwargs):
        """
        :param list[(str,()->None)] actions:
        :param int initial_selected_action_index:
        """
        super(Menu, self).__init__(**kwargs)
        self.selected_action_index = initial_selected_action_index
        self.actions = actions
        self.labels = [
            arcade.create_text(
                act[0], color=arcade.color.BLACK, anchor_y="center", font_size=20)
            for act in actions]
        self.label_location_map = {}
        self.label_width = max([label.content_width for label in self.labels]) + 30
        self.label_height = max([label.content_height for label in self.labels]) + 10
        self.label_step_size = 5

    def get_size(self):
        height = 0
        height += self.label_height * len(self.labels)
        height += self.label_step_size * (len(self.labels) - 1)
        if self.title_label:
            height += self.title_step_size + self.title_label.content_height
        height += self.border_size * 2
        width = self.label_width
        if self.title_label:
            width = max(width, self.title_label.content_width)
        width += self.border_size * 2
        return width, height

    def draw(self):
        self.label_location_map.clear()
        from .app import app
        center_x = app.window.width // 2
        y = super(Menu, self).draw()
        y += self.label_height // 2
        for i, label in enumerate(self.labels):
            focused = i == self.selected_action_index
            self.label_location_map[(center_x, y)] = i
            arcade.draw_rectangle_filled(
                color=arcade.color.BABY_BLUE if focused else arcade.color.BLUE_GRAY,
                center_x=center_x, center_y=app.window.height - y,
                width=self.label_width, height=self.label_height)
            arcade.draw_rectangle_outline(
                color=arcade.color.BLUE if focused else arcade.color.BLACK,
                center_x=center_x, center_y=app.window.height - y,
                width=self.label_width, height=self.label_height)
            arcade.render_text(
                label,
                start_x=center_x - label.content_width // 2, start_y=app.window.height - y)
            y += self.label_height + self.label_step_size

    def switch_focus(self, relative=1):
        self.selected_action_index += relative
        self.selected_action_index %= len(self.actions)

    def do_action(self):
        self.actions[self.selected_action_index][1]()

    def _find_label_for_location(self, x, y):
        for (label_x, label_y), i in self.label_location_map.items():
            if abs(label_x - x) < self.label_width // 2 and abs(label_y - y) < self.label_height // 2:
                return i
        return None

    def on_mouse_motion(self, x, y):
        idx = self._find_label_for_location(x, y)
        if idx is not None:
            self.selected_action_index = idx

    def on_mouse_press(self, x, y, button):
        idx = self._find_label_for_location(x, y)
        if button == 1 and idx is not None:
            self.selected_action_index = idx
            self.do_action()