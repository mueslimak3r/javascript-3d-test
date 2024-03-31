import pygame
import math
import random
from helldivers import get_wars, get_war_planets
import json
import shapely.geometry
import math
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
    start = (0, 0) if rx == 0 else get_grid_point(angle_radians, radii[rx - 1])
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


def generate_curve_points(p1, p2, center, radius=10):
    arc_length_per_point = 2
    theta_start_rad = math.atan2(p1[1] - center[1], p1[0] - center[0])
    theta_end_rad = math.atan2(p2[1] - center[1], p2[0] - center[0])
    theta_start_deg = math.degrees(theta_start_rad)
    theta_end_deg = math.degrees(theta_end_rad)
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
lines = []
scaling_factor = 4
planet_size = 4
line_size = 5

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
    planet_points.append(planet_point)
    for l in p['waypoints']:
        startx = center[0] - (-p['position']['x'] * scaling_factor)
        starty = center[1] - (y * scaling_factor)
        endx = center[0] - (-planets[l]['position']['x'] * scaling_factor)
        endy = center[1] - (planets[l]['position']['y'] * scaling_factor)
        lines.append(((startx, starty), (endx, endy)))

radii = furthest if furthest % 10 == 0 else furthest + 10
units_from_center = int(radii / 10)
units_around = 24

sections = {}
circles = generate_concentric_circles_radii(radii * scaling_factor * 2, units_from_center)
gridlines, sections = generate_grid_points(units_around, circles)
cx, cy, r = center[0], center[1], radii * scaling_factor #furthest * scaling_factor
print(furthest * scaling_factor)
printed_sections = 0
print('POLYGONS')
for s in sections:
    if printed_sections < 10:
        print(sections[s]['polygon'])
        printed_sections += 1
print('PLANETS')

sectors = {}

for px in len(planet_points):
    p = planet_points[px]
    found = False
    for s in sections:
        if sections[s]['polygon'].contains(p):
        #if p.within(sections[s]['polygon']):
            sections[s]['show'] = True
            sector = planets[px]['sector']
            if sector not in sectors:
                sectors[sector] = []
                sectors[sector].append = sections[s]['polygon']
            else:
                if sections[s]['polygon'] not in sectors[sector]:
                    sectors[sector].append = sections[s]['polygon']
            found = True
            #print('showing %s' % s)
            break
    if not found:
        print('not found')
        print(p)

#for sectorkey in sectors.keys():


    #print(p)
#print(json.dumps(sections, indent=4))
#gridlines = generate_circle_lines(furthest * scaling_factor, 24, center, scaling_factor)

'''
absolute garbage code
'''
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
            #print('unique')
            colors.append(newcolor)
            break
#print(gridlines)
index = 0
screen.fill((255, 255, 255))
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if should_draw:
        screen.fill((0, 0, 0))
        #screen.fill((255, 255, 255))
        #pygame.draw.circle(screen, (0, 0, 0), (cx, cy), r)
        #for i in range(len(circles)):
            #print(circles[i])
            #pygame.draw.circle(screen, colors[i], center, circles[i])

        for p in planets_rects:
            pygame.draw.circle(screen, (255, 0, 0), p, planet_size)
        for l in lines:
            pygame.draw.line(screen, (255, 255, 255), l[0], l[1], line_size)
        sectionkeys = list(sections.keys())
        #pygame.draw.arc(screen, (255, 255, 255), (50, 50, 100, 100), ((12+90)/57), ((42+90)/57), 1)
        #pygame.draw.arc(screen, (255, 255, 255), (100, 100, 900, 900), 9, 48, width=10)
        #if index < len(sectionkeys):
        #    lx = index
        for lx in range(len(sectionkeys)):
            baseobj = sections[sectionkeys[lx]]
            #print(baseobj['show'])
            obj = baseobj['lines']
            #if obj[0][0][0] == 0:
            #    continue
            if not baseobj['show']:
                continue
            sectioncoords = baseobj['polygon'].exterior.coords
            for i in range(len(sectioncoords) - 1):
                pygame.draw.line(screen, colors[len(circles) + lx],
                                (center[0] - sectioncoords[i][0], center[1] - sectioncoords[i][1]),
                                (center[0] - sectioncoords[i + 1][0], center[1] - sectioncoords[i + 1][1]),
                                5)
            index += 1
            pygame.display.flip()
            sleep(0.02)
            should_draw = False
            continue
            # print('drawing')
            #print(obj)
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
        
pygame.quit()