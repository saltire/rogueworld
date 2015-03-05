import random


def place_cities(width, height, citycount, distance):
    cities = []

    while len(cities) < citycount:
        cx = random.randint(0, width - 1)
        cy = random.randint(0, height - 1)

        if any((abs(nx - cx) < distance or abs(ny - cy) < distance)
               for nx, ny in cities):
            continue

        cities.append((cx, cy))

    return cities
