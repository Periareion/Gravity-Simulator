import sys
import os
import warnings
import time
import datetime
import math

sys.path.append('.\assets')
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

import pygame
from pygame import gfxdraw

import numpy as np

from modules import configurator as cfg
from modules import const

WIDTH, HEIGHT = 1080, 720

settings = {
    'TARGET_SIM_FPS': 500,
    'paused': False,
    'simulation_start_time': time.time(),
    'delta_time': 200000,
    'fragments': 5,
}

visual_settings = {
    'FPS': 60,
    'scale': const.AU / 100,
    'show_center_of_mass': False,
    'display_names': True,
    'rescale_factor': 500,
    'circumference_thickness': 2,
    'hollow_segment_length': 5,
    'zoom_increment_factor': 1.1,
}

COLORS = {
    'BACKGROUND': pygame.Color('#050610'),
    'TEXT': pygame.Color('#bbccee'),
    'HOVERING': pygame.Color('#bbbbbb'),
    'SELECTED': pygame.Color('#ddeeff'),
    'EMPTY': pygame.Color(0,0,0,0),
    'FADE': pygame.Color(255,255,255,240),
}


settings['TRUE_FPS'] = settings['TARGET_SIM_FPS']

updated_settings = cfg.readConfig('config.cfg')
cfg.update_dictionaries(updated_settings, [settings, visual_settings, COLORS])

pygame.font.init()
Courier_New = pygame.font.SysFont('Courier New', 16)
Consolas = pygame.font.SysFont('Consolas', 16)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Gravity Simulation')
pygame.display.set_icon(pygame.image.load('assets\\icon.png'))

clock = pygame.time.Clock()

path_surface_margin = np.array((10, 10), dtype=np.int32)
path_surface_size = (WIDTH+path_surface_margin[0]*2, HEIGHT+path_surface_margin[1]*2)
zoom_in_WIDTH, zoom_in_HEIGHT = int(path_surface_size[0]*visual_settings['zoom_increment_factor']), int(path_surface_size[1]*visual_settings['zoom_increment_factor'])
zoom_out_WIDTH, zoom_out_HEIGHT = int(path_surface_size[0]/visual_settings['zoom_increment_factor']), int(path_surface_size[1]/visual_settings['zoom_increment_factor'])

if path_surface_size[0] * path_surface_size[1] > 1500*1500:
    warnings.warn("Path surface margin is high, which may cause lag spikes.")

if WIDTH > 1920 or HEIGHT > 1080:
    warnings.warn("Screen dimensions may be too high.")

gui_background = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA, 32)
gui_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA, 32)
empty_gui_surface = gui_surface.copy()

def offset_surface(surface, offset=(0,0)):
    new_surface = surface.copy()
    new_surface.fill(COLORS['EMPTY'])
    new_surface.blit(surface, offset)
    return new_surface

class Environment:

    def __init__(self, name, object_dict={}, start_time=0, delta_time=settings['delta_time'], softening=9000, G=6.6743*10**-11):
        self.name=name
        self.object_dict = object_dict
        self.time = start_time
        self.delta_time = delta_time
        self.softening = softening
        self.G = G

    @property
    def mass(self):
        return sum([body.mass for body in self.objects])

    @property
    def objects(self):
        return self.object_dict.values()

universe = Environment('Universe', start_time=settings['simulation_start_time'])

from modules.Body import Body

from modules import systems

def environment_setup(environment, system):
    environment.name = system.name

    visual_settings['scale'] = system.parent.radius/5

    systems.load_system(environment, system, np.array([0,0,0], dtype=np.float64), np.array([0,0,0], dtype=np.float64))

environment_setup(universe, systems.solar_system)



