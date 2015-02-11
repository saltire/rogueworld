import random


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
