import pygame
import math

from utils.vector import dist


class Sprite:
    """
    Базовый класс для игровых спрайтов.
    """
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound=None):
        """
        Инициализация спрайта.

        Args:
            pos: Начальная позиция спрайта [x, y].
            vel: Начальная скорость спрайта [x, y].
            ang: Начальный угол поворота спрайта (в радианах).
            ang_vel: Угловая скорость вращения спрайта (в радианах в секунду).
            image: Объект pygame.Surface, представляющий изображение спрайта.
            info: Объект ImageInfo, содержащий информацию об изображении.
            sound: Объект pygame.mixer.Sound (необязательно), звук, воспроизводимый при создании спрайта.
        """
        self.pos = list(pos)  # Создаем копию, чтобы не изменять исходный список
        self.vel = list(vel)  # Создаем копию, чтобы не изменять исходный список
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
        """
        Отрисовка спрайта на экране.
        Args:
            screen: Объект pygame.Surface, представляющий экран для отрисовки.
        """
        if self.animated:
            # Предполагается, что анимированные изображения обрабатываются иначе. Это заполнитель.
            screen.blit(self.image, self.pos)  # Базовая отрисовка, требует правильной обработки анимации
        else:
            img_rect = self.image.get_rect(center=self.image_center)
            rotated_image = pygame.transform.rotate(self.image, math.degrees(self.angle))
            new_rect = rotated_image.get_rect(center=self.pos)
            screen.blit(rotated_image, new_rect.topleft)

    def update(self, width, height):
        """
        Обновление состояния спрайта.
        Args:
            width: Ширина игрового поля.
            height: Высота игрового поля.
        Returns:
            True, если спрайт достиг конца своего жизненного цикла, False в противном случае.
        """
        # Обновляем угол
        self.angle += self.angle_vel
        # Обновляем позицию
        self.pos[0] = (self.pos[0] + self.vel[0]) % width
        self.pos[1] = (self.pos[1] + self.vel[1]) % height
        self.age += 1
        return self.age >= self.lifespan

    def get_position(self):
        """
        Возвращает текущую позицию спрайта.
        Returns:
            Список [x, y], представляющий позицию спрайта.
        """
        return self.pos

    def get_radius(self):
        """
        Возвращает радиус спрайта.
        Returns:
            Радиус спрайта (int).
        """
        return self.radius

    def collide(self, other):
        """
        Проверяет, сталкивается ли спрайт с другим спрайтом.
        Args:
            other: Другой спрайт (объект Sprite).
        Returns:
            True, если спрайты сталкиваются, False в противном случае.
        """
        distance = dist(self.pos, other.get_position())
        return distance <= (self.radius + other.get_radius())
