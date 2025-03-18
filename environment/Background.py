class Background:
    """
    Класс, представляющий фон игрового поля.
    """
    def __init__(self, image):
        """
        Инициализация фона.
        Args:
            image: Объект pygame.Surface, представляющий изображение фона.
        """
        self.image = image
        self.rect = image.get_rect()
        self.rect.topleft = (0, 0)  # Позиция в верхнем левом углу

    def draw(self, screen):
        """
        Отрисовка фона на экране.
        Args:
            screen: Объект pygame.Surface, представляющий экран для отрисовки.
        """
        screen.blit(self.image, self.rect)

    def set_image(self, new_image):
        """
        Изменение изображения фона.
        Args:
            new_image: Новый объект pygame.Surface для использования в качестве фона.
        """
        self.image = new_image
        self.rect = new_image.get_rect()
        self.rect.topleft = (0, 0)

    def reset(self):
        """Сбрасывает сетку к начальному состоянию."""
        self.grid = [["." for _ in range(self.width)] for _ in range(self.height)]