def main():
    
    camera_offset = np.array([0,0], dtype=np.float64)
    
    def screen_position(true_position, offset=(0,0)):
        return ((true_position[0]) / visual_settings['scale'] + WIDTH/2 + camera_offset[0] + offset[0], \
            -(true_position[1]) / visual_settings['scale'] + HEIGHT/2 + camera_offset[1] + offset[1])

    def true_position(screen_position, offset=(0,0)):
        return ((screen_position[0]-WIDTH/2-camera_offset[0]-offset[1])*visual_settings['scale'], \
            (screen_position[1]-HEIGHT/2-camera_offset[1]-offset[1])*visual_settings['scale'], 0)

    def draw_body(body):
        try:
            screen_pos = screen_position(body.position)
            screen_pos = int(screen_pos[0]), int(screen_pos[1])
            gfxdraw.aacircle(screen, *screen_pos, int(body.size(visual_settings['scale'], visual_settings['rescale_factor'])), body.color)
            gfxdraw.filled_circle(screen, *screen_pos, int(body.size(visual_settings['scale'], visual_settings['rescale_factor'])), body.color)
        except:
            pass

    was_left_clicked = False
    hovering = False

    path_surface = pygame.Surface((WIDTH+path_surface_margin[0]*2, HEIGHT+path_surface_margin[1]*2), pygame.SRCALPHA, 32)
    
    fade_timer = 0  

    # System to check if a key was just pressed
    last_key_state = pygame.key.get_pressed()

    last_draw_time = time.perf_counter()

    tracked_keys = {
        pygame.K_x: False,
        }

    active = True
    while active:
        
        if not settings['paused']:
            
            for body in universe.objects:
                body.update_position(settings['delta_time'], settings['TARGET_SIM_FPS'])
                body.update_acceleration(universe.objects, const.G, universe.softening)
                body.update_velocity(settings['delta_time'], settings['TARGET_SIM_FPS'])
            
            for body in universe.objects:

                pygame.draw.aaline(path_surface, body.darker_color, screen_position(body.position, path_surface_margin), screen_position(body.new_position, path_surface_margin))
                
                body.position = body.new_position
                body.velocity = body.new_velocity
                body.acceleration = body.new_acceleration
        
            universe.time += settings['delta_time'] / settings['TARGET_SIM_FPS']

        clock.tick(settings['TARGET_SIM_FPS'])

        if (fps := clock.get_fps()):
            settings['TRUE_FPS'] = fps

        current_draw_time = time.perf_counter()
        if current_draw_time-last_draw_time < 1/visual_settings['FPS']:
            continue
        last_draw_time = current_draw_time




