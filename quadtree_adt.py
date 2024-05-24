def create_quadtree(bounds, capacity):
    return {'bounds': bounds, 'capacity': capacity, 'points': [], 'divided': False}

def insert(quadtree, point):
    if not contains_point(quadtree, point):
        return False

    if len(quadtree['points']) < quadtree['capacity']:
        quadtree['points'].append(point)
        return True
    else:
        if not quadtree['divided']:
            subdivide(quadtree)

        if insert(quadtree['northeast'], point):
            return True
        elif insert(quadtree['northwest'], point):
            return True
        elif insert(quadtree['southeast'], point):
            return True
        elif insert(quadtree['southwest'], point):
            return True

def contains_point(quadtree, point):
    bounds = quadtree['bounds']
    return (bounds[0] <= point[0] < bounds[0] + bounds[2] and
            bounds[1] <= point[1] < bounds[1] + bounds[3])

def subdivide(quadtree):
    bounds = quadtree['bounds']
    x, y, w, h = bounds
    half_width = w // 2
    half_height = h // 2
    capacity = quadtree['capacity']

    quadtree['northeast'] = create_quadtree((x + half_width, y, half_width, half_height), capacity)
    quadtree['northwest'] = create_quadtree((x, y, half_width, half_height), capacity)
    quadtree['southeast'] = create_quadtree((x + half_width, y + half_height, half_width, half_height), capacity)
    quadtree['southwest'] = create_quadtree((x, y + half_height, half_width, half_height), capacity)
    quadtree['divided'] = True

def check_range(quadtree, range):
    found_points = []
    if not intersects(quadtree, range):
        return found_points

    for point in quadtree['points']:
        if range[0] <= point[0] <= range[0] + range[2] and range[1] <= point[1] <= range[1] + range[3]:
            found_points.append(point)

    if quadtree['divided']:
        found_points.extend(check_range(quadtree['northeast'], range))
        found_points.extend(check_range(quadtree['northwest'], range))
        found_points.extend(check_range(quadtree['southeast'], range))
        found_points.extend(check_range(quadtree['southwest'], range))

    return found_points

def intersects(quadtree, range):
    bounds = quadtree['bounds']
    return not (range[0] > bounds[0] + bounds[2] or
                range[1] > bounds[1] + bounds[3] or
                range[0] + range[2] < bounds[0] or
                range[1] + range[3] < bounds[1])

def remove_point(quadtree, point):
    if not contains_point(quadtree, point):
        return False
    if point in quadtree['points']:
        quadtree['points'].remove(point)
        return True
    if quadtree['divided']:
        return (remove_point(quadtree['northeast'], point) or
                remove_point(quadtree['northwest'], point) or
                remove_point(quadtree['southeast'], point) or
                remove_point(quadtree['southwest'], point))
    return False

