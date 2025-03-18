import math

# --- Helper Functions --- #
def angle_to_vector(ang):
    """
    Преобразует угол в вектор, учитывая направление Pygame.
    Args:
        ang: Угол в радианах.
    Returns:
        Список [x, y], представляющий вектор.
    """
    return [math.cos(ang), math.sin(ang)]  # Инвертируем sin


def dist(p, q):
    """
    Вычисляет расстояние между двумя точками.
    Args:
        p: Первая точка [x, y].
        q: Вторая точка [x, y].
    Returns:
        Расстояние между точками (float).
    """
    return math.sqrt(((p[0] - q[0]) ** 2) + ((p[1] - q[1]) ** 2))