import random
from typing import List

import arcade

BLOCK_SIZE = 100  # Размер одного квадратного блока
BLOCK_SPRITE = "sprites/box_sprite.png"

CONTAINER_COLOR = arcade.csscolor.PALE_GOLDENROD
BORDER_COLOR = arcade.csscolor.BLACK
BACKGROUND_COLOR = arcade.csscolor.GOLD
ENTRY_COLOR = arcade.csscolor.DARK_SLATE_GREY

COLORS = [arcade.color.RED, arcade.color.DARK_ORANGE, arcade.color.GO_GREEN, arcade.color.BRIGHT_NAVY_BLUE,
          arcade.color.PURPLE, arcade.color.CERISE_PINK]  # Используемые цвета
STACK_HEIGHT = len(COLORS)  # Количество блоков в одной колбе в начале игры

CONTAINER_WIDTH = BLOCK_SIZE + 20  # Ширина колбы
CONTAINER_HEIGHT = BLOCK_SIZE * (STACK_HEIGHT + 2)  # Высота колбы
CONTAINER_BORDER = 2  # Ширина стенки колбы
CONTAINER_GAP = 0  # Расстояние между колбами

WW = CONTAINER_WIDTH * 10  # Ширина окна (Window Width)
WH = CONTAINER_HEIGHT + 2 * BLOCK_SIZE  # Высота окна (Window Height)
GRID_ALIGN_CELL = 10  # Устраняет проблемы с дробными значениями

BLOCK_SCALE = 0.75  # Размер блока (независимо от колб)

