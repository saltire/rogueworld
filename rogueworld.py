import math
import random

from PIL import Image


width = 160
height = 90
cells = {}


class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = {}

    def __setitem__(self, key, value):
        cx, cy = key
        if cx >= width or cy >= height:
            raise ValueError

        self.cells[cx, cy] = value

    def __getitem__(self, key):
        return self.cells[key]


class Cell:
    def __init__(self):
        self.exits = set()
        self.dests = set()


class City(Cell):
    pass


class Path(Cell):
    pass


# generate cities

def place_cities(width, height, citycount, distance):
    cities = []

    def city_isolated(cx, cy, cities, distance):
        for nx, ny in cities:
            if abs(nx - cx) < distance or abs(ny - cy) < distance:
                return False
        return True

    while len(cities) < citycount:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)

        if not city_isolated(cx, cy, cities, distance):
            continue

        cities.append((x, y))

    return cities


citycount = 5
distance = 10
cities = place_cities(width, height, citycount, distance)
for cx, cy in cities:
    cells[cx, cy] = City()


def get_angle(x1, y1, x2, y2):
    return math.degrees(math.atan2(y2 - y1, x2 - x1)) + 180


def reverse_angle(angle):
    return (angle + 180) % 360


def unique_angle(angle, paths, minangle):
    for pangle in paths:
        diff = abs(pangle - angle)
        if diff < minangle or diff > 360 - minangle:
            return False
    return True


def can_enter(ncell):
    x, y = ncell
    return x >= 0 and y >= 0 and x < width and y < height


# draw paths

base = 1  # base weight for all directions
fwt = 25   # flat added weight for desired directions
pwt = 1   # proportional added weight for desired directions

paths = {(cx, cy): [] for cx, cy in cities}
minangle = 10
minpaths = 1
maxpaths = 3
for cx, cy in cities:
    neighbours = sorted([(abs(nx - cx) + abs(ny - cy), nx, ny)
                         for nx, ny in cities
                         if nx != cx and ny != cy])

    for distance, nx, ny in neighbours[:maxpaths]:
        if len(paths[cx, cy]) == maxpaths:
            break

        angle = get_angle(cx, cy, nx, ny)
        rangle = reverse_angle(angle)

        if (not unique_angle(angle, paths[cx, cy], minangle)
                or not unique_angle(rangle, paths[nx, ny], minangle)):
            continue

        if len(paths[cx, cy]) > minpaths and len(paths[nx, ny]) == maxpaths:
            break

        paths[cx, cy].append(angle)
        paths[nx, ny].append(rangle)

        x, y = cx, cy
        backdir = None
        while (abs(nx - x) + abs(ny - y) > 1):
            dirs = []
            ncells = [(x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y)]
            deltas = [y - ny, nx - x, ny - y, x - nx]

            for ndir in range(4):
                if ndir != backdir and can_enter(ncells[ndir]):
                    dirs += [ndir] * (base + ((fwt + deltas[ndir] * pwt)
                                              if deltas[ndir] > 0 else 0))

            direction = random.choice(dirs)
            backdir = (direction + 2) % 4

            x, y = ncells[direction]

            cell = cells.setdefault((x, y), Path())
            cell.dests |= set([(cx, cy), (nx, ny)])
            cell.exits |= set([direction, backdir])


# generate map image

img = Image.new('RGB', (width, height))
pix = img.load()
for y in range(height):
    for x in range(width):
        if (x, y) not in cells:
            continue
        if cells[x, y] == 'city':
            pix[x, y] = 255, 0, 0
        elif cells[x, y] == 'path':
            pix[x, y] = 255, 255, 255

img.save('map.png')