#        if fade_timer < 0:
#            fade_timer = int(100000000/settings['delta_time'])
#            path_surface.fill(COLORS['FADE'], special_flags=pygame.BLEND_RGBA_MULT)
#        fade_timer -= 1
        
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
                    visual_settings['show_center_of_mass'] = not visual_settings['show_center_of_mass']

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
                    visual_settings['scale'] /= visual_settings['zoom_increment_factor']
                    
                    offset = np.array(true_position(mouse_pos)[:-1], dtype=np.float64)/visual_settings['scale']*(1-visual_settings['zoom_increment_factor'])
                    camera_offset += offset

                    temp = pygame.transform.smoothscale(path_surface, (zoom_in_WIDTH, zoom_in_HEIGHT))
                    path_surface.fill(COLORS['EMPTY'])
                    path_surface.blit(temp, ((path_surface_size[0]-zoom_in_WIDTH)/2+(mouse_pos[0]-WIDTH/2)*(1-visual_settings['zoom_increment_factor'])-1, (path_surface_size[1]-zoom_in_HEIGHT)/2+(mouse_pos[1]-HEIGHT/2)*(1-visual_settings['zoom_increment_factor'])-1))
                    path_surface.fill(COLORS['FADE'], special_flags=pygame.BLEND_RGBA_MULT)

                elif event.y == -1:
                    # Zoom out
                    visual_settings['scale'] *= visual_settings['zoom_increment_factor']
                    
                    offset = np.array(true_position(mouse_pos)[:-1])/visual_settings['scale']*(1-1/visual_settings['zoom_increment_factor'])
                    camera_offset += offset

                    temp = pygame.transform.smoothscale(path_surface, (zoom_out_WIDTH, zoom_out_HEIGHT))
                    path_surface.fill(COLORS['EMPTY'])
                    path_surface.blit(temp, ((path_surface_size[0]-zoom_out_WIDTH)/2+(mouse_pos[0]-WIDTH/2)*(1-1/visual_settings['zoom_increment_factor']), (path_surface_size[1]-zoom_out_HEIGHT)/2+(mouse_pos[1]-HEIGHT/2)*(1-1/visual_settings['zoom_increment_factor'])))

        mouse_relative_position = pygame.mouse.get_rel()
        
        if mouse_state[2]:
            camera_offset += np.array(mouse_relative_position)
            path_surface = offset_surface(path_surface, mouse_relative_position)

        if current_key_state[pygame.K_UP]:
            settings['delta_time'] *= 1.02
        if current_key_state[pygame.K_DOWN]:
            settings['delta_time'] /= 1.02
        
        screen.fill(COLORS['BACKGROUND'])
        screen.blit(path_surface, -path_surface_margin)
        gui_surface = empty_gui_surface.copy() #gui_surface.fill(COLORS['EMPTY'])

        removed_bodies = []
        new_body_dict = {}
        
        # Mouse-body events

        already_hovering = False
        for body in universe.objects:
                
            body_screen_position = screen_position(body.position)
            body_screen_size = body.size(visual_settings['scale'], visual_settings['rescale_factor'])

            mouse_distance = math.sqrt((mouse_pos[0]-body_screen_position[0])**2+(mouse_pos[1]-body_screen_position[1])**2)

            if mouse_distance > body_screen_size+1000:
                continue

            color = COLORS['HOVERING']
            
            if mouse_distance < body_screen_size+12 and not already_hovering:
                already_hovering = True
                hovering = body.mouse_hovering = True
                if mouse_state[0] and not was_left_clicked:
                    body.selected = not body.selected
                    was_left_clicked = True
                elif not mouse_state[0] and was_left_clicked:
                    was_left_clicked = False
                    
                if tracked_keys[pygame.K_x]:
                    angle_increment = 2*math.pi/settings['fragments']
                    mass = body.mass/settings['fragments']
                    velocity = body.velocity
                    velocity_norm = np.linalg.norm(velocity)

                    removed_bodies.append(body.name)
                    
                    for n in range(settings['fragments']):
                        angle = angle_increment*n
                        normalized_direction = np.array([math.cos(angle), math.sin(angle), 0])
                        name = f"{body.name} {n}"
                        new_body_dict[name] = Body(
                            name=name,
                            color=body.color,
                            mass=body.mass/settings['fragments'],
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
                    color = pygame.Color(color)
                    gfxdraw.aacircle(gui_surface, *tuple(int(x) for x in body_screen_position), int(body_screen_size)+(visual_settings['hollow_segment_length']+visual_settings['circumference_thickness']), color)
                    gfxdraw.filled_circle(gui_surface, *tuple(int(x) for x in body_screen_position), int(body_screen_size)+(visual_settings['hollow_segment_length']+visual_settings['circumference_thickness']), color)
                    gfxdraw.filled_circle(gui_surface, *tuple(int(x) for x in body_screen_position), int(body_screen_size)+visual_settings['hollow_segment_length'], COLORS['EMPTY'])
                    pygame.draw.line(gui_surface, COLORS['EMPTY'],
                                    (body_screen_position[0]-(int(body_screen_size)+(visual_settings['hollow_segment_length']+visual_settings['circumference_thickness'])+2), body_screen_position[1]),
                                    (body_screen_position[0]+(int(body_screen_size)+(visual_settings['hollow_segment_length']+visual_settings['circumference_thickness'])+2), body_screen_position[1]),
                                    int(body_screen_size/2)+3)
                    pygame.draw.line(gui_surface, COLORS['EMPTY'],
                                    (body_screen_position[0], body_screen_position[1]-(int(body_screen_size)+(visual_settings['hollow_segment_length']+visual_settings['circumference_thickness'])+2)),
                                    (body_screen_position[0], body_screen_position[1]+(int(body_screen_size)+(visual_settings['hollow_segment_length']+visual_settings['circumference_thickness'])+2)),
                                    int(body_screen_size/2)+3)
                except:
                    pass

                if visual_settings['display_names']:
                    pygame.draw.line(gui_surface, color,
                                    (body_screen_position[0]+int(body_screen_size)+(visual_settings['hollow_segment_length']+visual_settings['circumference_thickness']), body_screen_position[1]),
                                    (body_screen_position[0]+int(body_screen_size)+60, body_screen_position[1]),
                                    )
                    gui_surface.blit(Consolas.render(body.name, True, color), (body_screen_position[0]+int(body_screen_size)+66, body_screen_position[1]-7))

        for body in removed_bodies:
            del universe.object_dict[body]

        universe.object_dict.update(new_body_dict)

        # Draw bodies with low mass first
        for body in sorted(universe.objects, key=lambda x: x.mass):
            draw_body(body)

        if settings['paused']:
            gui_surface.blit(Courier_New.render('SIMULATION PAUSED', True, '#4460ff'), (WIDTH/2-92, 36))

        if hovering:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            
        hovering = False

        if visual_settings['show_center_of_mass']:
            center_of_mass = sum([body.mass*body.position for body in universe.objects])/universe.mass
            
            pygame.draw.circle(screen, '#ff4400', screen_position(center_of_mass), 2)
        
        try:
            simulation_date = datetime.date.fromtimestamp(universe.time).strftime('%Y-%m-%d')
        except OSError:
            pass

        speed = settings['delta_time']*settings['TRUE_FPS']/settings['TARGET_SIM_FPS']

        info = [
            (f"Date: {simulation_date}", COLORS['TEXT']),
            (f"{round(speed,2)} seconds per second", COLORS['TEXT']),
            (f"{round(speed/60/60/24,2)} days per second", COLORS['TEXT']),
            (f"{round(speed/60/60/24/365.25,3)} years per second", COLORS['TEXT']),
            (f"{round(visual_settings['scale']/10**(int(math.log10(visual_settings['scale']))),3)}e{int(math.log10(visual_settings['scale']))} meters per pixel", COLORS['TEXT']),
            (f"Total mass: {round(universe.mass/10**(int(math.log10(universe.mass))),6)}e{int(math.log10(universe.mass))} kg", COLORS['TEXT']),
            (f"FPS: {round(settings['TRUE_FPS'],3)}", COLORS['TEXT'])
            ]
        
        for n, i in enumerate(info):
            gui_surface.blit(Courier_New.render(i[0], True, i[1]), (24, 20*n+16))
            
        screen.blit(gui_surface, (0,0))

        pygame.display.update()

if __name__ == '__main__':
    main()

pygame.quit()
