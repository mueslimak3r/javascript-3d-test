import pygame
import math
import random
from helldivers import get_wars, get_war_planets, get_sectors
import json
import shapely.geometry
from shapely.ops import unary_union
import math
from shapely.validation import make_valid
import geopandas as gpd
from time import sleep

def random_color():
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    return color

def calculate_arc_angles(x1, y1, x2, y2, radius):
    print(x1, y1, x2, y2, radius)
    # Validate the points are on the circle's perimeter
    assert math.isclose(x1**2 + y1**2, radius**2, abs_tol=1e-9) and math.isclose(x2**2 + y2**2, radius**2, abs_tol=1e-9), "Points are not on the circle's perimeter"
    
    # Calculate angles in radians
    angle1 = math.atan2(y1, x1)
    angle2 = math.atan2(y2, x2)
    
    # Convert angles to degrees
    angle1_deg = math.degrees(angle1)
    angle2_deg = math.degrees(angle2)
    
    return angle1_deg, angle2_deg

def generate_concentric_circles_radii(original_diameter, number_of_circles):
    original_radius = original_diameter / 2.0
    radius_decrement = original_radius / number_of_circles
    concentric_circles_radii = []

    for i in range(1, number_of_circles + 1):
        #radius = 0 + (i - 1) * radius_decrement
        radius = original_radius - (i - 1) * radius_decrement
        concentric_circles_radii.append(radius)
    return sorted(concentric_circles_radii, reverse=False)

def generate_circle_lines(diameter, intersections, center, scaling_factor):
    radius = diameter / 2.0
    angle_increment = (2 * math.pi) / intersections
    lines = []

    for i in range(intersections):
        angle_radians = angle_increment * i
        x = radius * math.cos(angle_radians)
        y = radius * math.sin(angle_radians)
        lines.append((center, (center[0] - (x * scaling_factor), center[1] - (y * scaling_factor))))
    
    return lines

def get_grid_point(angle_radians, radius):
    x = radius * math.cos(angle_radians)
    y = radius * math.sin(angle_radians)
    return (x, y)

def get_points2(angle_increment, index, radii, rx):
    angle_radians = angle_increment * index
    start = (1.0, 1.0) if rx == 0 else get_grid_point(angle_radians, radii[rx - 1])
    end = get_grid_point(angle_radians, radii[rx])
    return start, end

def generate_arc_points(radius, theta_start_deg, theta_end_deg, arc_length_per_point=1):
    # Convert angles from degrees to radians
    theta_start = math.radians(theta_start_deg)
    theta_end = math.radians(theta_end_deg)
    
    # Ensure theta_end is greater than theta_start
    if theta_start > theta_end:
        theta_start, theta_end = theta_end, theta_start
    
    delta_theta = theta_end - theta_start
    
    # Calculate arc length
    arc_length = radius * abs(delta_theta)
    
    # Determine the number of points based on arc length
    num_points = max(int(arc_length / arc_length_per_point), 2)  # Ensure at least 2 points
    
    # Generate points along the arc
    points = []
    for i in range(num_points):
        theta = theta_start + (i / (num_points - 1)) * delta_theta
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        points.append((x, y))
    
    return points

def adjust_angle_difference(theta_start, theta_end):
    # Normalize angles to [0, 2*pi) range
    theta_start = theta_start % (2 * math.pi)
    theta_end = theta_end % (2 * math.pi)

    # Calculate the shortest path difference
    diff = theta_end - theta_start
    if diff < 0:
        diff += 2 * math.pi  # Adjust if we're going the long way around
    
    # Now, choose the direction that results in the shortest arc
    if diff > math.pi:
        # The arc is trying to go the long way around; adjust it
        if theta_end > theta_start:
            theta_end -= 2 * math.pi
        else:
            theta_start -= 2 * math.pi

    return theta_start, theta_end

