import pygame


class Grid:
    """
    Класс, представляющий сетку игрового поля.
    """
    def __init__(self, width, height, cell_size, wall_image, loot_image):
        """
        Инициализация сетки.
        Args:
            width: Ширина сетки (количество ячеек).
            height: Высота сетки (количество ячеек).
            cell_size: Размер одной ячейки в пикселях.
            wall_image: Объект pygame.Surface, представляющий изображение стены.
            loot_image: Объект pygame.Surface, представляющий изображение добычи.
        """
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid = [["." for _ in range(width)] for _ in range(height)]
        self.wall_image = wall_image
        self.loot_image = loot_image

    def draw(self, screen):
        """
        Отрисовка сетки на экране.
        Args:
            screen: Объект pygame.Surface, представляющий экран для отрисовки.
        """
        for row in range(self.height):
            for col in range(self.width):
                x = col * self.cell_size
                y = row * self.cell_size
                if self.grid[row][col] == "#":
                    wall_image_scaled = pygame.transform.scale(
                        self.wall_image, (self.cell_size, self.cell_size)
                    )
                    screen.blit(wall_image_scaled, (x, y))
                elif self.grid[row][col] == "@":
                    loot_image_scaled = pygame.transform.scale(
                        self.loot_image, (self.cell_size, self.cell_size)
                    )
                    screen.blit(loot_image_scaled, (x, y))

    def add_obstacle(self, row, col):
        """
        Добавление препятствия на сетку.
        Args:
            row: Номер строки ячейки.
            col: Номер столбца ячейки.
        """
        if 0 <= row < self.height and 0 <= col < self.width:
            self.grid[row][col] = "#"

    def is_obstacle(self, x, y):
        """
        Проверка, является ли ячейка препятствием.
        Args:
            x: X-координата в пикселях.
            y: Y-координата в пикселях.
        Returns:
            True, если ячейка является препятствием, False в противном случае.
        """
        col = int(x / self.cell_size)
        row = int(y / self.cell_size)
        if 0 <= row < self.height and 0 <= col < self.width:
            return self.grid[row][col] == "#"
        else:
            return False

    def get_loot_count(self):
        """
        Подсчитывает количество лута на карте.
        Returns:
            Количество лута на карте (int).
        """
        loot_count = 0
        for row in self.grid:
            loot_count += row.count("@")
        return loot_count

    def reset(self):
        """Сбрасывает сетку к начальному состоянию."""
        self.grid = [["." for _ in range(self.width)] for _ in range(self.height)]
