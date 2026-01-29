import pygame # For graphical display
import math

print("hi")
def hej():
    print("hej")

PIXELS_PER_DEGREE = 8

#Koordininatsystem:
WIDTH, HEIGHT = 800, 800
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2

def rotate_point(x, y, angle_deg):
    a = math.radians(angle_deg)
    xr = x * math.cos(a) - y * math.sin(a)
    yr = x * math.sin(a) + y * math.cos(a)
    return xr, yr

def world_to_screen(x, y):
    screen_x = CENTER_X + x
    screen_y = CENTER_Y - y   # invertera Y!
    return int(screen_x), int(screen_y)

pitch_deg = 5  # testvärde
roll = 15  # testvärde
y_offset = -pitch_deg * PIXELS_PER_DEGREE
y = -pitch_deg * PIXELS_PER_DEGREE

p1 = (-300, y)
p2 = (-300, y)

def pygame_loop(state):
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        #y = 0
        p1r = rotate_point(*p1, -roll)
        p2r = rotate_point(*p2, -roll)

        pygame.draw.line(
            screen,
            (255,255,255),
            world_to_screen(*p1r),
            world_to_screen(*p2r),
            5
        )
        pygame.display.flip()
        clock.tick(60)

pygame_loop(True)