def generate_curve_points(point1, point2, center, radius=10):
    p1 = point1
    p2 = point2
    arc_length_per_point = 6
    theta_start_rad = math.atan2(p1[1] - center[1], p1[0] - center[0])
    theta_end_rad = math.atan2(p2[1] - center[1], p2[0] - center[0])
    theta_start, theta_end = adjust_angle_difference(theta_start_rad, theta_end_rad)
    theta_start_deg = math.degrees(theta_start)
    theta_end_deg = math.degrees(theta_end)
    points = generate_arc_points(radius, theta_start_deg, theta_end_deg, arc_length_per_point)
    return points


def generate_grid_points(intersections, radii):
    angle_increment = (2 * math.pi) / intersections
    lines = []
    sections = {}
    '''
    "00002": [
        ((0, 0), (0, 0), radius/curve)
    ]
    '''

    for rx in range(len(radii)):
        for i in range(intersections):
            start, end = get_points2(angle_increment, i, radii, rx)
            adjacent_index = i + 1 if i + 1 < intersections else 0
            #print('index %s adjacent index %s' % (i, adjacent_index))
            adjacent_start, adjacent_end = get_points2(angle_increment, adjacent_index, radii, rx)
            #print('start %s end %s' % (start, end))
            #print('adjacent start %s end %s' % (adjacent_start, adjacent_end))
            tmpcenter = (0, 0)
            polygon_points = []
            #polygon_points.append(adjacent_start)
            polygon_points.append(adjacent_start)
            polygon_points.append(adjacent_end)
            polygon_points.append(end)
            polygon_points.append(start)
            polygon_points.append(adjacent_start)
            #polygon_points.append(end)
            #polygon_points.append(start)
            #polygon_points.append(adjacent_start)
            '''
            if angle_increment * i >= angle_increment * adjacent_index:
                polygon_points.append(adjacent_start)
                polygon_points.append(adjacent_end)
                polygon_points.append(end)
                polygon_points.append(start)
                polygon_points.append(adjacent_start)
            elif end[1] > adjacent_end[1]:
                polygon_points.append(adjacent_start)
                polygon_points.append(adjacent_end)
                polygon_points.append(end)
                polygon_points.append(start)
                polygon_points.append(adjacent_start)
            else:
                polygon_points.append(start)
                polygon_points.append(end)
                polygon_points.extend(generate_curve_points(end, adjacent_end, tmpcenter, radii[rx]))
                polygon_points.append(adjacent_end)
                polygon_points.append(adjacent_start)
                polygon_points.extend(generate_curve_points(adjacent_start, start, tmpcenter, radii[rx - 1] if rx > 0 else 0.0))
                polygon_points.append(start)
            '''
            #polygon_points.append(adjacent_end)
            
            #polygon_points.append(end)
            #print(polygon_points)
            #polygon_points = sorted(polygon_points, key=lambda x: math.atan2(x[1] - tmpcenter[1], x[0] - tmpcenter[0]))
            newsection = {
                "polygon": shapely.geometry.Polygon(polygon_points),
                "show": False,
                "lines": [
                    (start, end, 0, (0, 0)),
                    (adjacent_start, adjacent_end, 0, (0, 0)),
                    (start, adjacent_start, 0 if rx == 0 else radii[rx - 1], (math.atan2(start[1] - tmpcenter[1], start[0] - tmpcenter[0]), math.atan2(adjacent_start[1] - tmpcenter[1], adjacent_start[0] - center[0]))),
                    (end, adjacent_end, radii[rx], (math.atan2(end[1] - tmpcenter[1], end[0] - tmpcenter[0]), math.atan2(adjacent_end[1] - tmpcenter[1], adjacent_end[0] - center[0])))
                ]
            }
            name = ''
            for n in newsection['lines']:
                name += str(n[0][0]) + str(n[0][1]) + str(n[1][0]) + str(n[1][1])
            sections[name] = newsection
            lines.append((start, end))
    return lines, sections

