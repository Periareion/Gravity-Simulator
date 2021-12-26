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

G = 6.6743*10**-11
au = 1.495978707*10**11
WIDTH, HEIGHT = 1080, 720
FPS = 300

scale = au / 100

settings = {
    'scale': scale,
    'delta_time': 200000,
    'paused': False,
    'show_center_of_mass': False,
    'display_names': True,
    'hovering': False,
    'planet_rescale_factor': 500,
    'camera_offset': np.array([0,0], dtype=np.float64),
}

COLORS = {
    'BACKGROUND': pygame.Color('#050610'),
    'TEXT': pygame.Color('#bbccee'),
    'HOVERING': pygame.Color('#bbbbbb'),
    'SELECTED': pygame.Color('#ddeeff'),
    'EMPTY': pygame.Color(0,0,0,0),
    'FADE': pygame.Color(255,255,255,240)
}

zoom_increment_factor = 1.1

circumference_thickness = 2
hollow_segment_length = 3
fragments = 4

settings.update(cfg.readConfig('config.cfg'))

pygame.font.init()
Courier_New = pygame.font.SysFont('Courier New', 16)
Consolas = pygame.font.SysFont('Consolas', 16)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Gravity Simulation')
pygame.display.set_icon(pygame.image.load('icon.png'))

clock = pygame.time.Clock()

path_surface_margin = np.array((10, 10), dtype=np.int32)
path_surface_size = (WIDTH+path_surface_margin[0]*2, HEIGHT+path_surface_margin[1]*2)
zoom_in_WIDTH, zoom_in_HEIGHT = int(path_surface_size[0]*zoom_increment_factor), int(path_surface_size[1]*zoom_increment_factor)
zoom_out_WIDTH, zoom_out_HEIGHT = int(path_surface_size[0]/zoom_increment_factor), int(path_surface_size[1]/zoom_increment_factor)

if path_surface_size[0] * path_surface_size[1] > 1500*1500:
    warnings.warn("Path surface margin is high, which may cause lag spikes.")

if WIDTH > 1920 or HEIGHT > 1080:
    warnings.warn("Screen dimensions may be too high.")

gui_background = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA, 32)
gui_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA, 32)

def screen_position(true_position, offset=(0,0)):
    return ((true_position[0]) / settings['scale'] + WIDTH/2 + settings['camera_offset'][0] + offset[0], \
           -(true_position[1]) / settings['scale'] + HEIGHT/2 + settings['camera_offset'][1] + offset[1])

def true_position(screen_position, offset=(0,0)):
    return ((screen_position[0]-WIDTH/2-settings['camera_offset'][0]-offset[1])*settings['scale'], \
           (screen_position[1]-HEIGHT/2-settings['camera_offset'][1]-offset[1])*settings['scale'], 0)

def offset_surface(surface, offset=(0,0)):
    new_surface = surface.copy()
    new_surface.fill(COLORS['EMPTY'])
    new_surface.blit(surface, offset)
    return new_surface

class Environment:

    def __init__(self, name, object_dict={}, start_time=0, delta_time=settings['delta_time'], softening=80000000, G=6.6743*10**-11):
        self.name=name
        self.object_dict = object_dict
        self.time = start_time
        self.delta_time = delta_time
        self.softening = softening
        self.G = G

    @property
    def mass(self):
        return sum([body.mass for body in universe.objects])

    @property
    def objects(self):
        return self.object_dict.values()

    def draw():
        pass

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
            ):

        self.name = name
        self.color = pygame.Color(color)
        self.mass = mass
        self.radius = radius

        self.position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.acceleration = np.array([0,0,0], dtype=np.float64)

        self.new_position = self.position
        self.new_velocity = self.velocity
        self.new_acceleration = self.acceleration

        self.darker_color = pygame.Color(int(0.5*self.color.r), int(0.5*self.color.g), int(0.5*self.color.b))
        self.mouse_hovering = False
        self.selected = False

    @property
    def size(self):
        # meters / meters per pixel = pixels
        size = self.radius/settings['scale']

        
        if self.name != 'Sol' and universe.name == 'Solar System':
            size *= settings['planet_rescale_factor']
        #else:
        #    size = (self.mass)**(1/20)*200000000/settings['scale']
            
        if size < 1:
            size = 1
            
        return size

    def update_position(self):

        self.new_position = self.position + self.velocity * settings['delta_time'] / FPS + self.acceleration*(0.5*(settings['delta_time']/FPS)**2)

    def update_acceleration(self):
        
        self.new_acceleration = np.array([0,0,0], dtype=np.float64)
        
        for other in universe.objects:
            dist = other.position - self.new_position
            dist_norm = math.sqrt(sum((dim**2 for dim in dist))+universe.softening)
            
            if self == other or dist_norm < self.radius + other.radius:
                continue
            
            self.new_acceleration += G * other.mass * dist / dist_norm**3

    def update_velocity(self):
        
        self.new_velocity = self.velocity + (self.new_acceleration + self.acceleration) * 0.5 * settings['delta_time'] / FPS



from systems import solar_system, sagittarius
from spacemath import kep_to_cart

