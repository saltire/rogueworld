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
        self.dests = {}


class City(Cell):
    def __init__(self):
        Cell.__init__(self)

        self.paths = set()


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
        cx = random.randint(0, width - 1)
        cy = random.randint(0, height - 1)

        if not city_isolated(cx, cy, cities, distance):
            continue

        cities.append((cx, cy))

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


def get_direction(x1, y1, x2, y2):
    return [(0, -1), (1, 0), (0, 1), (-1, 0)].index((x2 - x1, y2 - y1))


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

        path = [(cx, cy)]
        x, y = cx, cy
        while (abs(nx - x) + abs(ny - y) > 1):
            def pick_weighted_dir(x, y, nx, ny, lx, ly):
                # cells to the N, E, S, W
                ncells = [(x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y)]
                # distance to travel N, E, S, W
                deltas = [y - ny, nx - x, ny - y, x - nx]

                # calculate weights for each direction and make a weighted list
                dirs = []
                for ndir in range(4):
                    ncell = ncells[ndir]

                    # skip this direction if we can't enter or it leads backward
                    if not can_enter(ncell) or (nx, ny) == (lx, ly):
                        continue

                    dirs += [ndir] * (base + ((fwt + deltas[ndir] * pwt)
                                              if deltas[ndir] > 0 else 0))

                # pick a direction from the weighted list and get the next cell
                return ncells[random.choice(dirs)]

            lx, ly = path[-2] if len(path) > 1 else (None, None)

            if (x, y) in cells and (nx, ny) in cells[x, y].dests:
                x, y = cells[x, y].dests[nx, ny]
            else:
                x, y = pick_weighted_dir(x, y, nx, ny, lx, ly)

            if (x, y) in path:
                # truncate path to just before first pass through this cell
                path = path[:path.index((x, y))]

            path.append((x, y))

        path.append((nx, ny))
        for i, (x, y) in enumerate(path):
            cell = cells.setdefault((x, y), Path())
            if i < len(path) - 1:
                cell.dests[nx, ny] = path[i + 1]
                cell.exits.add(get_direction(x, y, *path[i + 1]))

            if i > 0:
                cell.dests[cx, cy] = path[i - 1]
                cell.exits.add(get_direction(x, y, *path[i - 1]))




# generate map image

img = Image.new('RGB', (width, height))
pix = img.load()
for y in range(height):
    for x in range(width):
        if (x, y) not in cells:
            continue
        if isinstance(cells[x, y], City):
            pix[x, y] = 255, 0, 0
        elif isinstance(cells[x, y], Path):
            pix[x, y] = 255, 255, 255

img.save('map.png')
