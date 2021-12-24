import sys, os
import warnings
import time
import datetime
import math

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

import pygame
from pygame import gfxdraw

import numpy as np

import modules.configurator as cfg

au = 1.495978707*10**11

BACKGROUND_COLOR = pygame.Color('#050712')
width, height = 1080, 720
scale = au / 100
camera_offset = (0,0)
zoom_increment_factor = 1.1
FPS = 100

paused = False
show_center_of_mass = False
display_names = True

text_color = pygame.Color('#bbccee')
hovering_color = pygame.Color('#bbbbbb')
selected_color = pygame.Color('#ddeeff')
circumference_thickness = 2
hollow_segment_length = 4


G = 6.6743*10**-11
dt = 2000000

globals().update(cfg.readConfig('settings.cfg'))

half_screen_offset = (width/2, height/2)
circumference_distance = hollow_segment_length + circumference_thickness

pygame.init()
Courier_New = pygame.font.SysFont('Courier New', 16)
Consolas = pygame.font.SysFont('Consolas', 16)

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Gravioli')
pygame.display.set_icon(pygame.image.load('icon.png'))

clock = pygame.time.Clock()

# Margin in pixels, for the rendering of paths.
path_surface_margin = np.array((10, 10), dtype=np.int32)
path_surface_size = (width+path_surface_margin[0]*2, height+path_surface_margin[1]*2)

if path_surface_size[0] * path_surface_size[1] > 1500*1500:
    warnings.warn("Path surface margin is high, which may cause lag spikes.")

if width > 1920 or height > 1080:
    warnings.warn("Screen dimensions may be too high.")

empty = pygame.Color(0,0,0,0)
fade = pygame.Color(255,255,255,240)
path_surface = pygame.Surface((width+path_surface_margin[0]*2, height+path_surface_margin[1]*2), pygame.SRCALPHA, 32)

gui_background = pygame.Surface((width, height), pygame.SRCALPHA, 32)
gui_surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)

def screen_position(true_position, offset=(0,0)):
    return ((true_position[0]) / scale + half_screen_offset[0] + camera_offset[0] + offset[0], \
           -(true_position[1]) / scale + half_screen_offset[1] + camera_offset[1] + offset[1])

def true_position(screen_position, offset=(0,0)):
    return (screen_position[0]-half_screen_offset[0]-offset[1])*scale, -(screen_position[1]-half_screen_offset[1]-offset[1])*scale, 0

def offset_surface(surface, offset=(0,0)):
    new_surface = surface.copy()
    new_surface.fill(empty)
    new_surface.blit(surface, offset)
    return new_surface

class Environment:

    def __init__(self, name, object_dict={}, start_time=0, dt=dt, softening=80000000, G=6.6743*10**-11):
        self.object_dict = object_dict
        self.start_time = start_time
        self.dt = dt
        self.softening = softening
        self.G = G

    @property
    def mass(self):
        return sum([body.mass for body in universe.objects])

    @property
    def objects(self):
        return self.object_dict.values()

universe = Environment('Universe', start_time=time.time())

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
            environment=None,
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
        self.acceleration = np.array([0,0,0], dtype=np.float64)

        self.new_position = self.position
        self.new_acceleration = self.acceleration
        self.new_velocity = self.velocity

        self.darker_color = pygame.Color(int(0.5*self.color.r), int(0.5*self.color.g), int(0.5*self.color.b))
        self.mouse_hovering = False
        self.selected = False

    @property
    def size(self):
        # meters / meters per pixel = pixels
        size = self.radius/scale
        
        if self.name != 'Sol' and universe.name == 'Solar System':
            size *= 1#800
            
        if size < 1:
            size = 1
            
        return size

    def update_position(self):

        self.new_position = self.position + self.velocity * dt / FPS + self.acceleration*(0.5*(dt/FPS)**2)

    def update_acceleration(self):
        
        self.new_acceleration = np.array([0,0,0], dtype=np.float64)
        
        for other in universe.objects:
            dist = other.position - self.new_position
            dist_norm = math.sqrt(sum((dim**2 for dim in dist))+universe.softening)
            
            if self == other or dist_norm < self.radius + other.radius:
                continue
            
            self.new_acceleration += G * other.mass * dist / dist_norm**3

    def update_velocity(self):
        
        self.new_velocity = self.velocity + (self.new_acceleration + self.acceleration) * 0.5 * dt / FPS



