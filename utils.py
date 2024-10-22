import random
from loader import ROOMS


def print_field(field):
    for row in field:
        print(*row, sep='\t')


import random
import math

def generate_field(width, height, bomb_percentage, safe_zone: tuple, safe_zone_square_percent=0.2):
    # Создаем поле, где -3 означает необработанную клетку
    field = [[{'value': -3, 'opened': False, 'flag': False} for _ in range(width)] for _ in range(height)]

    if not (0 <= safe_zone[0] < width and 0 <= safe_zone[1] < height):
        raise ValueError('Safe zone is out of the field')

    # Определяем размер безопасной зоны
    safe_zone_area = int(width * height * safe_zone_square_percent)
    safe_zone_radius = int(math.sqrt(safe_zone_area / math.pi))

    # Определяем границы безопасной зоны
    sx_min = max(0, safe_zone[0] - safe_zone_radius)
    sx_max = min(width, safe_zone[0] + safe_zone_radius + 1)
    sy_min = max(0, safe_zone[1] - safe_zone_radius)
    sy_max = min(height, safe_zone[1] + safe_zone_radius + 1)

    # Обозначаем безопасную зону (клетки со значением 0) и открываем их
    for y in range(sy_min, sy_max):
        for x in range(sx_min, sx_max):
            if (x - safe_zone[0])**2 + (y - safe_zone[1])**2 <= safe_zone_radius**2:
                field[y][x]['value'] = 0
                # field[y][x]['opened'] = True

    # Генерируем мины вне безопасной зоны
    bomb_count = int(width * height * bomb_percentage)
    placed_bombs = 0

    while placed_bombs < bomb_count:
        x, y = random.randint(0, width - 1), random.randint(0, height - 1)
        if field[y][x]['value'] == -3:  # Ставим бомбы только на необработанных клетках
            field[y][x]['value'] = -1
            placed_bombs += 1

    # Заполняем соседние клетки количеством мин
    for y in range(height):
        for x in range(width):
            if field[y][x]['value'] == -1:
                continue

            bomb_count = 0
            for x_offset in range(-1, 2):
                for y_offset in range(-1, 2):
                    nx, ny = x + x_offset, y + y_offset
                    if (x_offset == 0 and y_offset == 0) or not (0 <= nx < width and 0 <= ny < height):
                        continue
                    if field[ny][nx]['value'] == -1:
                        bomb_count += 1

            # if field[y][x]['value'] != 0:  # Не трогаем клетки, которые уже принадлежат безопасной зоне
            field[y][x]['value'] = bomb_count

    return field



def generate_key(length):
    return ''.join(random.choice('0123456789abcdef') for _ in range(length))


def open_cell(field, x, y, action='open'):
    height = len(field)
    width = len(field[0])
    
    def open_adjacent_zeros(field, x, y):
        """Рекурсивно открывает соседние клетки, если текущая клетка содержит 0."""
        stack = [(x, y)]
        visited = set()

        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))
            
            # Открываем текущую клетку
            field[cy][cx]['opened'] = True

            if field[cy][cx]['value'] == 0:
                # Проверяем все соседние клетки
                for x_offset in range(-1, 2):
                    for y_offset in range(-1, 2):
                        nx, ny = cx + x_offset, cy + y_offset
                        if (x_offset == 0 and y_offset == 0) or not (0 <= nx < width and 0 <= ny < height):
                            continue
                        if not field[ny][nx]['opened'] and field[ny][nx]['value'] != -1:
                            stack.append((nx, ny))
            # Если клетка с цифрой (1, 2, 3 и т.д.), просто открываем её

    if action == 'flag':
        # Переключаем флаг
        if field[y][x]['flag']:
            field[y][x]['flag'] = False
        else:
            field[y][x]['flag'] = True
        return field
    else:
        # Если клетка уже открыта или помечена флагом, ничего не делаем
        if field[y][x]['opened'] or field[y][x]['flag']:
            return field
        
        # Открываем клетку
        field[y][x]['opened'] = True
        
        # Если это ноль, запускаем рекурсивное открытие соседних клеток
        if field[y][x]['value'] == 0:
            open_adjacent_zeros(field, x, y)

        return field


def get_fields_for_room(room):
    result = {}
    local_result = []
    for target_user in ROOMS[room]:
        for field_owner in ROOMS[room]:
            if field_owner == target_user:
                continue
            
            field = ROOMS[room][field_owner]['field']
            if field is None:
                field = [[{'value': -3, 'opened': False, 'flag': False} for _ in range(15)] for _ in range(15)]

            local_result.append(field)

        result[target_user] = local_result
        local_result = []
        
    return result