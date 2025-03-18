import pygame
import math

from utils.vector import dist, angle_to_vector
from entities.Sprite import Sprite


class Ship:
    """
    Класс, представляющий корабль игрока.
    """
    def __init__(self, pos, vel, angle, image, info, flight_image):
        """
        Args:
            pos: Начальная позиция корабля [x, y].
            vel: Начальная скорость корабля [x, y].
            angle: Начальный угол поворота корабля (в радианах).
            image: Объект pygame.Surface, представляющий изображение корабля.
            info: Объект ImageInfo, содержащий информацию об изображении.
            flight_image: Изображение корабля в состоянии полета.
        """
        self.pos = list(pos)
        self.vel = list(vel)
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.target_pos = None
        self.initial_distance = 0
        self.acceleration_rate = 0.1
        self.max_speed = 5
        self.deceleration_range = 0.5
        self.original_image = image
        self.flight_image = flight_image
        self.is_shooting = False

    def draw(self, screen):
        """
        Отрисовка корабля на экране.
        Args:
            screen: Объект pygame.Surface, представляющий экран для отрисовки.
        """
        img_rect = self.image.get_rect(center=self.image_center)
        rotated_image = pygame.transform.rotate(self.image, math.degrees(self.angle))
        new_rect = rotated_image.get_rect(center=self.pos)
        screen.blit(rotated_image, new_rect.topleft)

    def update(self, started, grid, loot_collected, loot_sound, width, height):
        """
        Обновление состояния корабля.
        Args:
            started: Флаг, указывающий, началась ли игра.
            grid: Объект Grid, представляющий карту уровня.
            loot_collected: Переменная, хранящая количество собранной добычи.
            loot_sound: Звук, воспроизводимый при сборе добычи.
            width: Ширина игрового поля.
            height: Высота игрового поля.
        Returns:
            Обновленное значение loot_collected.
        """
        if started:
            if self.target_pos:
                distance_to_target = dist(self.pos, self.target_pos)
                angle_to_target = math.atan2(
                    self.target_pos[1] - self.pos[1],
                    self.target_pos[0] - self.pos[0]
                )
                self.angle = -angle_to_target

                if distance_to_target > self.initial_distance * self.deceleration_range:
                    acceleration_direction = angle_to_vector(-self.angle)
                    self.vel[0] += acceleration_direction[0] * self.acceleration_rate
                    self.vel[1] += acceleration_direction[1] * self.acceleration_rate

                    speed = math.sqrt(self.vel[0] ** 2 + self.vel[1] ** 2)
                    if speed > self.max_speed:
                        scale = self.max_speed / speed
                        self.vel[0] *= scale
                        self.vel[1] *= scale
                else:
                    deceleration_speed = 0.95
                    self.vel[0] *= deceleration_speed
                    self.vel[1] *= deceleration_speed

                    if distance_to_target < 5:
                        self.target_pos = None
                        self.vel = [0, 0]

            new_x = (self.pos[0] + self.vel[0]) % width
            new_y = (self.pos[1] + self.vel[1]) % height

            ship_col = int(new_x // grid.cell_size)
            ship_row = int(new_y // grid.cell_size)

            if not grid.is_obstacle(new_x, new_y):
                self.pos[0] = new_x
                self.pos[1] = new_y

            if 0 <= ship_row < grid.height and 0 <= ship_col < grid.width and grid.grid[ship_row][ship_col] == '@':
                loot_collected += 1
                grid.grid[ship_row][ship_col] = '.'
                loot_sound.play()

            if self.thrust:
                acc = angle_to_vector(self.angle)
                self.vel[0] += acc[0] * 0.1
                self.vel[1] += acc[1] * 0.1
            self.vel[0] *= 0.99
            self.vel[1] *= 0.99
        return loot_collected

    def set_thrust(self, on, started, ship_thrust_sound):
        """
        Включение/выключение тяги корабля.
        Args:
            on: True для включения тяги, False для выключения.
            started: Флаг, указывающий, началась ли игра.
            ship_thrust_sound: Звук тяги корабля.
        """
        self.thrust = on
        if on and started:
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.stop()

    def increment_angle_vel(self):
        """
        Увеличение угловой скорости вращения корабля.
        """
        self.angle_vel += 0.05

    def decrement_angle_vel(self):
        """
        Уменьшение угловой скорости вращения корабля.
        """
        self.angle_vel -= 0.05

    def shoot(self, missile_group, started, missile_image, missile_info, missile_sound, ship_info):
        """
        Выстрел ракеты.
        Args:
            missile_group: Группа спрайтов, содержащая ракеты.
            started: Флаг, указывающий, началась ли игра.
            missile_image: Изображение ракеты.
            missile_info: Объект ImageInfo, содержащий информацию об изображении ракеты.
            missile_sound: Звук выстрела ракеты.
            ship_info:  Объект ImageInfo, содержащий информацию об изображении корабля.
        """
        if started:
            forward = angle_to_vector(-self.angle)
            missile_pos = [self.pos[0] + self.radius * forward[0], self.pos[1] + self.radius * forward[1]]
            missile_vel = [self.vel[0] + 6 * forward[0], self.vel[1] + 6 * forward[1]]
            missile = Sprite(missile_pos, missile_vel, self.angle, 0, missile_image, missile_info, missile_sound)
            missile_group.add(missile)
            self.set_image(self.flight_image, ship_info, (92, 92))
            self.is_shooting = True

    def get_position(self):
        """
        Возвращает текущую позицию корабля.
        Returns:
            Список [x, y], представляющий позицию корабля.
        """
        return self.pos

    def get_radius(self):
        """
        Возвращает радиус корабля.
        Returns:
            Радиус корабля (int).
        """
        return self.radius
    def set_image(self, image, ship_info, size=None):
        """
        Устанавливает новое изображение для корабля.
        Args:
            image: Объект pygame.Surface, представляющий изображение корабля.
            ship_info: Объект ImageInfo, содержащий информацию об изображении корабля.
            size: Новый размер изображения (необязательно).
        """
        if size:
            self.image = pygame.transform.scale(image, size)
        else:
            self.image = image
        self.image_center = ship_info.get_center()
        self.image_size = ship_info.get_size()

    def reset_image(self, ship_info):
        """
        Возвращает исходное изображение корабля.
        Args:
            ship_info:  Объект ImageInfo, содержащий информацию об изображении корабля.
        """
        self.set_image(self.original_image, ship_info, (92, 92))
        self.is_shooting = False

    def set_target_position(self, pos):
        """
        Устанавливает целевую позицию для движения к мыши.
        Args:
            pos: Позиция мыши [x, y].
        """
        self.target_pos = pos
        self.initial_distance = dist(self.pos, self.target_pos)

    def reset(self, width, height):
        """
        Сбрасывает позицию корабля в центр экрана.
        Args:
            width: Ширина игрового поля.
            height: Высота игрового поля.
        """
        self.pos = [width / 2, height / 2]
        self.vel = [0, 0]
        self.angle = 0
        self.target_pos = None