from systems import solar_system, sagittarius
from spacemath import kep_to_cart

def set_system(environment, system):
    print(f"Setting up {system.name}")

    environment.name = system.name

    parent = system.parent
    parent_body = Body(parent.name, parent.color, parent.mass, parent.radius, [0,0,0], [0,0,0])
    environment.object_dict[parent_body.name] = (parent_body)

    global scale
    scale = parent_body.radius
    print("Set scale to", scale)

    # Sub-systems
    
    planets = system.planets
    for planet in planets:
        planet_body = Body(
            planet.name,
            planet.color,
            planet.mass,
            planet.radius,
            *kep_to_cart(
                G*parent_body.mass,
                planet.a,
                planet.e,
                math.radians(planet.i),
                math.radians(planet.lon_AN),
                math.radians(planet.lon_Pe),
                math.radians(planet.ML),
                environment.start_time,
                planet.Epoch,
                )
            )
        environment.object_dict[planet_body.name] = (planet_body)

set_system(universe, solar_system)

fade_timer = 0

simulation_time = int(time.time())


def calculate_fps():
    global current, previous, fps_list
    
    current = time.perf_counter()
    fps = round(1/(current-previous),4)
    previous = current

    if len(fps_list) >= 10:
        del fps_list[0]
    fps_list.append(fps)

was_left_clicked = False

k = 0
fps_list = []
previous = time.perf_counter()

active = True
while active:

    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            active = False
            
        elif event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_SPACE:
                paused = not paused

            elif event.key == pygame.K_LEFT:
                dt = math.copysign(dt,-1)
            elif event.key == pygame.K_RIGHT:
                dt = math.copysign(dt,1)

            elif event.key == pygame.K_m:
                show_center_of_mass = not show_center_of_mass
                print(show_center_of_mass)
                
        elif event.type == pygame.MOUSEWHEEL:
            
            if event.y == 1:
                scale /= zoom_increment_factor
                path_surface.fill(empty)
            elif event.y == -1:
                scale *= zoom_increment_factor
                path_surface.fill(empty)
    
    mouse_pos = pygame.mouse.get_pos()

    mouse_state = pygame.mouse.get_pressed()
    keys = pygame.key.get_pressed()

    mouse_relative_position = pygame.mouse.get_rel()
    
    if mouse_state[2]:
        camera_offset += np.array(mouse_relative_position)
        path_surface = offset_surface(path_surface, mouse_relative_position)

    if keys[pygame.K_UP]:
        dt *= 1.02
    if keys[pygame.K_DOWN]:
        dt /= 1.02
        
    
    if not paused:
        
        for body in universe.objects:
            body.update_position()
            body.update_acceleration()
            body.update_velocity()
        
        for body in universe.objects:

            pygame.draw.aaline(path_surface, body.darker_color, screen_position(body.position, path_surface_margin), screen_position(body.new_position, path_surface_margin))
            
            body.position = body.new_position
            body.velocity = body.new_velocity
            body.acceleration = body.new_acceleration
    
        if fade_timer < 0:
            fade_timer = int(300000000/abs(dt))
            path_surface.fill(fade, special_flags=pygame.BLEND_RGBA_MULT)
        fade_timer -= 1

        simulation_time += dt / FPS

    else:
        time.sleep(0.02)

    screen.fill(BACKGROUND_COLOR)
    gui_surface.fill(empty)
    screen.blit(path_surface, -path_surface_margin)

    
    # Drawing of bodies, and hovering effects.
    for body in universe.objects:
            
        body_screen_position = screen_position(body.position)
        body_screen_size = body.size

        mouse_distance = math.sqrt((mouse_pos[0]-body_screen_position[0])**2+(mouse_pos[1]-body_screen_position[1])**2)

        if mouse_distance > body_screen_size+1000:
            continue
        
        try:
            gfxdraw.aacircle(screen, *tuple(map(int, body_screen_position)), int(body_screen_size), body.color)
            gfxdraw.filled_circle(screen, *tuple(map(int, body_screen_position)), int(body_screen_size), body.color)
        except:
            pass

        color = hovering_color
        
        if mouse_distance < body_screen_size+12:
            body.mouse_hovering = True
            if mouse_state[0] and not was_left_clicked:
                body.selected = not body.selected
                was_left_clicked = True
            elif not mouse_state[0] and was_left_clicked:
                was_left_clicked = False
        else:
            body.mouse_hovering = False

        if body.selected:
            color = body.color
            if body.mouse_hovering:
                color = selected_color

        if body.mouse_hovering or body.selected:
            gfxdraw.aacircle(gui_surface, *tuple(int(x) for x in body_screen_position), int(body_screen_size)+circumference_distance, color)
            gfxdraw.filled_circle(gui_surface, *tuple(int(x) for x in body_screen_position), int(body_screen_size)+circumference_distance, color)
            gfxdraw.filled_circle(gui_surface, *tuple(int(x) for x in body_screen_position), int(body_screen_size)+hollow_segment_length, empty)

            if display_names:
                pygame.draw.line(gui_surface, color, \
                                   (body_screen_position[0]+int(body_screen_size)+circumference_distance, body_screen_position[1]), \
                                   (body_screen_position[0]+int(body_screen_size)+60, body_screen_position[1]), \
                                   )
                gui_surface.blit(Consolas.render(body.name, True, color), (body_screen_position[0]+int(body_screen_size)+66, body_screen_position[1]-7))
            

    if show_center_of_mass:
        center_of_mass = sum([body.mass*body.position for body in universe.objects])/universe.mass
        
        pygame.draw.circle(screen, '#ff4400', screen_position(center_of_mass, camera_offset), 2)
    
    try:
        simulation_date = datetime.date.fromtimestamp(simulation_time).strftime('%Y-%m-%d')
    except OSError:
        pass

    calculate_fps()
    if not k % 10:
        average_fps = sum(fps_list)/len(fps_list)

    info = [
        (f"Date: {simulation_date}", text_color),
        (f"{round(dt,2)} seconds per second", text_color),
        (f"{round(dt/60/60/24,2)} days per second", text_color),
        (f"{round(dt/60/60/24/365.25,2)} years per second", text_color),
        (f"{round(scale/10**(int(math.log10(scale))),3)}e{int(math.log10(scale))} meters per pixel", text_color),
        (f"{round(average_fps,2)} frames per second", text_color),
        (f"Total mass: {round(universe.mass/10**(int(math.log10(universe.mass))),6)}e{int(math.log10(universe.mass))} kg", text_color),
        ]
    
    for n, i in enumerate(info):
        gui_surface.blit(Courier_New.render(i[0], True, i[1]), (24, 20*n+16))
        
    screen.blit(gui_surface, (0,0))

    pygame.display.update()

    k += 1
    clock.tick(FPS)