def make_union_polygon(poly_list=[]):
    if len(poly_list) == 0:
        return None
    result = unary_union([ p.simplify(tolerance=0.001, preserve_topology=True) for p in poly_list ]).buffer(0)
    return result
    #return result if type(result) is shapely.geometry.Polygon else unary_union(shapely.delaunay_triangles(result, tolerance=0.05, only_edges=True).geoms)
    '''
    buffer_size = 0.00001
    buffered_poly = []
    for p in poly_list:
        buffered_poly.append(p.buffer(buffer_size))
    
    if len(poly_list) == 1:
        union_poly = buffered_poly[0]
    else:
        union_poly = unary_union(buffered_poly)

    # Step 2: Convex Hull (if you want to ensure all gaps are filled)
    #convex_hull_poly = union_poly.buffer(-buffer_size).convex_hull

    #unbuffered_poly = convex_hull_poly.buffer(-buffer_size)
    return union_poly.buffer(-buffer_size) #convex_hull_poly
    '''
    

pygame.init()

screen = pygame.display.set_mode([1000, 1000])
running = True
should_draw = True
wars = get_wars()
if not wars:
    print('no wars')
    exit(1)
current_war = wars['current']
planets = get_war_planets(current_war)
sector_map = get_sectors()
lines = []
scaling_factor = 4
planet_size = 4
line_size = 1

planets_rects = []
center = screen.get_rect().center
furthest = 0
planet_points = []

printed_points = 0

for p in planets:
    x = p['position']['x']
    y = p['position']['y']
    if abs(x) > furthest:
        furthest = abs(x)
    if abs(y) > furthest:
        furthest = abs(y)

    planets_rects.append((center[0] - (-x * scaling_factor), center[1] - (y * scaling_factor)))
    
    planet_point = shapely.geometry.Point((-x * scaling_factor, y * scaling_factor))
    if printed_points < 10:
        print(planet_point)
        printed_points += 1
    planet_points.append((planet_point, int(p['index']), str(p['name'])))
    for l in p['waypoints']:
        startx = center[0] - (-p['position']['x'] * scaling_factor)
        starty = center[1] - (y * scaling_factor)
        endx = center[0] - (-planets[l]['position']['x'] * scaling_factor)
        endy = center[1] - (planets[l]['position']['y'] * scaling_factor)
        lines.append(((startx, starty), (endx, endy)))

radii = furthest if furthest % 10 == 0 else furthest + (10 - furthest % 10)
units_from_center = int(radii / 10)
units_around = 24

sections = {}
circles = generate_concentric_circles_radii(radii * scaling_factor * 2, units_from_center)
gridlines, sections = generate_grid_points(units_around, circles)
cx, cy, r = center[0], center[1], radii * scaling_factor
print(furthest * scaling_factor)
printed_sections = 0
print('POLYGONS')
for s in sections:
    if printed_sections < 10:
        print(sections[s]['polygon'])
        printed_sections += 1
print('PLANETS')

sectors = {}

for px in range(len(planet_points)):
    p, planet_index, pname = planet_points[px]
    found = False
    tol = 1e-4
    sector = None
    for sm in sector_map.keys():
        if planet_index in sector_map[sm]:
            sector = sm
            break
    if not sector:
        print('no sector found for planet %s %s' % (pname, planet_index))
        continue
    for sk in list(sections.keys()):
        s = sections[sk]
        if s['polygon'].is_valid == False:
            print('invalid')
            print(s)
        if p.within(make_valid(s['polygon'])):
            print('planet %s [%s] %s is in sector %s %s' % (pname, planet_index, p, sector, s['polygon']))
            s['show'] = True
            if sector not in sectors:
                print('adding sector %s' % sector)
                sectors[sector] = make_union_polygon([make_valid(s['polygon'])])
            else:
                try:
                    sectors[sector] = make_union_polygon([sectors[sector], make_valid(s['polygon'])])
                except Exception as e:
                    print(e)
                    print('failed to union')
                    print('sector %s' % sector)
                    print('polygon is valid %s' % make_valid(s['polygon']).is_valid)
                    print('polygon %s' % s['polygon'])
                    print('polygon %s' % sectors[sector])
                    print('corrected polygon %s' % make_valid(s['polygon']))
                    exit(1)
            
            found = True
            break
    if not found:
        print('not found')
        print(p)

printed_sections = 0
print('PLANETS')
for s in planet_points:
    if printed_sections < 25:
        print(s)
        printed_sections += 1
print('END PLANETS')

