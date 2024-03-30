import pygame
import math
import random
from helldivers import get_wars, get_war_planets

import math

def random_color():
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    return color

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
line_size = 2

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
circles = generate_concentric_circles_radii(furthest * scaling_factor * 2, 10)

cx, cy, r = center[0], center[1], furthest * scaling_factor
print(furthest * scaling_factor)

gridlines = generate_circle_lines(furthest * scaling_factor, 12, center, scaling_factor)

'''
absolute garbage code
'''
colors = []
for i in range(10):
    print(i)
    while True:
        newcolor = random_color()
        unique = True
        for c in colors:
            if c[0] == newcolor[0] and c[1] == newcolor[1] and c[2] == newcolor[2]:
                unique = False
                break
        if unique:
            print('unique')
            colors.append(newcolor)
            break

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if should_draw:
        screen.fill((255, 255, 255))
        pygame.draw.circle(screen, (0, 0, 0), (cx, cy), r)
        for i in range(len(circles)):
            print(circles[i])
            pygame.draw.circle(screen, colors[i], center, circles[i])

        for p in planets_rects:
            pygame.draw.circle(screen, (255, 0, 0), p, planet_size)
        for l in lines:
            pygame.draw.line(screen, (255, 255, 255), l[0], l[1], line_size)
        for line in gridlines:
            pygame.draw.line(screen, (255, 255, 255), line[0], line[1], line_size)
        pygame.display.flip()
        should_draw = False
pygame.quit()