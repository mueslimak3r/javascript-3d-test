import pygame
import math

from helldivers import get_wars, get_war_planets
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
print(planets)
lines = []
scaling_factor = 4
planet_size = 4
line_size = 2

planets_rects = []
center = screen.get_rect().center
furthest = 0

for p in planets:
    print(p)
    
    print(center)
    x = p['position']['x']
    y = p['position']['y']
    if abs(x) > furthest:
        furthest = abs(x)
    if abs(y) > furthest:
        furthest = abs(y)

    planets_rects.append((center[0] - (-x * scaling_factor), center[1] - (y * scaling_factor)))
    #pygame.draw.circle(screen, (255, 0, 100), (center[0] - (-x * scaling_factor), center[1] - (y * scaling_factor)), planet_size)
    for l in p['waypoints']:
        startx = center[0] - (-p['position']['x'] * scaling_factor)
        starty = center[1] - (y * scaling_factor)
        endx = center[0] - (-planets[l]['position']['x'] * scaling_factor)
        endy = center[1] - (planets[l]['position']['y'] * scaling_factor)
        lines.append(((startx, starty), (endx, endy)))

# Center and radius of pie chart
cx, cy, r = center[0], center[1], furthest * scaling_factor



while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if should_draw:
        screen.fill((255, 255, 255))
        pygame.draw.circle(screen, (0, 0, 0), (cx, cy), r)
        '''
        pygame.draw.circle(
            screen,  # Surface to draw on
            [100, 100, 100],  # Color in RGB Fashion
            center,  # Center
            furthest * scaling_factor,  # Radius
        )
        '''
        for p in planets_rects:
            pygame.draw.circle(screen, (255, 0, 0), p, planet_size)
        for l in lines:
            pygame.draw.line(screen, (255, 255, 255), l[0], l[1], line_size)
        # pygame.draw.circle(screen, (0, 0, 255), (250, 250), 75)
        pygame.display.flip()
        should_draw = False
pygame.quit()