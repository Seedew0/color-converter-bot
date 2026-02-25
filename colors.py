# colors.py
import colorsys
import re


def hex_to_rgb(hex_color):
    """Конвертирует HEX в RGB"""
    # Убираем # если есть
    hex_color = hex_color.lstrip('#').upper()

    # Проверяем формат (3 или 6 символов)
    if len(hex_color) == 3:
        hex_color = ''.join([c * 2 for c in hex_color])

    if len(hex_color) != 6:
        return None

    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)
    except ValueError:
        return None


def rgb_to_hex(r, g, b):
    """Конвертирует RGB в HEX"""
    return '#{:02X}{:02X}{:02X}'.format(r, g, b)


def rgb_to_hsl(r, g, b):
    """Конвертирует RGB в HSL"""
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0

    h, l, s = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)

    h = round(h * 360)
    s = round(s * 100)
    l = round(l * 100)

    return (h, s, l)


def rgb_to_cmyk(r, g, b):
    """Конвертирует RGB в CMYK"""
    if r == 0 and g == 0 and b == 0:
        return (0, 0, 0, 100)

    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0

    k = 1 - max(r_norm, g_norm, b_norm)
    c = (1 - r_norm - k) / (1 - k) * 100 if (1 - k) != 0 else 0
    m = (1 - g_norm - k) / (1 - k) * 100 if (1 - k) != 0 else 0
    y = (1 - b_norm - k) / (1 - k) * 100 if (1 - k) != 0 else 0
    k = k * 100

    return (round(c), round(m), round(y), round(k))


def parse_rgb(rgb_string):
    """Парсит RGB из строки вида '255, 128, 0' или '255 128 0'"""
    # Убираем все лишнее и разбиваем по пробелам или запятым
    rgb_string = rgb_string.replace(',', ' ').strip()
    parts = rgb_string.split()

    if len(parts) != 3:
        return None

    try:
        r = int(parts[0])
        g = int(parts[1])
        b = int(parts[2])

        # Проверяем диапазон
        if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
            return (r, g, b)
        return None
    except ValueError:
        return None


def is_valid_hex(hex_color):
    """Проверяет, является ли строка валидным HEX-кодом"""
    hex_color = hex_color.lstrip('#').upper()
    pattern = r'^[0-9A-F]{3}$|^[0-9A-F]{6}$'
    return re.match(pattern, hex_color) is not None