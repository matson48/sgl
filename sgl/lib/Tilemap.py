import sgl
from sgl.lib.Sprite import Sprite, AnimatedSprite, RectSprite, Scene

class Tilemap(Sprite):
    tiles = []

    map = [[]]
    collision = [[]]
    default_collision = {}

    map_size = 0,0
    tile_size = 0,0

    to_update = []
    
    def __init__(self):
        super(Tilemap, self).__init__()

    def make_blank_map(self, width, height, tile=0):
        self.map = []
        self.collision = []

        for row in range(height):
            self.map.append(
                [tile for i in range(width)]
            )

            self.collision.append(
                [self.default_collision.get(tile, 0) 
                 for i in range(width)]
            )

        self.update_map_sizes()
        self.update_to_update()

    def set_tile(self, tile, x, y):
        self.map[y][x] = tile
        self.collision[y][x] = self.default_collision.get(tile, 0)

    def get_tile(self, x, y):
        return self.map[y][x]

    def set_collision(self, collision, x, y):
        self.collision[y][x] = collision

    def get_collision(self, x, y):
        return self.collision[y][x]

    def update_map_sizes(self):
        height = len(self.map)
        width = len(self.map[0])

        self.map_size = width, height

        self.width = width * self.tile_size[0]
        self.height = height * self.tile_size[1]

    def update_to_update(self):
        self.to_update = [i for i in self.tiles if isinstance(i, Sprite)]

    def coords_at(self, x, y, screen=True):
        if screen:
            x -= int(self.screen_x)
            y -= int(self.screen_y)
        return x / self.tile_size[0], y / self.tile_size[1]

    def in_bounds(self, row, column):
        if column < 0 or column >= self.map_size[0]:
            return False

        if row < 0 or row >= self.map_size[1]:
            return False

        return True

    def tile_at(self, x, y):
        column, row = self.coords_at(x, y)
        if self.in_bounds(row, column):
            return self.map[row][column]
        else:
            return -1
            
    def collision_at(self, x, y):
        column, row = self.coords_at(x, y)
        if self.in_bounds(row, column):
            return self.collision[row][column]
        else:
            return -1

    def update(self):
        super(Tilemap, self).update()

        for item in self.to_update:
            item.preupdate()
            item.update()

    def draw_self(self):
        x = int(self.screen_x)
        y = int(self.screen_y)

        for row in range(self.map_size[1]):
            for column in range(self.map_size[0]):
                tile = self.tiles[self.map[row][column]]
                if isinstance(tile, Sprite):
                    tile.position = x, y
                    tile.update_screen_positions()
                    tile.draw()
                else:
                    sgl.blitf(tile, x, y)

                x += self.tile_size[0]

            y += self.tile_size[1]
            x = int(self.screen_x)

class AnimatedTile(AnimatedSprite):
    def __init__(self, frames, speed, animation=[]):
        super(AnimatedTile, self).__init__()

        self.frames = frames
        self.anim_def_frame_length = speed

        if animation:
            self.animations = {
                "anim": animation
            }
        else:
            self.animations = {
                "anim": range(len(self.frames))
            }

        self.animation = "anim"
        self.play()


if __name__ == "__main__":
    sgl.init(640, 480, 1)
    sgl.set_font(sgl.load_system_font("Arial", 20))

    class TestScene(Scene):
        def __init__(self):
            super(TestScene, self).__init__()

            blackness = RectSprite()

            blackness.no_stroke = True
            blackness.fill_color = 0.25
            blackness.fixed = True
            blackness.fill()

            self.add(blackness)

            self.map = Tilemap()

            self.map.tiles = [
                sgl.make_surface(32, 32, (0,1.0,0)),
                AnimatedTile(
                    [sgl.make_surface(32, 32, (0,0,1.0)),
                     sgl.make_surface(32, 32, (0.5,0.5,1.0))],
                    1.0
                ),
                sgl.make_surface(32, 32, (0.5,0,0.25)),
            ]

            self.map.default_collision = {
                1: 1, 2: 1,
            }

            self.map.tile_size = 32, 32

            self.map.make_blank_map(10, 20)

            for i in range(10):
                self.map.set_tile(2, i, 0)

            for i in range(1,20):
                self.map.set_tile(2, 0, i)
                self.map.set_tile(2, 9, i)

            for i in range(5,20-5):
                for j in range(3, 7):
                    self.map.set_tile(1, j, i)

            for i in range(10):
                self.map.set_tile(2, i, 19)

            self.add(self.map)

        def draw(self):
            super(TestScene, self).draw()

        def update(self):
            super(TestScene, self).update()

            # tween.update(sgl.get_dt())
            # time.update(sgl.get_dt())

            mx, my = sgl.get_mouse_x(), sgl.get_mouse_y()
            x, y = self.map.coords_at(mx, my)
            map_text = "({}, {}) Tile: {} Collision: {}".format(
                x, y,
                self.map.tile_at(mx, my),
                self.map.collision_at(mx, my),
            )

            v = 200

            if sgl.is_key_pressed(sgl.key.down): 
                self.camera.y -= v * sgl.get_dt()
            if sgl.is_key_pressed(sgl.key.up): 
                self.camera.y += v * sgl.get_dt()

            if sgl.is_key_pressed(sgl.key.right): 
                self.camera.x -= v * sgl.get_dt()
            if sgl.is_key_pressed(sgl.key.left): 
                self.camera.x += v * sgl.get_dt()

            sgl.set_title(map_text + " FPS: " + str(int(sgl.get_fps())))

    scene = TestScene()

    sgl.run(scene.update, scene.draw)
