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
    return [math.cos(ang), -math.sin(ang)]  # Инвертируем sin


def dist(p, q):
    return math.sqrt(((p[0] - q[0]) ** 2) + ((p[1] - q[1]) ** 2))

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

    def draw(self, screen):
        global started
        img_rect = self.image.get_rect(center=self.image_center)
        rotated_image = pygame.transform.rotate(self.image, math.degrees(self.angle))
        new_rect = rotated_image.get_rect(center=self.pos)
        screen.blit(rotated_image, new_rect.topleft)

    def update(self):
        global started
        if started:
            # update angle
            self.angle += self.angle_vel
            # update position
            self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
            self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
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
            forward = angle_to_vector(self.angle)
            missile_pos = [self.pos[0] + self.radius * forward[0], self.pos[1] + self.radius * forward[1]]
            missile_vel = [self.vel[0] + 6 * forward[0], self.vel[1] + 6 * forward[1]]
            missile = Sprite(missile_pos, missile_vel, self.angle, 0, missile_image, missile_info, missile_sound)
            missile_group.add(missile)

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
def click(pos):
    global started, score, lives, MAX_ROCK, my_ship, rock_group, missile_group, explosion_group
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        lives = 3
        score = 0
        my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
        rock_group = set()
        missile_group = set()
        explosion_group = set()
        soundtrack.play(-1)

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
pygame.display.set_caption("Asteroids")
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
splash_image = load_image_local("screens", "Заставка 1.png")
nebula_image = load_image_local("screens", "фон.png")
nebula_image = pygame.transform.scale(nebula_image, (WIDTH, HEIGHT))
debris_image = load_image_local("screens", "debris_blend.png")
ship_image = load_image_local("sprites", "кот1.png")
ship_image = pygame.transform.scale(ship_image, (92, 92))
flight_image = load_image_local("sprites", "кот2.png")
flight_image = pygame.transform.scale(flight_image, (92, 92))
missile_image = load_image_local("sprites", "снаряд.png")
missile_image = pygame.transform.scale(flight_image, (20, 20))
asteroid_image = load_image_local("sprites", "пончик.png")
asteroid_image = pygame.transform.scale(asteroid_image, (90, 90))

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
explosion_sound = load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

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

# --- Game Loop --- #
running = True
while running:
    # --- Event Handling --- #
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            click(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                my_ship.decrement_angle_vel()
            elif event.key == pygame.K_RIGHT:
                my_ship.increment_angle_vel()
            elif event.key == pygame.K_UP:
                my_ship.set_thrust(True)
                # Меняем изображение при нажатии K_UP и подгоняем размер
                my_ship.set_image(flight_image, (92, 92))
                is_thrusting = True  # Устанавливаем флаг тяги
            elif event.key == pygame.K_SPACE:
                my_ship.shoot()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                my_ship.increment_angle_vel()
            elif event.key == pygame.K_RIGHT:
                my_ship.decrement_angle_vel()
            elif event.key == pygame.K_UP:
                my_ship.set_thrust(False)
                # Возвращаем исходное изображение при отпускании K_UP и подгоняем размер
                my_ship.set_image(ship_image, (92, 92))
                is_thrusting = False  # Снимаем флаг тяги


    # --- Game Logic --- #
    if started:
        rock_spawner()
        group_group_collide(rock_group, missile_group)
        if group_collide(rock_group, my_ship):
            lives -= 1
            if lives == 0:
                started = False
                soundtrack.stop()
                my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
                rock_group = set()
                missile_group = set()
                explosion_group = set()
        my_ship.update()

    # --- Drawing --- #
    screen.blit(nebula_image, (0, 0))
    time_value = (time / 4) % WIDTH
    screen.blit(debris_image, (time_value - WIDTH / 2, 0))
    screen.blit(debris_image, (time_value + WIDTH / 2, 0))

    font = pygame.font.Font(None, 30)
    lives_text = font.render(f"Lives: {lives}", True, (255, 255, 255))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(lives_text, (50, 50))
    screen.blit(score_text, (680, 50))

    my_ship.draw(screen)
    process_sprite_group(rock_group, screen)
    process_sprite_group(missile_group, screen)
    process_sprite_group(explosion_group, screen)

    if not started:
        screen.blit(splash_image, (WIDTH / 2 - splash_image.get_width() / 2, HEIGHT / 2 - splash_image.get_height() / 2))

    # --- Update Display --- #
    pygame.display.flip()
    time += 1
    clock.tick(60)  # Limit frame rate to 60 FPS

# --- Quit Pygame --- #
pygame.quit()
