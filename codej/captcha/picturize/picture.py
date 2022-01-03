import glob
import io
import os
import random

from PIL import Image, ImageFilter
from PIL.ImageFont import truetype
from PIL.ImageDraw import Draw


# the majority of this code is borrowed
# from https://github.com/lepture/captcha with some subtle improvements
# and in accordance with the main target of this application
def check_fonts():
    basedir = os.path.dirname(__file__)
    return [os.path.realpath(each) for each in
            glob.glob(os.path.join(basedir, '*.ttf'))]


def choose_color(start, end, opacity=None):
    red = random.randint(start, end)
    green = random.randint(start, end)
    blue = random.randint(start, end)
    if opacity is None:
        return red, green, blue
    return red, green, blue, opacity


def warp(w, h):
    dx = w * random.uniform(0.1, 0.3)
    dy = h * random.uniform(0.2, 0.3)
    x1 = int(random.uniform(-dx, dx))
    y1 = int(random.uniform(-dy, dy))
    x2 = int(random.uniform(-dx, dx))
    y2 = int(random.uniform(-dy, dy))
    w2 = w + abs(x1) + abs(x2)
    h2 = h + abs(y1) + abs(y2)
    data = (x1, y1, -x1, h2 - y2, w2 + x2, h2 + y2, w2 - x2, -y1)
    return w2, h2, data


def draw_character(c, draw, color):
    fonts = tuple(truetype(n, s) for n in check_fonts()
                  for s in (42, 48, 52))
    font = random.choice(fonts)
    w, h = draw.textsize(c, font=font)
    dx = random.randint(0, 4)
    dy = random.randint(0, 6)
    image = Image.new('RGBA', (w + dx, h + dy))
    Draw(image).text((dx, dy), c, font=font, fill=color)
    image = image.crop(image.getbbox())
    image = image.rotate(random.uniform(-30, 30), Image.BILINEAR, expand=1)
    w2, h2, data = warp(w, h)
    image = image.resize((w2, h2))
    image = image.transform((w, h), Image.QUAD, data)
    return image


def compound(chars, draw, color):
    images = []
    for c in chars:
        if random.random() > 0.5:
            images.append(draw_character(' ', draw, color))
        images.append(draw_character(c, draw, color))
    return images


def create_captcha_image(chars, width, height, color, background):
    image = Image.new('RGB', (width, height), background)
    draw = Draw(image)
    images = compound(chars, draw, color)
    text_width = sum(i.size[0] for i in images)
    width_ = max(text_width, width)
    image = image.resize((width_, height))
    average = int(text_width / len(chars))
    rand = int(0.25 * average)
    offset = int(average * 0.1)
    table = [i * 1.97 for i in range(256)]
    for each in images:
        w, h = each.size
        mask = each.convert('L').point(table)
        image.paste(each, (offset, int((height - h) / 2)), mask)
        offset = offset + w + random.randint(-rand, 0)
    if width_ > width:
        image = image.resize((width, height))
    return image


def create_noise_dots(image, color, width=3, number=30):
    draw = Draw(image)
    w, h = image.size
    while number:
        x1 = random.randint(0, w)
        y1 = random.randint(0, h)
        draw.line(((x1, y1), (x1 - 1, y1 - 1)), fill=color, width=width)
        number -= 1


def create_noise_curve(image, color):
    w, h = image.size
    x1 = random.randint(0, int(w / 5))
    x2 = random.randint(w - int(w / 5), w)
    y1 = random.randint(int(h / 5), h - int(h / 5))
    y2 = random.randint(y1, h - int(h / 5))
    points = [x1, y1, x2, y2]
    end = random.randint(160, 200)
    start = random.randint(0, 20)
    Draw(image).arc(points, start, end, fill=color)


def generate_image(chars='hello', width=120, height=60, file_type='jpeg'):
    background = choose_color(238, 255)
    color = choose_color(10, 200, random.randint(220, 255))
    image = create_captcha_image(chars, width, height, color, background)
    create_noise_dots(image, color)
    create_noise_curve(image, color)
    image = image.filter(ImageFilter.SMOOTH)
    out = io.BytesIO()
    image.save(out, format=file_type)
    out.seek(0)
    return out
