class Cell:
    def __init__(self):
        # dict indexed by destination coords,
        # containing a list of tuples with the distance to the destination along a certain route
        # and the coords of the next step on that route
        self.routes = {}


def can_enter(x, y):
    return x >= 0 and y >= 0 and x < width and y < height


def weight_direction(delta):
    base = 1  # base weight for all directions
    fwt = 25  # flat added weight for desired directions
    pwt = 1   # proportional added weight for desired directions

    return base + ((fwt + pwt * delta) if delta > 0 else 0)


def next_step(prev, current, dest):
    x, y = current
    dx, dy = dest

    # next cell to the N/E/S/W
    ncells = [(x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y)]
    # distance to travel N/E/S/W
    deltas = [y - dy, dx - x, dy - y, x - dx]

    # calculate weights for each direction and make a weighted list
    choices = []
    for ndir in range(4):
        ncell = ncells[ndir]

        # skip this direction if we can't enter or it leads backward
        if not can_enter(*ncell) or ncell == prev:
            continue

        # add to the choices list a weighted number of times
        choices += [ncell] * weight_direction(deltas[ndir])

    # pick a direction from the weighted list and get the next cell
    return random.choice(choices)


# pick steps toward a destination cell, returning when we hit an existing cell
def find_path(cells, start, dest):
    path = []
    prev = None, None
    current = start
    while True:
        nextcell = next_step(prev, current, dest)
        path.append(nextcell)
        if isinstance(cells.get(nextcell), Cell):
            return path

        prev = current
        current = nextcell


# add a set of new routes to a cell, and propagate them along that cell's existing routes
def propagate_routes_to(cells, prev, current, routes):
    new_routes = {}

    for dest, (rdist, _) in routes.items():
        rdist += 1
        existing_dist, _ = cells[current].routes.get(dest, (None, None))

        # figure out which of the new routes are in fact new or shorter
        # then save them and keep track of whether we made changes
        if existing_dist is None or rdist < existing_dist:
            cells[current].routes[dest] = rdist, prev
            new_routes[dest] = cells[current].routes[dest]

    # propagate the new routes along all the unchanged routes
    for dest, (_, nextstep) in cells[current].routes.items():
        if dest not in new_routes:
            propagate_routes_to(cells, current, nextstep, new_routes)


# follow a list of coordinates, marking the distance back to the origin at each step
def blaze_path(cells, prev, path):
    start_routes = cells[prev].routes
    distance = 0

    for current in path:
        distance += 1

        # create a cell at every step except the last one, which should already be a cell
        if current != path[-1]:
            cells[current] = Cell()
            # continue each of the origin cell's routes in this cell
            for dest, (rdist, _) in start_routes.items():
                cells[current].routes[dest] = rdist + distance, prev

            prev = current

    # now do the last cell, and propagate routes across the new connection
    new_routes = {}
    # we will be sending routes from this cell back along any new/shorter routes
    back_routes = {current: 0, None}

    # figure out which of the new routes are in fact new or shorter
    for dest, (rdist, _) in start_routes.items():
        rdist += distance
        existing_dist, _ = cells[current].routes.get(dest, (None, None))

        # figure out which of the new routes are in fact new or shorter
        # then save them and keep track of whether we made changes or not
        if existing_dist is None or rdist < existing_dist:
            cells[current].routes[dest] = rdist, prev
            new_routes[dest] = cells[current].routes[dest]
        else:
            back_routes[dest] = cells[current].routes[dest]

    # propagate the new routes along all the unchanged routes, and vice versa
    for dest, (_, nextstep) in cells[current].routes.items():
        propagate_routes_to(cells, current, nextstep,
                            back_routes if dest in new_routes else new_routes)


def link_cities(cells, origin, dest):
    current = origin
    distance = 0
    while current != dest:
        # find the next leg of the path from the current cell to the destination
        start = current
        path = find_path(start, dest)
        current = path[-1]

        if origin in cells[current].dests:
            # there is already a path from origin to here - don't blaze a new one
            # even if the existing one is longer
            distance, _ = cells[current].routes[origin]
            continue

        # mark the route from the current coord to the end of the path
        blaze_path(cells, start, path)

        if current == dest:
            break