colors = []
for i in range(len(circles) + len(list(sections.keys()))):
    #print(i)
    while True:
        newcolor = random_color()
        unique = True
        for c in colors:
            if c[0] == newcolor[0] and c[1] == newcolor[1] and c[2] == newcolor[2]:
                unique = False
                break
        if unique:
            colors.append(newcolor)
            break
index = 0
screen.fill((0, 0, 0))
pygame.draw.circle(screen, (194, 194, 194), (cx, cy), r)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if should_draw:
        for p in planets_rects:
            pygame.draw.circle(screen, (255, 0, 0), p, planet_size)
        for l in lines:
            pygame.draw.line(screen, (0, 0, 0), l[0], l[1], line_size)
        
        sectionkeys = list(sections.keys())
        sectorkeys = list(sectors.keys())
        if index < len(sectorkeys):
            lx = index
            sectorgeos = sectors[sectorkeys[lx]]
            print(sectorkeys[lx])
            
            if type(sectorgeos) is shapely.geometry.Polygon:
                sectioncoords = sectorgeos.exterior.coords
                pygame.draw.lines(screen, (0, 0, 0),
                              closed=True,
                              #points=sectioncoords,
                              points=[ (center[0] - x, center[1] - y) for x, y in sectioncoords ],
                              width=2)
            
            if type(sectorgeos) is shapely.geometry.MultiPolygon:
                for poly in sectorgeos.geoms:
                    sectioncoords = poly.exterior.coords
                    pygame.draw.lines(screen, (0, 0, 0),
                                closed=True,
                                #points=sectioncoords,
                                points=[ (center[0] - x, center[1] - y) for x, y in sectioncoords ],
                                width=2)
            
            if type(sectorgeos) is shapely.geometry.LineString:
                print('line')
                sectioncoords = sectorgeos.coords
                pygame.draw.lines(screen, (0, 0, 0),
                                closed=False,
                                #points=sectioncoords,
                                points=[ (center[0] - x, center[1] - y) for x, y in sectioncoords ],
                                width=2)
            index += 1
        else:
            should_draw = False
        sleep(0.25)
        pygame.display.flip()
        '''
        if should_draw == False:
            pygame.display.flip()
            continue
        for lx2 in range(len(sectionkeys)):
        #if index < len(sectionkeys):
            #lx2 = index
            baseobj = sections[sectionkeys[lx2]]
            sectioncoords = baseobj['polygon'].exterior.coords
            sectioncoords = baseobj['polygon'].exterior.coords
            for i in range(len(sectioncoords) - 1):
                pygame.draw.line(screen, colors[len(circles) + lx2],
                                (center[0] - sectioncoords[i][0], center[1] - sectioncoords[i][1]),
                                (center[0] - sectioncoords[i + 1][0], center[1] - sectioncoords[i + 1][1]),
                                5)
            index += 1
            #sleep(0.25)
        else:
            should_draw = False
        #should_draw = False
        pygame.display.flip()
        '''

        '''
        for lx in range(len(sectionkeys)):
            baseobj = sections[sectionkeys[lx]]
            obj = baseobj['lines']
            if not baseobj['show']:
                continue
            pygame.draw.line(screen, colors[len(circles) + lx],
                                (center[0] - obj[0][0][0], center[1] - obj[0][0][1]),
                                (center[0] - obj[0][1][0], center[1] - obj[0][1][1]),
                                5)
            pygame.draw.line(screen, colors[len(circles) + lx],
                                (center[0] - obj[1][0][0], center[1] - obj[1][0][1]),
                                (center[0] - obj[1][1][0], center[1] - obj[1][1][1]),
                                5)
            rect = pygame.Rect(center[0]-obj[2][2], center[1]-obj[2][2], obj[2][2]*2, obj[2][2]*2)
            pygame.draw.arc(screen, colors[len(circles) + lx], rect, obj[2][3][0], obj[2][3][1], 2)
            rect = pygame.Rect(center[0]-obj[3][2], center[1]-obj[3][2], obj[3][2]*2, obj[3][2]*2)
            pygame.draw.arc(screen, colors[len(circles) + lx], rect, obj[3][3][0], obj[3][3][1], 2)
            pygame.display.flip()
            #sleep(0.02)
            should_draw = False
        '''
pygame.quit()