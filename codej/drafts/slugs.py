from slugify import Slugify


def make(title):
    make_slug = Slugify(max_length=108, to_lower=True)
    return make_slug(title)


def parse_match(match):
    return [each.get('slug') for each in match]


def check_max(match, slug):
    maxi = 0
    for each in match:
        try:
            n = abs(int(each.split(slug)[1]))
        except ValueError:
            n = 0
        if n > maxi:
            maxi = n
    return maxi
