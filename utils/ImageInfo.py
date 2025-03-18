class ImageInfo:
    """
    Класс, хранящий информацию об изображении.
    """
    def __init__(self, center, size, radius=0, lifespan=None, animated=False):
        """
        Инициализация информации об изображении.
        Args:
            center: Центр изображения [x, y].
            size: Размер изображения [width, height].
            radius: Радиус столкновения (необязательно, по умолчанию 0).
            lifespan: Время жизни (необязательно, по умолчанию None, что означает бесконечность).
            animated: True, если изображение анимировано, False в противном случае (необязательно, по умолчанию False).
        """
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float("inf")
        self.animated = animated
    def get_center(self):
        """
        Возвращает центр изображения.
        Returns:
            Центр изображения [x, y].
        """
        return self.center

    def get_size(self):
        """
        Возвращает размер изображения.
        Returns:
            Размер изображения [width, height].
        """
        return self.size

    def get_radius(self):
        """
        Возвращает радиус столкновения.
        Returns:
            Радиус столкновения (int).
        """
        return self.radius

    def get_lifespan(self):
        """
        Возвращает время жизни.
        Returns:
            Время жизни (float).
        """
        return self.lifespan

    def get_animated(self):
        """
        Возвращает True, если изображение анимировано, False в противном случае.
        Returns:
            True, если изображение анимировано, False в противном случае (bool).
        """
        return self.animated