def set_system(environment, system):
    print(f"Setting up {system.name}")

    environment.name = system.name

    parent = system.parent
    parent_body = Body(parent.name, parent.color, parent.mass, parent.radius, [0,0,0], [0,0,0])
    environment.object_dict[parent_body.name] = (parent_body)

    settings['scale'] = parent_body.radius

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
                environment.time,
                planet.Epoch,
                )
            )
        environment.object_dict[planet_body.name] = (planet_body)

set_system(universe, solar_system)




def main():

    was_left_clicked = False
    hovering = False

    path_surface = pygame.Surface((WIDTH+path_surface_margin[0]*2, HEIGHT+path_surface_margin[1]*2), pygame.SRCALPHA, 32)
    
    fade_timer = 0  

    k = 0
    fps_list = []
    previous_time = time.perf_counter()

    # System to check if a key was just pressed
    last_key_state = pygame.key.get_pressed()

    tracked_keys = {
        pygame.K_x: False,
        }

    active = True
    while active:
        
        mouse_pos = pygame.mouse.get_pos()

        mouse_state = pygame.mouse.get_pressed()
        
        current_key_state = pygame.key.get_pressed()

        for key in tracked_keys.keys():
            if last_key_state[key]:
                # Pressed last frame
                tracked_keys[key] = False
            elif current_key_state[key]:
                # Pressed this from and not last frame.
                tracked_keys[key] = True

        last_key_state = current_key_state
                
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                active = False
                
            elif event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_SPACE:
                    settings['paused'] = not settings['paused']

                elif event.key == pygame.K_LEFT:
                    settings['delta_time'] = math.copysign(settings['delta_time'],-1)
                elif event.key == pygame.K_RIGHT:
                    settings['delta_time'] = math.copysign(settings['delta_time'],1)

                elif event.key == pygame.K_m:
                    settings['show_center_of_mass'] = not settings['show_center_of_mass']

                elif event.key == pygame.K_c:
                    path_surface.fill(COLORS['EMPTY'])

                elif event.key == pygame.K_v:
                    contents = cfg.readLine(input("Manually redefine a variable: "))
                    if contents == 'stop':
                        active = False
                    elif contents == None:
                        pass
                    elif len(contents) == 2:
                        key, value = contents
                        globals().update({key: value})
                        print(cfg.print_format.format(k=key,v=value))
                    
            elif event.type == pygame.MOUSEWHEEL:
                
                if event.y == 1:
                    # Zoom in
                    settings['scale'] /= zoom_increment_factor
                    
                    offset = np.array(true_position(mouse_pos)[:-1], dtype=np.float64)/settings['scale']*(1-zoom_increment_factor)
                    settings['camera_offset'] += offset

                    temp = pygame.transform.smoothscale(path_surface, (zoom_in_WIDTH, zoom_in_HEIGHT))
                    path_surface.fill(COLORS['EMPTY'])
                    path_surface.blit(temp, ((path_surface_size[0]-zoom_in_WIDTH)/2+(mouse_pos[0]-WIDTH/2)*(1-zoom_increment_factor)-1, (path_surface_size[1]-zoom_in_HEIGHT)/2+(mouse_pos[1]-HEIGHT/2)*(1-zoom_increment_factor)-1))
                    path_surface.fill(COLORS['FADE'], special_flags=pygame.BLEND_RGBA_MULT)

                elif event.y == -1:
                    # Zoom out
                    settings['scale'] *= zoom_increment_factor
                    
                    offset = np.array(true_position(mouse_pos)[:-1])/settings['scale']*(1-1/zoom_increment_factor)
                    settings['camera_offset'] += offset

                    temp = pygame.transform.smoothscale(path_surface, (zoom_out_WIDTH, zoom_out_HEIGHT))
                    path_surface.fill(COLORS['EMPTY'])
                    path_surface.blit(temp, ((path_surface_size[0]-zoom_out_WIDTH)/2+(mouse_pos[0]-WIDTH/2)*(1-1/zoom_increment_factor), (path_surface_size[1]-zoom_out_HEIGHT)/2+(mouse_pos[1]-HEIGHT/2)*(1-1/zoom_increment_factor)))

        mouse_relative_position = pygame.mouse.get_rel()
        
        if mouse_state[2]:
            settings['camera_offset'] += np.array(mouse_relative_position)
            path_surface = offset_surface(path_surface, mouse_relative_position)

        if current_key_state[pygame.K_UP]:
            settings['delta_time'] *= 1.02
        if current_key_state[pygame.K_DOWN]:
            settings['delta_time'] /= 1.02
        
        if not settings['paused']:
            
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
                fade_timer = int(700000000/abs(settings['delta_time']))%10000
                path_surface.fill(COLORS['FADE'], special_flags=pygame.BLEND_RGBA_MULT)
            fade_timer -= 1

            universe.time += settings['delta_time'] / FPS
        
        screen.fill(COLORS['BACKGROUND'])
        screen.blit(path_surface, -path_surface_margin)
        gui_surface.fill(COLORS['EMPTY'])
        
        # Drawing of bodies, and hovering effects.
        removed_bodies = []
        new_body_dict = {}
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

            color = COLORS['HOVERING']
            
            if mouse_distance < body_screen_size+12:
                hovering = body.mouse_hovering = True
                if mouse_state[0] and not was_left_clicked:
                    body.selected = not body.selected
                    was_left_clicked = True
                elif not mouse_state[0] and was_left_clicked:
                    was_left_clicked = False
                    
                if tracked_keys[pygame.K_x]:
                    angle_increment = 2*math.pi/fragments
                    mass = body.mass/fragments
                    velocity = body.velocity
                    velocity_norm = np.linalg.norm(velocity)

                    removed_bodies.append(body.name)
                    
                    for n in range(fragments):
                        angle = angle_increment*n
                        normalized_direction = np.array([math.cos(angle), math.sin(angle), 0])
                        name = f"{body.name} {n}"
                        new_body_dict[name] = Body(
                            name=name,
                            color=body.color,
                            mass=body.mass/fragments,
                            radius=body.radius*0.4,
                            position=body.position+normalized_direction*body.radius*50,
                            velocity=velocity+(normalized_direction*velocity_norm*0.4)
                            )

                    tracked_keys[pygame.K_x] = False
                    continue
                
            else:
                body.mouse_hovering = False

            if body.selected:
                color = body.color
                if body.mouse_hovering:
                    color = COLORS['SELECTED']

            if body.mouse_hovering or body.selected:
                try:
                    gfxdraw.aacircle(gui_surface, *tuple(int(x) for x in body_screen_position), int(body_screen_size)+(hollow_segment_length+circumference_thickness), color)
                    gfxdraw.filled_circle(gui_surface, *tuple(int(x) for x in body_screen_position), int(body_screen_size)+(hollow_segment_length+circumference_thickness), color)
                    gfxdraw.filled_circle(gui_surface, *tuple(int(x) for x in body_screen_position), int(body_screen_size)+hollow_segment_length, COLORS['EMPTY'])
                    pygame.draw.line(gui_surface, COLORS['EMPTY'],
                                    (body_screen_position[0]-(int(body_screen_size)+(hollow_segment_length+circumference_thickness)+2), body_screen_position[1]),
                                    (body_screen_position[0]+(int(body_screen_size)+(hollow_segment_length+circumference_thickness)+2), body_screen_position[1]),
                                    int(body_screen_size/2)+3)
                    pygame.draw.line(gui_surface, COLORS['EMPTY'],
                                    (body_screen_position[0], body_screen_position[1]-(int(body_screen_size)+(hollow_segment_length+circumference_thickness)+2)),
                                    (body_screen_position[0], body_screen_position[1]+(int(body_screen_size)+(hollow_segment_length+circumference_thickness)+2)),
                                    int(body_screen_size/2)+3)
                except:
                    pass

                if settings['display_names']:
                    pygame.draw.line(gui_surface, color,
                                    (body_screen_position[0]+int(body_screen_size)+(hollow_segment_length+circumference_thickness), body_screen_position[1]),
                                    (body_screen_position[0]+int(body_screen_size)+60, body_screen_position[1]),
                                    )
                    gui_surface.blit(Consolas.render(body.name, True, color), (body_screen_position[0]+int(body_screen_size)+66, body_screen_position[1]-7))

        for body in removed_bodies:
            del universe.object_dict[body]

        universe.object_dict.update(new_body_dict)

        if settings['paused']:
            gui_surface.blit(Courier_New.render('SIMULATION PAUSED', True, '#4460ff'), (WIDTH/2-92, 36))

        if hovering:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            
        hovering = False

        if settings['show_center_of_mass']:
            center_of_mass = sum([body.mass*body.position for body in universe.objects])/universe.mass
            
            pygame.draw.circle(screen, '#ff4400', screen_position(center_of_mass), 2)
        
        try:
            simulation_date = datetime.date.fromtimestamp(universe.time).strftime('%Y-%m-%d')
        except OSError:
            pass

        info = [
            (f"Date: {simulation_date}", COLORS['TEXT']),
            (f"{round(settings['delta_time'],2)} seconds per second", COLORS['TEXT']),
            (f"{round(settings['delta_time']/60/60/24,2)} days per second", COLORS['TEXT']),
            (f"{round(settings['delta_time']/60/60/24/365.25,3)} years per second", COLORS['TEXT']),
            (f"{round(settings['scale']/10**(int(math.log10(settings['scale']))),3)}e{int(math.log10(settings['scale']))} meters per pixel", COLORS['TEXT']),
            #(f"{round(average_fps, 2)} frames per second", COLORS['TEXT']),
            (f"Total mass: {round(universe.mass/10**(int(math.log10(universe.mass))),6)}e{int(math.log10(universe.mass))} kg", COLORS['TEXT']),
            ]
        
        for n, i in enumerate(info):
            gui_surface.blit(Courier_New.render(i[0], True, i[1]), (24, 20*n+16))
            
        screen.blit(gui_surface, (0,0))

        pygame.display.update()

        k += 1
        clock.tick(FPS)

if __name__ == '__main__':
    main()

pygame.quit()