CONTAINER_POSITIONS = ((WW // 2 + (CONTAINER_WIDTH + CONTAINER_GAP), WH // 2),
                       (WW // 2 + (CONTAINER_WIDTH + CONTAINER_GAP) * 2, WH // 2),
                       (WW // 2 + (CONTAINER_WIDTH + CONTAINER_GAP) * 3, WH // 2),
                       (WW // 2 - (CONTAINER_WIDTH + CONTAINER_GAP), WH // 2),
                       (WW // 2 - (CONTAINER_WIDTH + CONTAINER_GAP) * 2, WH // 2),
                       (WW // 2 - (CONTAINER_WIDTH + CONTAINER_GAP) * 3, WH // 2),
                       (WW // 2, WH // 2),)  # Координаты колб

GRAVITY = 1000  # Гравитация, действующая на блоки


def a(coord, grid_cell_size: int = GRID_ALIGN_CELL) -> int:  # Округление целых значений (align)
    return int(coord // grid_cell_size * grid_cell_size)


class InteractiveGame(arcade.Window):
    def __init__(self) -> None:
        super().__init__(WW, WH, "Interactive Project")

        self.containers = None
        self.container_backs = None
        self.container_entries = None
        self.curr_block = None
        self.blocks = None
        self.physics_engine = None
        self.ground = None
        self.last_block_pos = None
        self.score_text = None

        self.mouse_down = False
        self.score = 0

    def setup(self) -> None:
        self.physics_engine = arcade.PymunkPhysicsEngine((0, -GRAVITY))

        arcade.set_background_color(BACKGROUND_COLOR)

        self.containers: List[arcade.SpriteList] = []
        self.container_backs = arcade.SpriteList()
        self.container_entries = arcade.SpriteList()
        self.add_containers()

        self.blocks = arcade.SpriteList()
        self.add_blocks()

        self.add_ground()

        self.physics_engine.add_sprite_list(self.blocks, 1)
        for c in self.containers:
            self.physics_engine.add_sprite_list(c, body_type=arcade.PymunkPhysicsEngine.STATIC)

    def add_containers(self) -> None:
        for x, y in CONTAINER_POSITIONS:
            left = arcade.SpriteSolidColor(width=CONTAINER_BORDER, height=CONTAINER_HEIGHT,
                                           color=BORDER_COLOR)
            left.center_x = a(x - CONTAINER_WIDTH // 2)
            left.center_y = a(y)

            right = arcade.SpriteSolidColor(width=CONTAINER_BORDER, height=CONTAINER_HEIGHT,
                                            color=BORDER_COLOR)
            right.center_x = a(x + CONTAINER_WIDTH // 2)
            right.center_y = a(y)

            bottom = arcade.SpriteSolidColor(width=CONTAINER_WIDTH, height=CONTAINER_BORDER,
                                             color=BORDER_COLOR)
            bottom.center_x = a(x)
            bottom.center_y = a(y - CONTAINER_HEIGHT // 2)

            c = arcade.SpriteList()
            c.append(left)
            c.append(right)
            c.append(bottom)
            self.containers.append(c)

            back = arcade.SpriteSolidColor(width=CONTAINER_WIDTH, height=CONTAINER_HEIGHT,
                                           color=CONTAINER_COLOR)
            back.center_x = a(x)
            back.center_y = a(y)
            self.container_backs.append(back)

            entry = arcade.SpriteSolidColor(width=CONTAINER_WIDTH, height=a(CONTAINER_HEIGHT // 10),
                                            color=ENTRY_COLOR)
            entry.center_x = a(x)
            entry.center_y = y + (CONTAINER_HEIGHT - CONTAINER_HEIGHT // 10) // 2
            self.container_entries.append(entry)

    def add_blocks(self) -> None:
        for x, y in CONTAINER_POSITIONS:
            colors_tmp: List[arcade.csscolor] = COLORS.copy()
            for i in range(STACK_HEIGHT):
                b = arcade.Sprite(BLOCK_SPRITE, BLOCK_SCALE)
                b.width, b.height = BLOCK_SIZE, BLOCK_SIZE
                b.color = random.choice(colors_tmp)
                colors_tmp.remove(b.color)
                b.center_x = a(x)
                b.center_y = a(y - 30 * i)
                self.blocks.append(b)

    def add_ground(self) -> None:
        self.ground = arcade.SpriteSolidColor(width=WW, height=100, color=arcade.csscolor.BROWN)
        self.ground.center_x = a(WW / 2)
        self.ground.center_y = a(0)
        self.ground.color = (100, 100, 100)
        self.score_text = arcade.Text("Score: " + str(self.score), start_x=a(WW / 2), start_y=100 / 5)
        self.physics_engine.add_sprite(self.ground, body_type=arcade.PymunkPhysicsEngine.STATIC)

    def on_draw(self):
        arcade.start_render()

        self.container_backs.draw()
        self.container_entries.draw()
        for c in self.containers:
            c.draw()

        self.ground.draw()
        self.blocks.draw()
        if self.curr_block is not None:
            self.curr_block.draw()

        self.score_text.text = ("Score: " + str(self.score)) if not self.check_won() else "You won!"
        self.score_text.draw()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        self.mouse_down = True

        blocks = arcade.get_sprites_at_point((x, y), self.blocks)

        if len(blocks) and self.check_max_same_container(blocks[-1]):
            self.curr_block = blocks[-1]
            self.last_block_pos = a(x), a(y)
            self.physics_engine.remove_sprite(self.curr_block)

    def check_max_same_container(self, block: arcade.Sprite) -> bool:
        x, y = None, None
        if arcade.check_for_collision_with_list(block, self.container_backs):
            y = block.center_y
            x = block.center_x

        if x is None or y is None:
            return False

        heights = []
        for b in self.blocks:
            if x - BLOCK_SIZE / 2 <= b.center_x <= x + BLOCK_SIZE / 2:
                heights.append(b.center_y)

        return max(heights) - BLOCK_SIZE / 2 <= y <= max(heights) + BLOCK_SIZE / 2

    def get_size_container_from_block(self, block: arcade.Sprite) -> int:
        x, y = None, None
        if arcade.check_for_collision_with_list(block, self.container_backs):
            y = block.center_y
            x = block.center_x

        if x is None or y is None:
            return False

        cnt = 0
        for b in self.blocks:
            if x - BLOCK_SIZE / 2 <= b.center_x <= x + BLOCK_SIZE / 2:
                cnt += 1
        return cnt

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        self.mouse_down = False

        if self.curr_block is None:
            return

        if not arcade.get_sprites_at_point((x, y), self.container_entries) or self.get_size_container_from_block(
                self.curr_block) > STACK_HEIGHT + 1:
            if self.last_block_pos is not None:
                self.curr_block.center_x, self.curr_block.center_y = self.last_block_pos
        self.physics_engine.add_sprite(self.curr_block)
        self.last_block_pos = None
        self.curr_block = None

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        if self.curr_block is not None:
            self.curr_block.center_x += dx
            self.curr_block.center_y += dy

    # noinspection PyBroadException
    def update(self, delta_time: float):
        if not self.mouse_down:
            for i in self.blocks:
                colls = arcade.check_for_collision_with_list(i, self.blocks)
                if colls and colls[-1].color == i.color:
                    try:
                        i.kill()
                    except:
                        pass
                    try:
                        colls[-1].kill()
                    except:
                        pass
                    self.score += 1
        self.physics_engine.step()

    def check_won(self) -> bool:
        colors_left = set()
        for b in self.blocks:
            colors_left.add(b.color)
        return len(colors_left) == len(self.blocks)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            self.close()


def main():
    window = InteractiveGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
