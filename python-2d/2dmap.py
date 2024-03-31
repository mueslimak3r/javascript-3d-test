import pygame
import math
import random
from helldivers import get_wars, get_war_planets
import json
import math

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
        radius = original_radius - (i - 1) * radius_decrement
        concentric_circles_radii.append(radius)

    return concentric_circles_radii

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
            print('index %s adjacent index %s' % (i, adjacent_index))
            adjacent_start, adjacent_end = get_points2(angle_increment, adjacent_index, radii, rx)
            print('start %s end %s' % (start, end))
            print('adjacent start %s end %s' % (adjacent_start, adjacent_end))
            tmpcenter = (0, 0)
            newsection = [
                            (start, end, 0, (0, 0)),
                            (adjacent_start, adjacent_end, 0, (0, 0)),
                            (start, adjacent_start, 0 if rx == 0 else radii[rx - 1], (math.atan2(start[1] - tmpcenter[1], start[0] - tmpcenter[0]), math.atan2(adjacent_start[1] - tmpcenter[1], adjacent_start[0] - center[0]))),
                            (end, adjacent_end, radii[rx], (math.atan2(end[1] - tmpcenter[1], end[0] - tmpcenter[0]), math.atan2(adjacent_end[1] - tmpcenter[1], adjacent_end[0] - center[0])))
                        ]
            
            name = ''
            for n in newsection:
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


for p in planets:
    x = p['position']['x']
    y = p['position']['y']
    if abs(x) > furthest:
        furthest = abs(x)
    if abs(y) > furthest:
        furthest = abs(y)

    planets_rects.append((center[0] - (-x * scaling_factor), center[1] - (y * scaling_factor)))
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
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if should_draw:
        #screen.fill((0, 0, 0))
        screen.fill((255, 255, 255))
        pygame.draw.circle(screen, (0, 0, 0), (cx, cy), r)
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
        for lx in range(len(sectionkeys)):
            obj = sections[sectionkeys[lx]]
            if obj[0][0][0] == 0:
                continue
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
        pygame.display.flip()
        should_draw = False
pygame.quit()