"""
    Игра: Аркада - Мяу - Теоритный Бардак
    Главный персонаж - кот - он реализован классом Корабль
    Кот стреляет снарядами по Пончикам
    Пончики взрываются и отнимают жизни, если в них врезается персонаж
    В игре три уровня - уровни сменяются автоматически, если персонаж соберет весь лут на карте и наберет нужное количество очков стреляя по пончикам
    На каждом уровне спаунится больше пончиков и увеличивается число очков для перехода на новый уровень
    Количество жиней не обновляется при переходе на новый уровень, но обновляется после смерти
    При смерти лут и очки обнуляются, при переходе на новый уровень сохраняются
    Управление: движение левой кнопкой мыши, стрелять на пробел
    На главной заставке правой кнопкой мыши можно посмотреть справку
    Приятной игры
"""
import pygame
import random
import os


# Импортируем классы из соответствующих папок
from entities.Ship import Ship
from entities.Sprite import Sprite
from entities.Explosion import Explosion
from environment.Grid import Grid
from utils.ImageInfo import ImageInfo
from utils.vector import dist

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
levels_up = False


# --- Helper Functions for Groups --- #
def process_sprite_group(group, screen):
    for sprite in set(group):  # Iterate over a copy to allow modification
        sprite.update(WIDTH, HEIGHT)
        sprite.draw(screen)
        if sprite.update(WIDTH, HEIGHT):
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
    global current_level, grid, loot_collected, my_ship, score_to_next_level, nebula_images, nebula_image, MAX_ROCK

    current_level += 1
    level_filename = f"levels\level{current_level}.txt"
    level_data = load_level(level_filename)

    if level_data:
        grid = Grid(WIDTH // 50, HEIGHT // 50, 50, wall_image, loot_image)  # Создаем новый Grid
        generate_level(level_data, grid)
        # Увеличиваем необходимые очки
        score_to_next_level =  score_to_next_level * 2 + 25
        MAX_ROCK += 1

        # Меняем изображение фона (если есть)
        if current_level - 1 < len(nebula_images) and nebula_images[current_level - 1]:
            nebula_image = nebula_images[current_level - 1] # Update level image
        else:
            print(f"Нет изображения для уровня {current_level}, используем изображение по умолчанию")

        print(f"Загружен уровень {current_level}")
        return True
    else:
        print("Все уровни пройдены!")
        return False


def click(pos):
    global started, score, lives, MAX_ROCK, my_ship, rock_group, missile_group, explosion_group, loot_collected
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        score = 0
        loot_collected = 0
        lives = 3
        my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info, flight_image)
        rock_group = set()
        missile_group = set()
        explosion_group = set()
        soundtrack.play()
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
    loot_collected = 0

    #Этот кусок кода нужен был, чтобы менять внешний вид котов - кораблей с каждым уровнем, этот функционал возможно, появится потом
    #first_nebula_image = nebula_images[0] if len(nebula_images) > 0 and nebula_images[0] is not None else nebula_image
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
#from url
def load_image(url):
    try:
        import urllib.request
        from io import BytesIO
        image_stream = BytesIO(urllib.request.urlopen(url).read())
        image = pygame.image.load(image_stream)
        return image.convert_alpha()  # Ensures transparency
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")
        return None

#from local source
def load_image_local(directory, filename):
    try:
        image = pygame.image.load(os.path.join(directory, filename))
        return image.convert_alpha()
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")
        return None

#from url
def load_sound(url):
    try:
        import urllib.request
        from io import BytesIO
        sound_stream = BytesIO(urllib.request.urlopen(url).read())
        sound = pygame.mixer.Sound(sound_stream)
        return sound
    except Exception as e:
        print(f"Ошибка загрузки музыки: {e}")
        return None

#from local source
def load_music_local(directory, filename):
    try:
        sound = pygame.mixer.Sound(os.path.join(directory, filename))
        return sound
    except Exception as e:
        print(f"Ошибка загрузки музыки: {e}")

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
soundtrack = load_music_local('music', 'sound1.mp3')
missile_sound = load_music_local('music', 'shoot.mp3')
ship_thrust_sound = load_music_local('music', 'flight.mp3')
explosion_sound = load_music_local('music', 'explosion_orange.mp3')
loot_sound = load_music_local('music', 'loot.mp3')

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

my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info, flight_image)
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
                my_ship.set_thrust(True, started, ship_thrust_sound)
            elif event.button == 3 and not started and not game_over:  # Правая кнопка мыши
                show_instructions = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:  # Правая кнопка мыши отпущена
                show_instructions = False
            elif event.button == 1:  # Правая кнопка мыши отпущена
                my_ship.set_thrust(False,started, ship_thrust_sound)  # Выключаем звук тяги
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                my_ship.shoot(missile_group, started, missile_image, missile_info, missile_sound, ship_info)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                my_ship.reset_image(ship_info)  # Возвращаем исходное изображение корабля

    # --- Game Logic --- #
    if started:
        rock_spawner()

        # Проверка условия перехода на следующий уровень
        if score >= score_to_next_level and grid.get_loot_count() == 0:
            if next_level():
                # Переход на следующий уровень успешен
                continue
            else:
                # Все уровни пройдены
                started = False
                levels_up = True

    # --- Draw --- #
    screen.blit(nebula_image, (0, 0))
    time_value = (time / 4) % WIDTH
    screen.blit(debris_image, (time_value - WIDTH / 2, 0))
    screen.blit(debris_image, (time_value + WIDTH / 2, 0))
    process_sprite_group(rock_group, screen)
    process_sprite_group(missile_group, screen)
    process_sprite_group(explosion_group, screen)
    loot_collected = my_ship.update(started, grid, loot_collected, loot_sound, WIDTH, HEIGHT)
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

    # update loot
    loot_collected += group_group_collide(rock_group, missile_group)

    # Game Over
    if lives <= 0:
        game_over = True  # Устанавливаем флаг Game Over
        started = False
        soundtrack.stop()
        my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info, flight_image)
        rock_group = set()
        missile_group = set()
        explosion_group = set()
        grid = Grid(WIDTH // 50, HEIGHT // 50, 50, wall_image, loot_image)  # Создаем новый объект Grid
        level_data = load_level("levels\level1.txt")  # Загружаем данные первого уровня
        if level_data:
            generate_level(level_data, grid)  # Генерируем уровень заново
        else:
            print("Ошибка загрузки первого уровня!")
    if not started:
        if game_over:
            screen.blit(game_over_image, (0, 0))  # Отображаем экран Game Over
            if levels_up == True:
                final_level_text = font.render(f"Вы прошли все уровни!", True, (255, 255, 255))
                level_rect = final_level_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 200))
                screen.blit(final_level_text, level_rect)
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