pygame.quit()

# Retired code

        #gfxdraw.aacircle(screen, *tuple(map(int, screen_position(center_of_mass, camera_offset))), 2, pygame.Color('#ff3300'))
        #gfxdraw.filled_circle(screen, *tuple(map(int, screen_position(center_of_mass, camera_offset))), 2, pygame.Color('#ff3300'))

        #self.velocity += dt / FPS * sum([other.specific_gravity*distance/(sum((p**2 for p in distance))+universe.softening)**1.5 for other in universe.objects if ((other is not self) and (distance := (other.position-self.position)) is not None)])

       # pygame.draw.circle(screen, body.color, tuple(x+1 for x in screen_position(body.position, camera_offset)), body.size)
       
        #total_momentum = sum([body.mass*body.velocity for body in universe.objects])

##    Object(color='#eeff44',radius=6.96340*10**8,mass=1.98847*10**30,position=[0,0,0],velocity=[0,0,0]),
##    Object(color='#8f8099',radius=1*10**6,mass=2*10**23,position=[0.387*au,0,0],velocity=[0,29986/math.sqrt(0.387),0]),
##    Object(color='#cc9966',radius=6*10**6,mass=3*10**24,position=[0.723*au,0,0],velocity=[0,29986/math.sqrt(0.723),0]),
##    Object(color='#0055dd',radius=6.371*10**6,mass=5.972*10**24,position=[au,0,0],velocity=[0,29986,0]),
##    Object(color='#dd5522',radius=3*10**6,mass=5*10**23,position=[1.524*au,0,0],velocity=[0,29986/math.sqrt(1.524),0]),
