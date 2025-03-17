import pygame
import sys
import os

try:
    pygame.init()

    WIDTH, HEIGHT = 800, 600
    FPS = 50
    TILE_SIZE = 50
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Перемещение героя. Камера")

    clock = pygame.time.Clock()

    def load_image(name, colorkey=None):
        fullname = os.path.join('data', name)
        try:
            if not os.path.isfile(fullname):
                raise FileNotFoundError(f"Файл с изображением '{fullname}' не найден")
            image = pygame.image.load(fullname)
            if colorkey is not None:
                image = image.convert()
                if colorkey == -1:
                    colorkey = image.get_at((0, 0))
                image.set_colorkey(colorkey)
            else:
                image = image.convert_alpha()
            return image
        except FileNotFoundError as e:
            print(e)
            terminate()
        except pygame.error as e:
            print(f"Ошибка при загрузке изображения: {e}")
            terminate()

    def terminate():
        pygame.quit()
        sys.exit()

    def load_level(filename):
        filename = os.path.join('data', filename)
        try:
            with open(filename, 'r') as mapFile:
                level_map = [line.strip() for line in mapFile]
            max_width = max(map(len, level_map))
            return list(map(lambda x: x.ljust(max_width, '.'), level_map))
        except FileNotFoundError:
            print(f"Файл уровня '{filename}' не найден")
            terminate()
        except Exception as e:
            print(f"Ошибка при загрузке уровня: {e}")
            terminate()

    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()

    tile_images = {
        'wall': load_image('box.png'),
        'empty': load_image('grass.png')
    }
    player_image = load_image('mario.png')


    class Tile(pygame.sprite.Sprite):
        def __init__(self, tile_type, pos_x, pos_y):
            super().__init__(tiles_group, all_sprites)
            try:
                self.image = tile_images[tile_type]
            except KeyError:
                print(f"Неизвестный тип тайла: {tile_type}")
                self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
                self.image.fill(BLACK)

            self.rect = self.image.get_rect().move(
                TILE_SIZE * pos_x, TILE_SIZE * pos_y)


    class Player(pygame.sprite.Sprite):
        def __init__(self, pos_x, pos_y):
            super().__init__(player_group, all_sprites)
            self.image = player_image
            self.rect = self.image.get_rect().move(
                TILE_SIZE * pos_x + 15, TILE_SIZE * pos_y + 5)
            self.x = pos_x
            self.y = pos_y

        def move(self, dx, dy, level_map):
            new_x = self.x + dx
            new_y = self.y + dy

            if 0 <= new_x < len(level_map[0]) and 0 <= new_y < len(level_map):
                if level_map[new_y][new_x] != '#':
                    self.x = new_x
                    self.y = new_y
                    self.rect.x = TILE_SIZE * self.x + 15
                    self.rect.y = TILE_SIZE * self.y + 5


    def generate_level(level):
        new_player = None
        try:
            for y in range(len(level)):
                for x in range(len(level[y])):
                    if level[y][x] == '.':
                        Tile('empty', x, y)
                    elif level[y][x] == '#':
                        Tile('wall', x, y)
                    elif level[y][x] == '@':
                        Tile('empty', x, y)
                        new_player = Player(x, y)
        except Exception as e:
            print(f"Ошибка при создании уровня: {e}")
            terminate()
        return new_player, level


    class Camera:
        def __init__(self, level_width, level_height, view_distance=25):
            self.level_width = level_width
            self.level_height = level_height
            self.view_distance = view_distance
            self.camera_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)

        def update(self, target):
            center_x = target.rect.centerx
            center_y = target.rect.centery

            x = center_x - WIDTH // 2
            y = center_y - HEIGHT // 2

            x = max(0, min(x, self.level_width - WIDTH))
            y = max(0, min(y, self.level_height - HEIGHT))

            self.camera_rect.topleft = (x, y)

        def apply(self, entity):
             return entity.rect.move(-self.camera_rect.x, -self.camera_rect.y)


    def start_screen(message=None):
        intro_text = ["МОЯ ИГРА", "",
                      "Правила:",
                      "Перемещение стрелками",
                      "Избегайте стен!"]
        if message:
            intro_text.append(message)
        try:
            fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
            screen.blit(fon, (0, 0))
        except Exception as e:
            print(f"Ошибка при загрузке фона заставки: {e}")
            screen.fill(BLACK)

        font = pygame.font.Font(None, 30)
        text_coord = 50

        for line in intro_text:
            string_rendered = font.render(line, True, BLACK)
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN or \
                        event.type == pygame.MOUSEBUTTONDOWN:
                    return

            pygame.display.flip()
            clock.tick(FPS)


    def game(level_file):
        global all_sprites, tiles_group, player_group

        all_sprites.empty()
        tiles_group.empty()
        player_group.empty()

        player, level_map = generate_level(load_level(level_file))
        level_width = len(level_map[0]) * TILE_SIZE
        level_height = len(level_map) * TILE_SIZE

        camera = Camera(level_width, level_height)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        player.move(-1, 0, level_map)
                    if event.key == pygame.K_RIGHT:
                        player.move(1, 0, level_map)
                    if event.key == pygame.K_UP:
                        player.move(0, -1, level_map)
                    if event.key == pygame.K_DOWN:
                        player.move(0, 1, level_map)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        start_screen("Игра перезапущена!")
                        game(level_file)

            camera.update(player)

            screen.fill(BLACK)

            for tile in tiles_group:
                screen.blit(tile.image, camera.apply(tile))

            screen.blit(player.image, camera.apply(player))

            pygame.display.flip()
            clock.tick(FPS)

        terminate()


    if __name__ == "__main__":
        try:
            level_file = input("Введите имя файла уровня: ")
            if not os.path.isfile(os.path.join("data", level_file)):
                raise FileNotFoundError(f"Файл уровня '{level_file}' не найден в папке data")
            start_screen()
            game(level_file)
        except FileNotFoundError as e:
            print(e)
            terminate()
        except Exception as e:
            print(f"Критическая ошибка: {e}")
            pygame.quit()
            sys.exit()
except Exception as e:
    print(f"Критическая ошибка при инициализации: {e}")
    pygame.quit()
    sys.exit()