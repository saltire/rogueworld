class Cell:
    def __init__(self):
        # dict indexed by destination coords,
        # containing a list of tuples with the distance to the destination along a certain route
        # and the coords of the next step on that route
        self.dests = {}


# follow a list of coordinates, marking the distance back to the origin at each step
def blaze_path(cells, start, path):
    origin_dists = get_origin_distances(cells, start)
    px, py = start
    distance = 0
    for x, y in path:
        # create a cell at the next step in the path
        cell = cells.setdefault((x, y), Cell())

        # set the previous step and cumulative distance to all the origin points we are tracking
        distance += 1
        for origin, odist in origin_dists:
            cell.dests.setdefault(origin, set()).add({'step': (px, py),
                                                      'distance': odist + distance})
        px, py = x, y


# follow the shortest path from the start to the destination,
# marking the distances back to a set of origin points at each step
def follow_path(cells, start, dest):
    origin_dists = get_origin_distances(cells, start)
    px, py = start
    distance = 0
    while True:
        # find the next step on the shortest path to the destination
        _, x, y = sorted(cells[px, py].dests[dest])[0]
        cell = cells[x, y]

        # set the previous step and cumulative distance to all the origin points we are tracking
        distance += 1
        for origin, odist in origin_dists:
            cell.dests.setdefault(origin, set()).add({'step': (px, py),
                                                      'distance': odist + distance})
        px, py = x, y


def get_shortest_route(routes):
    return sorted(routes, lambda x, y: cmp(x.distance, y.distance))[0]


def get_origin_distances(cells, origin):
    # get the coordinates and shortest distance to each city connected to the origin
    origin_dists = set((dest, get_shortest_route(routes).distance)
                       for dest, routes in cells[origin].dests.items())
    # including the origin itself
    origin_dists.add((origin, 0))
    return origin_dists


def link_cities(origin, dest):
    current = origin
    distance = 0
    while True:
        path = get_path(origin, current, dest)
        newcell = path[-1]

        if origin in cells[newcell].dests:
            # there is already a path from origin to here - don't blaze a new one
            # even if it's longer than the current path
            current = newcell
            distance = get_shortest_route(cells[newcell].dests[origin]).distance
            continue

        # mark the route from the current coord to the end of the path
        blaze_path(cells, current, path)

        # TODO: change routes so it holds a single shortest route instead of a set
        routes = cells[newcell].routes
        routes[newcell] = 0, newcell
        for distance, (x, y) in cells[newcell].routes.values():
            propagate_to(cells[x, y], routes)


def propagate_to(cell, routes):
    # figure out which of the new routes are in fact new or shorter
    added_routes = {}
    for (rx, ry), (distance, (x, y)) in routes:
        distance += 1
        existing_dist, _ = cell.routes.get((rx, ry), (None, None))
        if existing_dist is None or distance < existing_dist:
            added_routes[rx, ry] = distance, (x, y)

    # update this cell's routes with the new/shorter ones
    cell.routes.update(added_routes)

    # propagate the new/shorter routes along all the other routes
    for rx, ry in cell.routes:
        if rx, ry not in added_routes:
            propagate_to(cells[rx, ry], added_routes)
