from entities.Sprite import Sprite


class Explosion(Sprite):
    """
    Класс, представляющий спрайт взрыва.
    """
    def __init__(self, pos, vel, ang, ang_vel, images, info, sound=None):
        """
        Инициализация взрыва.
        Args:
            pos: Начальная позиция взрыва [x, y].
            vel: Начальная скорость взрыва [x, y].
            ang: Начальный угол поворота взрыва (в радианах).
            ang_vel: Угловая скорость вращения взрыва (в радианах в секунду).
            images: Список объектов pygame.Surface, представляющих кадры анимации взрыва.
            info: Объект ImageInfo, содержащий информацию об изображении.
            sound: Объект pygame.mixer.Sound (необязательно), звук, воспроизводимый при создании взрыва.
        """
        super().__init__(pos, vel, ang, ang_vel, images[0], info, sound)
        self.images = images
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.explosion_frame = 0.0
        self.animated = True
        self.lifespan = len(images)

    def draw(self, screen):
        """
        Отрисовка взрыва на экране.
        Args:
            screen: Объект pygame.Surface, представляющий экран для отрисовки.
        """
        if int(self.explosion_frame) < len(self.images):
            img = self.images[int(self.explosion_frame)]
            img_rect = img.get_rect(center=self.image_center)
            screen.blit(
                img, (self.pos[0] - img_rect.width / 2, self.pos[1] - img_rect.height / 2)
            )

    def update(self, width, height):
        """
        Обновление состояния взрыва.
        Args:
            width: Ширина игрового поля.
            height: Высота игрового поля.
        Returns:
            True, если анимация взрыва завершена, False в противном случае.
        """
        self.explosion_frame += 0.08
        return self.explosion_frame >= len(self.images)
