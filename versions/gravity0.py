import sys, os
import time, datetime
import math

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

import pygame
from pygame import gfxdraw

import numpy as np

import modules.configurator as cfg

au = 1.495978707*10**11
earth_radius = 6.371*10**6

BACKGROUND_COLOR = pygame.Color('#0a0a10')
width, height = 800, 600
scale = au / 100
camera_offset = (0,0)
zoom_increment_factor = 1.1
FPS = 120

G = 6.6743*10**-11
time_variable = 1000000

globals().update(cfg.readConfig('settings.cfg'))
screen_offset = (width/2, height/2)

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Gravioli')
pygame.display.set_icon(pygame.image.load('icon.png'))

clock = pygame.time.Clock()

empty = pygame.Color(0,0,0,0)
fade = pygame.Color(255,255,255,240)
path_surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)

gui_background = pygame.Surface((width, height), pygame.SRCALPHA, 32)
gui_surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)

def screen_position(true_position, offset=(0,0)):
    return true_position[0]/scale + screen_offset[0] + offset[0], -true_position[1]/scale + screen_offset[1] + offset[1]

def true_position(screen_position, offset=(0,0)):
    return (screen_position[0]-screen_offset[0]-offset[1])*scale, -(screen_position[1]-screen_offset[1]-offset[1])*scale, 0

class Environment:

    def __init__(self, objects=[], start_time=0, time_variable=100000, G=6.6743*10**-11):
        self.objects = objects
        self.start_time = start_time
        self.time_variable = time_variable
        self.G = G

    @property
    def center_of_mass(self):
        pass

    @property
    def momentum_total(self):
        pass
        

class Body:

    global universe

    def __init__(
            self,
            name='Conway',
            color=pygame.Color(200,0,0),
            mass=10**6,
            radius=0.1,
            position=None,
            velocity=None,
            ):

        self.name = name
        self.color = pygame.Color(color)
        self.mass = mass
        self.radius = radius

        if position == None:
            position = [0,0,0]
        if velocity == None:
            velocity = [0,0,0]

        self.position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)

        self.path_surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)

        self.darker_color = pygame.Color(int(0.5*self.color.r), int(0.5*self.color.g), int(0.5*self.color.b))
        self.specific_gravity = G * mass * time_variable / FPS

    @property
    def size(self):
        # meters/(meters/pixel) = pixels
        size = self.radius/scale
        if self.name != 'Sol':
            size *= 600
        if size < 1:
            size = 1
        return size

    def update_velocity(self):

        self.velocity += sum([other.specific_gravity*distance/(sum((p**2 for p in distance)))**1.5 for other in universe.objects if ((other is not self) and (distance := (other.position-self.position)) is not None)])

    def update_position(self):

        self.last_position = screen_position(self.position)
        self.position += self.velocity * time_variable / FPS
        current_position = screen_position(self.position)

        pygame.draw.aaline(path_surface, self.darker_color, self.last_position, current_position)

universe = Environment([], start_time=time.time())

from systems import solar_system
from spacemath import kep_to_cart

def add_system(environment, system):

    focus = system.focus
    parent_body = Body(focus.name, focus.color, focus.mass, focus.radius, [0,0,0], [0,0,0])
    environment.objects.append(parent_body)

    planets = system.planets
    for planet in planets:
        planet_body = Body(
            planet.name,
            planet.color,
            planet.mass,
            planet.radius,
            *kep_to_cart(
                planet.a*au,
                planet.e,
                math.radians(planet.i),
                math.radians(planet.lon_AN),
                math.radians(planet.lon_Pe),
                math.radians(planet.ML),
                environment.start_time,
                )
            )
        environment.objects.append(planet_body)

add_system(universe, solar_system)

right_clicked = False
paused = False

fade_timer = 0

active = True
while active:

    screen.fill(BACKGROUND_COLOR)
    screen.blit(path_surface, camera_offset)

    mouse_state = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    if mouse_state[2]:
        mouse_relative = np.array(pygame.mouse.get_rel())
        if right_clicked:
            camera_offset += mouse_relative
        right_clicked = True
    elif right_clicked:
        right_clicked = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            active = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
        elif event.type == pygame.MOUSEWHEEL:
            if event.y == 1:
                scale /= zoom_increment_factor
                path_surface.fill(empty)
            elif event.y == -1:
                scale *= zoom_increment_factor
                path_surface.fill(empty)

    if not paused:

        if not fade_timer:
            fade_timer = int(60*5000000/time_variable)
            path_surface.fill(fade, special_flags=pygame.BLEND_RGBA_MULT)
        fade_timer -= 1

        for body in universe.objects:
            body.update_velocity()
    
        for body in universe.objects:
            body.update_position()

    for body in universe.objects:
        pygame.draw.circle(screen, body.color, tuple(x+1 for x in screen_position(body.position, camera_offset)), body.size)

    pygame.display.update()

    clock.tick(FPS)

pygame.quit()


        #total_momentum = sum([body.mass*body.velocity for body in universe.objects])

##    Object(color='#eeff44',radius=6.96340*10**8,mass=1.98847*10**30,position=[0,0,0],velocity=[0,0,0]),
##    Object(color='#8f8099',radius=1*10**6,mass=2*10**23,position=[0.387*au,0,0],velocity=[0,29986/math.sqrt(0.387),0]),
##    Object(color='#cc9966',radius=6*10**6,mass=3*10**24,position=[0.723*au,0,0],velocity=[0,29986/math.sqrt(0.723),0]),
##    Object(color='#0055dd',radius=6.371*10**6,mass=5.972*10**24,position=[au,0,0],velocity=[0,29986,0]),
##    Object(color='#dd5522',radius=3*10**6,mass=5*10**23,position=[1.524*au,0,0],velocity=[0,29986/math.sqrt(1.524),0]),
