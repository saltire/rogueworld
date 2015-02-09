import math
import random

from PIL import Image


width = 160
height = 90
cells = {}


# generate cities

citycount = 5
cities = []
distance = 10

while len(cities) < citycount:
    x = random.randint(0, width - 1)
    y = random.randint(0, height - 1)

    reject = False
    for cx, cy in cities:
        if abs(x - cx) < distance or abs(y - cy) < distance:
            reject = True
            break

    if reject:
        continue

    cities.append((x, y))
    cells[x, y] = 'city'
print(cities)


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

        angle = math.degrees(math.atan2(ny - cy, nx - cx)) + 180
        rangle = (angle + 180) % 360
        reject = False
        for pangle in paths[cx, cy]:
            diff = abs(pangle - angle)
            if diff < minangle or diff > 360 - minangle:
                reject = True
                break
        for pangle in paths[nx, ny]:
            diff = abs(pangle - rangle)
            if diff < minangle or diff > 360 - minangle:
                reject = True
                break

        if reject:
            continue

        if len(paths[cx, cy]) > minpaths and len(paths[nx, ny]) == maxpaths:
            break

        paths[cx, cy].append(angle)
        paths[nx, ny].append(rangle)

        x, y = cx, cy
        backdir = None
        while (abs(nx - x) + abs(ny - y) > 1):
            dirs = [d for d in range(4) if d != backdir] * base

            if ny < y and backdir != 0:  # north
                dirs += [0] * (fwt + (y - ny) * pwt)
            if nx > x and backdir != 1:  # east
                dirs += [1] * (fwt + (nx - x) * pwt)
            if ny > y and backdir != 2:  # south
                dirs += [2] * (fwt + (ny - y) * pwt)
            if nx < x and backdir != 3:  # west
                dirs += [3] * (fwt + (x - nx) * pwt)

            direction = random.choice(dirs)

            if direction == 0 and y > 0:
                y -= 1
            elif direction == 1 and x < width - 1:
                x += 1
            elif direction == 2 and y < height - 1:
                y += 1
            elif direction == 3 and x > 0:
                x -= 1

            if (x, y) not in cells:
                cells[x, y] = 'path'

            backdir = (direction + 2) % 4


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
