import random

def generate_field(WIDHT, HEIGHT, BOMB_PROCENTAGE):
    field = [[0] * WIDHT for _ in range(HEIGHT)] # создаем поле

    # раскидываем бомбы
    for _ in range(int(WIDHT * HEIGHT * BOMB_PROCENTAGE)):
        x = random.randint(0, WIDHT - 1)
        y = random.randint(0, HEIGHT - 1)

        if field[y][x] != -1:
            field[y][x] = -1

    for y in range(HEIGHT):
        for x in range(WIDHT):
            if field[y][x] == -1:
                continue

            for x_offset in range(-1, 2):
                for y_offset in range(-1, 2):
                    if x_offset == 0 and y_offset == 0:
                        continue
                    if x + x_offset < 0 or x + x_offset >= WIDHT:
                        continue
                    if y + y_offset < 0 or y + y_offset >= HEIGHT:
                        continue

                    if field[y + y_offset][x + x_offset] == -1:
                        field[y][x] += 1


def generate_key(length):
    return ''.join(random.choice('0123456789abcdef') for _ in range(length))