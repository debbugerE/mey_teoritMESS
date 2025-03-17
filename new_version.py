import pygame
import math
import random
import os

# --- Globals --- #
WIDTH = 800
HEIGHT = 600
MAX_ROCK = 5
score = 0
lives = 3
time = 0
started = False
loot_collected = 0
game_over = False  # переменная для отслеживания состояния Game Over
show_instructions = False  # показывать ли инструкцию
current_level = 1  # текущий уровень
score_to_next_level = 50  # очки для перехода на следующий уровень
nebula_images = []

# --- Image Info Class --- #
class ImageInfo:
    def __init__(self, center, size, radius=0, lifespan=None, animated=False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

# --- Helper Functions --- #
def angle_to_vector(ang):
    """Преобразует угол в вектор, учитывая направление Pygame."""
    return [math.cos(ang), math.sin(ang)]  # Инвертируем sin

def dist(p, q):
    return math.sqrt(((p[0] - q[0]) ** 2) + ((p[1] - q[1]) ** 2))

# --- Grid Class --- #
class Grid:
    def __init__(self, width, height, cell_size, wall_image, loot_image):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid = [['.' for _ in range(width)] for _ in range(height)]
        self.wall_image = wall_image
        self.loot_image = loot_image

    def draw(self, screen):
        for row in range(self.height):
            for col in range(self.width):
                x = col * self.cell_size
                y = row * self.cell_size
                if self.grid[row][col] == '#':
                    wall_image_scaled = pygame.transform.scale(self.wall_image, (self.cell_size, self.cell_size))
                    screen.blit(wall_image_scaled, (x, y))
                elif self.grid[row][col] == '@':
                    loot_image_scaled = pygame.transform.scale(self.loot_image, (self.cell_size, self.cell_size))
                    screen.blit(loot_image_scaled, (x, y))

    def add_obstacle(self, row, col):
        if 0 <= row < self.height and 0 <= col < self.width:
            self.grid[row][col] = '#'

    def is_obstacle(self, x, y):
        col = int(x / self.cell_size)
        row = int(y / self.cell_size)
        if 0 <= row < self.height and 0 <= col < self.width:
            return self.grid[row][col] == '#'
        else:
            return False

    def get_loot_count(self):
        """Подсчитывает количество лута на карте."""
        loot_count = 0
        for row in self.grid:
            loot_count += row.count('@')
        return loot_count


class Background:
    def __init__(self, image):
        self.image = image
        self.rect = image.get_rect()
        self.rect.topleft = (0, 0)  # Позиция в верхнем левом углу

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def set_image(self, new_image):
        self.image = new_image
        self.rect = new_image.get_rect()
        self.rect.topleft = (0, 0)


# --- Ship Class --- #
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.target_pos = None  # Целевая позиция для полета к мыши
        self.initial_distance = 0  # Изначальное расстояние до цели
        self.acceleration_rate = 0.1  # Скорость ускорения
        self.max_speed = 5  # Максимальная скорость
        self.deceleration_range = 0.5  # Процент пути, на котором начинается замедление
        self.original_image = image  # Сохраняем оригинальное изображение
        self.flight_image = flight_image  # Загруженное изображение для полета
        self.is_shooting = False  # Флаг для отслеживания стрельбы

    def draw(self, screen):
        global started
        img_rect = self.image.get_rect(center=self.image_center)
        rotated_image = pygame.transform.rotate(self.image, math.degrees(self.angle))
        new_rect = rotated_image.get_rect(center=self.pos)
        screen.blit(rotated_image, new_rect.topleft)

    def update(self):
        global started, grid, loot_collected  # Добавлен доступ к loot_collected
        if started:
            # Логика полета к мыши
            if self.target_pos:
                distance_to_target = dist(self.pos, self.target_pos)
                # Рассчитываем угол до цели
                angle_to_target = math.atan2(self.target_pos[1] - self.pos[1], self.target_pos[0] - self.pos[0])
                self.angle = -angle_to_target  # Устанавливаем угол корабля

                # Рассчитываем ускорение в зависимости от расстояния
                if distance_to_target > self.initial_distance * self.deceleration_range:  # Ускорение до определенной точки
                    # Рассчитываем вектор ускорения
                    acceleration_direction = angle_to_vector(-self.angle)
                    self.vel[0] += acceleration_direction[0] * self.acceleration_rate
                    self.vel[1] += acceleration_direction[1] * self.acceleration_rate

                    # Ограничиваем скорость
                    speed = math.sqrt(self.vel[0] ** 2 + self.vel[1] ** 2)
                    if speed > self.max_speed:
                        scale = self.max_speed / speed
                        self.vel[0] *= scale
                        self.vel[1] *= scale
                else:  # Замедление после определенной точки
                    # Рассчитываем скорость для замедления
                    deceleration_speed = 0.95  # Коэффициент замедления
                    self.vel[0] *= deceleration_speed
                    self.vel[1] *= deceleration_speed

                    # Если скорость достаточно мала, останавливаемся
                    if distance_to_target < 5:
                        self.target_pos = None
                        self.vel = [0, 0]

            # Обычное обновление позиции
            new_x = (self.pos[0] + self.vel[0]) % WIDTH
            new_y = (self.pos[1] + self.vel[1]) % HEIGHT

            # Получаем координаты ячейки, в которой находится корабль
            ship_col = int(new_x // grid.cell_size)
            ship_row = int(new_y // grid.cell_size)

            # Проверка на препятствие
            if not grid.is_obstacle(new_x, new_y):
                self.pos[0] = new_x
                self.pos[1] = new_y

            # Проверка на сбор лута
            if 0 <= ship_row < grid.height and 0 <= ship_col < grid.width and grid.grid[ship_row][ship_col] == '@':
                loot_collected += 1  # Увеличиваем счетчик лута
                grid.grid[ship_row][ship_col] = '.'  # Убираем лут с карты

            # update velocity
            if self.thrust:
                acc = angle_to_vector(self.angle)
                self.vel[0] += acc[0] * .1
                self.vel[1] += acc[1] * .1
            self.vel[0] *= .99
            self.vel[1] *= .99

    def set_thrust(self, on):
        global started
        self.thrust = on
        if on and started:
            ship_thrust_sound.play()  # No rewind in pygame, just play
        else:
            ship_thrust_sound.stop()

    def increment_angle_vel(self):
        self.angle_vel += .05

    def decrement_angle_vel(self):
        self.angle_vel -= .05

    def shoot(self):
        global missile_group, started
        if started:
            forward = angle_to_vector(-self.angle)
            missile_pos = [self.pos[0] + self.radius * forward[0], self.pos[1] + self.radius * forward[1]]
            missile_vel = [self.vel[0] + 6 * forward[0], self.vel[1] + 6 * forward[1]]
            missile = Sprite(missile_pos, missile_vel, self.angle, 0, missile_image, missile_info, missile_sound)
            missile_group.add(missile)
            # Меняем изображение на flight_image при стрельбе
            self.set_image(self.flight_image, (92, 92))
            self.is_shooting = True  # Устанавливаем флаг стрельбы

    def get_position(self):
        return self.pos

    def get_radius(self):
        return self.radius

    def set_image(self, image, size=None):
        """Устанавливает новое изображение для корабля и, при необходимости, изменяет его размер."""
        if size:
            self.image = pygame.transform.scale(image, size)
        else:
            self.image = image
        self.image_center = ship_info.get_center()
        self.image_size = ship_info.get_size()

    def reset_image(self):
        """Возвращает исходное изображение корабля."""
        self.set_image(self.original_image, (92, 92))
        self.is_shooting = False  # Снимаем флаг стрельбы

    def set_target_position(self, pos):
        """Устанавливает целевую позицию для движения к мыши."""
        self.target_pos = pos
        self.initial_distance = dist(self.pos, self.target_pos)  # Сохраняем начальное расстояние

# --- Sprite Class --- #
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound=None):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.play()

    def draw(self, screen):
        if self.animated:
            # Assuming animated images are strips and handled differently.  This is a placeholder.
            screen.blit(self.image, self.pos) #Basic drawing, needs proper animation handling
        else:
            img_rect = self.image.get_rect(center=self.image_center)
            rotated_image = pygame.transform.rotate(self.image, math.degrees(self.angle))
            new_rect = rotated_image.get_rect(center=self.pos)
            screen.blit(rotated_image, new_rect.topleft)

    def update(self):
        # update angle
        self.angle += self.angle_vel
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        self.age += 1
        if self.age < self.lifespan:
            return False
        else:
            return True

    def get_position(self):
        return self.pos

    def get_radius(self):
        return self.radius

    def collide(self, other):
        distance = dist(self.pos, other.get_position())
        return distance <= (self.radius + other.get_radius())

class Explosion(Sprite):
    def __init__(self, pos, vel, ang, ang_vel, images, info, sound=None):
        super().__init__(pos, vel, ang, ang_vel, images[0], info, sound)
        self.images = images
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.explosion_frame = 0.0
        self.animated = True
        self.lifespan = len(images)

    def draw(self, screen):
        if int(self.explosion_frame) < len(self.images):
            img = self.images[int(self.explosion_frame)]
            img_rect = img.get_rect(center=self.image_center)
            screen.blit(img, (self.pos[0] - img_rect.width / 2, self.pos[1] - img_rect.height / 2))

    def update(self):
        self.explosion_frame += 0.08
        return self.explosion_frame >= len(self.images)

# --- Helper Functions for Groups --- #
def process_sprite_group(group, screen):
    for sprite in set(group):  # Iterate over a copy to allow modification
        sprite.update()
        sprite.draw(screen)
        if sprite.update():
            group.remove(sprite)

def group_collide(group, other):
    collisions = 0
    for sprite in set(group):
        if sprite.collide(other):
            # Создаем спрайт анимации взрыва
            explosion = Explosion(sprite.pos, [0, 0], 0, 0, explosion_images, explosion_info, explosion_sound)
            explosion_group.add(explosion)

            group.remove(sprite)
            collisions += 1
    return collisions

def group_group_collide(group1, group2):
    collisions = 0
    for sprite in set(group1):
        if group_collide(group2, sprite):
            group1.remove(sprite)
            collisions += 1
    return collisions

# --- Game Logic Handlers --- #
def next_level():
    """Загружает следующий уровень."""
    global current_level, grid, loot_collected, my_ship, score_to_next_level, nebula_images, nebula_image

    current_level += 1
    level_filename = f"levels\level{current_level}.txt"
    level_data = load_level(level_filename)

    if level_data:
        grid = Grid(WIDTH // 50, HEIGHT // 50, 50, wall_image, loot_image)  # Создаем новый Grid
        generate_level(level_data, grid)
        loot_collected = 0  # Сбрасываем счетчик лута

        # Меняем изображение фона (если есть)
        if current_level - 1 < len(nebula_images) and nebula_images[current_level - 1]:
            nebula_image = nebula_images[current_level - 1] # Update level image
        else:
            print(f"Нет изображения для уровня {current_level}, используем изображение по умолчанию")

        # Увеличиваем необходимые очки
        score_to_next_level += 50

        print(f"Загружен уровень {current_level}")
        return True
    else:
        print("Все уровни пройдены!")
        return False


def click(pos):
    global started, score, lives, MAX_ROCK, my_ship, rock_group, missile_group, explosion_group
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        score = 0
        lives = 3
        MAX_ROCK = 5
        my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
        rock_group = set()
        missile_group = set()
        explosion_group = set()
        soundtrack.play(-1)
    elif started:
        # Устанавливаем цель для корабля при клике мышью
        my_ship.set_target_position(pos)

def start_game():
    global started, score, lives, MAX_ROCK, my_ship, rock_group, missile_group, explosion_group, game_over, grid, loot_collected, current_level, score_to_next_level, nebula_images
    started = True
    game_over = False
    score = 0
    lives = 3
    MAX_ROCK = 5
    score_to_next_level = 50

    # Load the first ship image if available, otherwise use default ship_image
    first_nebula_image = nebula_images[0] if len(nebula_images) > 0 and nebula_images[0] is not None else nebula_image
    #nebula = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, nebula_image, ship_info)

    my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
    rock_group = set()
    missile_group = set()
    explosion_group = set()
    soundtrack.play(-1)
    loot_collected = 0
    current_level = 1

    # load level
    level_data = load_level("level1.txt")
    if level_data:
      grid = Grid(WIDTH // 50, HEIGHT // 50, 50, wall_image, loot_image)
      generate_level(level_data, grid)

def rock_spawner():
    global rock_group, my_ship, started, MAX_ROCK, asteroid_info
    if started and len(rock_group) < MAX_ROCK:
        rock_pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]
        if dist(rock_pos, my_ship.get_position()) > 2 * asteroid_info.get_radius() + my_ship.get_radius():
            rock_vel = [random.random() * .6 - .3, random.random() * .6 - .3]
            rock_avel = random.random() * .2 - .1
            rock = Sprite(rock_pos, rock_vel, 0, rock_avel, asteroid_image, asteroid_info)
            rock_group.add(rock)

# --- Pygame Initialization --- #
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MEY TEOR MESS")
clock = pygame.time.Clock()

# --- Load Resources --- #
def load_image(url):
    try:
        import urllib.request
        from io import BytesIO
        image_stream = BytesIO(urllib.request.urlopen(url).read())
        image = pygame.image.load(image_stream)
        return image.convert_alpha()  # Ensures transparency
    except Exception as e:
        print(f"Error loading image: {e}")
        return None


def load_image_local(directory, filename):
    try:
        image = pygame.image.load(os.path.join(directory, filename))
        return image.convert_alpha()
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")
        return None


def load_sound(url):
    try:
        import urllib.request
        from io import BytesIO
        sound_stream = BytesIO(urllib.request.urlopen(url).read())
        sound = pygame.mixer.Sound(sound_stream)
        return sound
    except Exception as e:
        print(f"Error loading sound: {e}")
        return None

# Load images
wall_image = load_image_local("sprites", "туманность.png")
wall_image = pygame.transform.scale(wall_image, (50, 50))
loot_image = load_image_local("sprites", "лут.png")
loot_image = pygame.transform.scale(loot_image, (50, 50))


splash_image = load_image_local("screens", "Заставка 1.png")

# Load images (moved here to be accessible before initialization)
nebula_image = load_image_local("screens", "фон.png")
nebula_image = pygame.transform.scale(nebula_image, (WIDTH, HEIGHT))
# Load ship images for different levels
nebula_images = [
    load_image_local("screens", "фон.png"),
    load_image_local("screens", "фон2.png"),
    load_image_local("screens", "фон3.png")
]

# Scale the images
nebula_images = [pygame.transform.scale(img, (WIDTH, HEIGHT)) if img else None for img in nebula_images]


debris_image = load_image_local("screens", "debris_blend.png")
ship_image = load_image_local("sprites", "кот1.png")
ship_image = pygame.transform.scale(ship_image, (92, 92))
flight_image = load_image_local("sprites", "кот2.png")
flight_image = pygame.transform.scale(flight_image, (92, 92))
missile_image = load_image_local("sprites", "снаряд.png")
missile_image = pygame.transform.scale(flight_image, (20, 20))
asteroid_image = load_image_local("sprites", "пончик.png")
asteroid_image = pygame.transform.scale(asteroid_image, (90, 90))


# instructions images
instr_asteroid_image = load_image_local("sprites", "пончик.png")
instr_asteroid_image = pygame.transform.scale(instr_asteroid_image, (40, 40))
instr_wall_image = load_image_local("sprites", "туманность.png")
instr_wall_image = pygame.transform.scale(instr_wall_image, (40, 40))
instr_loot_image = load_image_local("sprites", "лут.png")
instr_loot_image = pygame.transform.scale(instr_loot_image, (40, 40))


game_over_image = load_image_local("screens", "game_over.jpg")  # Загружаем изображение Game Over

exp_image1 = load_image_local("boom", "взрыв 2.1.png")
exp_image1 = pygame.transform.scale(exp_image1, (90, 90))
exp_image2 = load_image_local("boom", "взрыв 3.1.png")
exp_image2 = pygame.transform.scale(exp_image2, (90, 90))
exp_image3 = load_image_local("boom", "взрыв 4.1.png")
exp_image3 = pygame.transform.scale(exp_image3, (90, 90))
explosion_images = [
    exp_image1,
    exp_image2,
    exp_image3
]

# Load sounds
soundtrack = load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
ship_thrust_sound = load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_orange.png")

if missile_sound:
    missile_sound.set_volume(0.5)

# --- Initialize Game Objects --- #
debris_info = ImageInfo([320, 240], [640, 480])
nebula_info = ImageInfo([400, 300], [800, 600])
splash_info = ImageInfo([200, 150], [400, 300])
ship_info = ImageInfo([45, 45], [90, 90], 35)
missile_info = ImageInfo([5, 5], [10, 10], 3, 50)
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)

my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
rock_group = set()
missile_group = set()
explosion_group = set()

# create grid
grid = Grid(WIDTH // 50, HEIGHT // 50, 50, wall_image, loot_image)


def load_level(filename):
    """Загружает уровень из файла."""
    level_data = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                level_data.append(line.strip())  # Удаляем лишние пробелы и переносы строк
    except FileNotFoundError:
        print(f"Ошибка: Файл уровня '{filename}' не найден.")
        return None  # Или можно создать уровень по умолчанию
    return level_data


def generate_level(level_data, grid):
    try:
        for row_index, row in enumerate(level_data):
            for col_index, cell in enumerate(row):
                if cell == '#':
                    grid.add_obstacle(row_index, col_index)
                elif cell == '@':
                    grid.grid[row_index][col_index] = '@'  # Place Loot
    except Exception as e:
        print(f"Ошибка при создании уровня: {e}")

# Load the level
level_data = load_level("levels\level1.txt") # директория файла
if level_data:
    generate_level(level_data, grid)

# --- Pygame Initialization --- #
pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MEOY TEORIT MESS")
clock = pygame.time.Clock()


# --- Game Loop --- #
running = True
while running:
    # --- Event Handling --- #
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левая кнопка мыши
                click(event.pos)
            elif event.button == 3 and not started and not game_over:  # Правая кнопка мыши
                show_instructions = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:  # Правая кнопка мыши отпущена
                show_instructions = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                my_ship.shoot()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                my_ship.reset_image()  # Возвращаем исходное изображение корабля

    # --- Game Logic --- #
    if started:
        rock_spawner()

        # Проверка условия перехода на следующий уровень
        if score >= 50 and grid.get_loot_count() == 0:
            if next_level():
                # Переход на следующий уровень успешен
                score = 0  # Обнуляем очки
            else:
                # Все уровни пройдены, что-то делаем (например, выводим со бщение)
                print("Вы прошли все уровни!")
                started = False  # Останавливаем игру

    # --- Draw --- #
    screen.blit(nebula_image, (0, 0))
    time_value = (time / 4) % WIDTH
    screen.blit(debris_image, (time_value - WIDTH / 2, 0))
    screen.blit(debris_image, (time_value + WIDTH / 2, 0))

    process_sprite_group(rock_group, screen)
    process_sprite_group(missile_group, screen)
    process_sprite_group(explosion_group, screen)

    my_ship.update()
    my_ship.draw(screen)
    grid.draw(screen)

    # draw UI
    font = pygame.font.Font(None, 38)
    lives_text = font.render(f"Lives: {lives}", True, (255, 255, 255))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    loot_text = font.render(f"Loot: {loot_collected}", True, (255, 255, 255))
    screen.blit(lives_text, (50, 50))
    screen.blit(score_text, (680, 50))
    screen.blit(loot_text, (350, 50))

    # update lives
    if group_collide(rock_group, my_ship):
        lives -= 1

    # update score
    score += group_group_collide(rock_group, missile_group)

    # Game Over
    if lives <= 0:
        game_over = True  # Устанавливаем флаг Game Over
        started = False
        soundtrack.stop()
        my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
        rock_group = set()
        missile_group = set()
        explosion_group = set()

    if not started:
        if game_over:
            screen.blit(game_over_image, (0, 0))  # Отображаем экран Game Over
            # Отображаем счет на экране Game Over
            final_score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            final_loot_text = font.render(f"Loot: {loot_collected}", True, (255, 255, 255))
            score_rect = final_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
            loot_rect = final_loot_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
            screen.blit(final_score_text, score_rect)
            screen.blit(final_loot_text, loot_rect)
        else:
            screen.blit(splash_image, (50, 50))
            time_value = (time / 4) % WIDTH
            screen.blit(debris_image, (time_value - WIDTH / 2, 0))
            screen.blit(debris_image, (time_value + WIDTH / 2, 0))

            # Draw instructions
            if show_instructions:
                instruction_font = pygame.font.Font(None, 24)
                line_spacing = 30
                text_color = (255, 255, 255)
                x_offset = 50
                y_start = 220

                instruction_texts = [
                    "1. Стрелять пробелом",
                    "2. Двигаться : щелчек левой кнопкой мыши",
                    "3. Собирайте лут:",
                    "4. Избегайте стен:",
                    "5. Разрушайте пончики:"
                ]

                for i, text in enumerate(instruction_texts):
                    text_surface = instruction_font.render(text, True, text_color)
                    screen.blit(text_surface, (x_offset, y_start + i * line_spacing))

                # Blit images for loot and wall
                screen.blit(instr_loot_image,
                            (x_offset + 150, y_start + 2 * line_spacing - 10))  # Сдвиг -10 для выравнивания
                screen.blit(instr_wall_image, (x_offset + 150, y_start + 3 * line_spacing - 5))
                # Blit image for asteroid
                screen.blit(instr_asteroid_image,
                            (x_offset + 190, y_start + 4 * line_spacing - 15))  # Уменьшаем сдвиг

    # --- Update Display --- #
    pygame.display.flip()
    time += 1
    clock.tick(60)  # Limit frame rate to 60 FPS

# --- Quit Pygame --- #
pygame.quit()
