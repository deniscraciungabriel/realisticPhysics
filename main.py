from email.header import Header
from venv import create
from cv2 import circle, getOptimalDFTSize
import pygame
import pymunk
import pymunk.pygame_util as P
import math

pygame.init()

WIDTH, HEIGHT = 1200, 800
window = pygame.display.set_mode((WIDTH, HEIGHT))


def draw(window, space, drawing_options, line):
    window.fill("white")

    if line:
        pygame.draw.line(window, "black", line[0], line[1], 3)

    # allows you to use pygame to draw objects (?)
    space.debug_draw(drawing_options)

    pygame.display.update()


def calculate_disatance(p1, p2):
    return math.sqrt((p2[1] - p1[1])**2 + (p2[0]-p1[0])**2)


def calculate_angle(p1, p2):
    return math.atan2(p2[1]-p1[1], p2[0]-p1[0])


# CREATING FLOORS AND WALLS
def create_walls(space, width, height):
    # unlike objects like a ball, which are dinamic bodies, these are going to be static, so they don't fall into the void
    rects = [
        [(width/2, height-10), (width, 20)],
        [(width/2, 10), (width, 20)],
        [(10, height/2), (20, height)],
        [(width-10, height/2), (20, height)]
    ]

    for pos, size in rects:
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        shape = pymunk.Poly.create_box(body, size)
        # CREATING ELASTICITY AND FRICTION
        shape.elasticity = 0.4
        shape.friction = 0.5  # both coefficients
        space.add(body, shape)
        shape.color = (100, 0, 20, 100)


# CREATING A CIRCLE
def create_ball(space, radius, mass, pos):
    # the way this works is similar to FPS games, where the hitbox (body) is simpler, like shapes, and the images is the one we actually see, but not the one interested to hits or in this case calculations
    # body, we are making it static becasue when we hold the mouse button, we need to have the ball staying still, and then make it dinamic when we want to launch it
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = pos
    shape = pymunk.Circle(body, radius)  # image
    shape.mass = mass
    # CREATING ELASTICITY AND FRICTION
    shape.elasticity = 0.9
    shape.friction = 0.4
    shape.color = (0, 200, 200, 100)
    space.add(body, shape)

    return shape


# CREATE OBSTACLES AND VARIOUS OBJECTS
def create_structure(space, width, height):
    BROWN = (139, 69, 19, 100)
    rects = [
        [(700, height-120), (40, 200), BROWN, 100],
        [(1000, height-120), (40, 200), BROWN, 100],
        [(850, height-240), (340, 40), BROWN, 150]
    ]

    for pos, size, color, mass in rects:
        body = pymunk.Body()
        body.position = pos
        shape = pymunk.Poly.create_box(body, size, radius=1)
        shape.color = color
        shape.mass = mass
        shape.elasticity = 0.9
        shape.friction = 0.4
        space.add(body, shape)


def create_swing(space):
    rotation_center_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    rotation_center_body.position = (300, 270)

    body = pymunk.Body()
    body.position = (300, 300)

    line = pymunk.Segment(body,  (0, 0), (255, 0), 5)
    circle = pymunk.Circle(body, 40,  (255, 0))
    line.friction = 1
    circle.friction = 1
    line.mass = 8
    circle.mass = 30
    circle.elasticity = 0.95
    rotation_center_joint = pymunk.PinJoint(
        body, rotation_center_body, (0, 0), (0, 0))
    space.add(circle, line, body, rotation_center_joint)


def run(window, WIDTH, HEIGHT):
    run = True
    fps = 60
    clock = pygame.time.Clock()
    deltaTime = 1 / fps

    # CREATING THE SPACE
    space = pymunk.Space()  # creates a space in which pymunk can create its simulations
    # it takes both a y and x value, and the reason it's not 9.81 is because that would just be too slow in the simulation
    space.gravity = (0, 981)

    # DRAWING THE SIMULATION
    drawing_options = P.DrawOptions(window)
    create_walls(space, WIDTH, HEIGHT)
    create_structure(space, WIDTH, HEIGHT)
    create_swing(space)

    pressed_pos = None
    ball = None

    while run:
        line = None
        if ball and pressed_pos:
            line = [pressed_pos, pygame.mouse.get_pos()]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            # LAUNCHING THE BALL
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not ball:
                    pressed_pos = pygame.mouse.get_pos()
                    ball = create_ball(space, 30, 10, pressed_pos)
                elif pressed_pos:
                    ball.body.body_type = pymunk.Body.DYNAMIC
                    angle = calculate_angle(*line)
                    force = calculate_disatance(*line) * 50
                    fx = math.cos(angle) * force
                    fy = math.sin(angle) * force
                    # force only in x, 0,0 is the location on the ball where the impulse is applied (so center)
                    ball.body.apply_impulse_at_local_point((fx, fy), (0, 0))
                    pressed_pos = None
                else:
                    space.remove(ball, ball.body)
                    ball = None

        draw(window, space, drawing_options, line)

        # similar to what the clock does, it sets the speed of the simulation
        space.step(deltaTime)
        clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    run(window, WIDTH, HEIGHT)
