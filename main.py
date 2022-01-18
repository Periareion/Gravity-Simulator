import sys
import os
import warnings
import time
import datetime
import math

sys.path.append('.\\assets')
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

import pygame
from pygame import gfxdraw

import numpy as np

from modules import configurator as cfg
from modules import const
from modules import systems

WIDTH, HEIGHT = 1080, 720

settings = {
    'system': systems.earth_system,
    'TARGET_SIM_FPS': 600,
    'paused': False,
    'simulation_start_time': time.time(),
    'delta_time': 200000,
    'fragments': 5,
}

visual_settings = {
    'FPS': 60,
    'scale': const.AU / 100,
    'focus': None,
    'render_paths': True,
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


def offset_surface(surface, offset=(0,0)):
    new_surface = surface.copy()
    new_surface.fill(COLORS['EMPTY'])
    new_surface.blit(surface, offset)
    return new_surface

class Environment:

    def __init__(self, name, object_dict={}, start_time=0, delta_time=settings['delta_time'], softening=5000, G=6.6743*10**-11):
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

from modules.ObjectClasses import Body

from modules import systems_core

def environment_setup(environment, system):
    environment.name = system.name

    visual_settings['scale'] = system.parent.radius/2

    systems_core.load_system(environment, system, np.array([0,0,0], dtype=np.float64), np.array([0,0,0], dtype=np.float64))


universe = Environment('Universe', start_time=settings['simulation_start_time'])

environment_setup(universe, settings['system'])

def get_focus_position():
    focus = visual_settings['focus']
    
    if focus == None:
        return np.array([0,0], dtype=np.float64)
    
    elif isinstance(focus, Body):
        return focus.position[:-1]

def draw_body(body, surf, position):
    try:
        body_screen_position = position
        body_screen_position = int(body_screen_position[0]), int(body_screen_position[1])
        body_screen_size = int(body.size(visual_settings['scale'], visual_settings['rescale_factor']))

        gfxdraw.aacircle(surf, *body_screen_position, body_screen_size, body.color)
        gfxdraw.filled_circle(surf, *body_screen_position, body_screen_size, body.color)
    except:
        pass

def draw_body_info(body, surf, name_font, info_font, position):
    try:
        body_screen_position = position
        body_screen_position = int(body_screen_position[0]), int(body_screen_position[1])
        body_screen_size = int(body.size(visual_settings['scale'], visual_settings['rescale_factor']))

        color = COLORS['HOVERING']

        if body.selected:
            color = body.color
            if body.mouse_hovering:
                color = COLORS['SELECTED']

        if body.mouse_hovering or body.selected:
            color = pygame.Color(color)
            gfxdraw.aacircle(surf, *((int(x) for x in body_screen_position)), int(body_screen_size)+(visual_settings['hollow_segment_length']+visual_settings['circumference_thickness']), color)
            gfxdraw.filled_circle(surf, *((int(x) for x in body_screen_position)), int(body_screen_size)+(visual_settings['hollow_segment_length']+visual_settings['circumference_thickness']), color)
            gfxdraw.filled_circle(surf, *((int(x) for x in body_screen_position)), int(body_screen_size)+visual_settings['hollow_segment_length'], COLORS['EMPTY'])
            pygame.draw.line(surf, COLORS['EMPTY'],
                            (body_screen_position[0]-(int(body_screen_size)+(visual_settings['hollow_segment_length']+visual_settings['circumference_thickness'])+2), body_screen_position[1]),
                            (body_screen_position[0]+(int(body_screen_size)+(visual_settings['hollow_segment_length']+visual_settings['circumference_thickness'])+2), body_screen_position[1]),
                            int(body_screen_size/2)+3)
            pygame.draw.line(surf, COLORS['EMPTY'],
                            (body_screen_position[0], body_screen_position[1]-(int(body_screen_size)+(visual_settings['hollow_segment_length']+visual_settings['circumference_thickness'])+2)),
                            (body_screen_position[0], body_screen_position[1]+(int(body_screen_size)+(visual_settings['hollow_segment_length']+visual_settings['circumference_thickness'])+2)),
                            int(body_screen_size/2)+3)

            if visual_settings['display_names']:
                pygame.draw.line(surf, color,
                                (body_screen_position[0]+int(body_screen_size)+(visual_settings['hollow_segment_length']+visual_settings['circumference_thickness']), body_screen_position[1]),
                                (body_screen_position[0]+int(body_screen_size)+60, body_screen_position[1]),
                                )
                surf.blit(name_font.render(body.name, True, color), (body_screen_position[0]+int(body_screen_size)+66, body_screen_position[1]-7))

                body_info = [
                    f"Mass: {np.format_float_scientific(body.mass, 4)}",
                    f"Radius: {np.format_float_scientific(body.radius, 4)}",
                ]

                for n, text in enumerate(body_info):
                    surf.blit(info_font.render(text, True, color), (body_screen_position[0]+int(body_screen_size)+70, body_screen_position[1]+9+15*n))
    except:
        pass

def draw_path_line(body, surf, pos1, pos2):
    pygame.draw.aaline(surf, body.darker_color, pos1, pos2)

def redraw_path(body, surf, points):
    body.path_points.append(body.position.copy())
    pygame.draw.aalines(surf, body.darker_color, False, points)

def purge_dict(dict, purgees):
    for key in purgees:
        del dict[key]


def main():

    camera_offset = np.array([0,0], dtype=np.float64)

    def screen_position(true_position, offset=(0,0), focus_position=(0,0)):
        return ((true_position[0] - focus_position[0]) / visual_settings['scale'] + WIDTH/2 + camera_offset[0] + offset[0], \
            -(true_position[1] - focus_position[1]) / visual_settings['scale'] + HEIGHT/2 + camera_offset[1] + offset[1])

    def true_position(screen_position, offset=(0,0), focus_position=(0,0)):
        return ((screen_position[0]-WIDTH/2-camera_offset[0]-offset[1])*visual_settings['scale'] + focus_position[0], \
            (screen_position[1]-HEIGHT/2-camera_offset[1]-offset[1])*visual_settings['scale'], + focus_position[1], 0)

    updated_settings = cfg.read_config('config.cfg')
    cfg.update_dictionaries(updated_settings, [settings, visual_settings, COLORS])

    pygame.font.init()
    Courier_New = pygame.font.SysFont('Courier New', 16)
    Consolas = pygame.font.SysFont('Consolas', 16)
    Consolas_small = pygame.font.SysFont('Consolas', 14)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Gravity Simulator')
    pygame.display.set_icon(pygame.image.load('assets\\icon.png'))

    clock = pygame.time.Clock()

    if WIDTH > 1920 or HEIGHT > 1080:
        warnings.warn("Screen dimensions may be too high.")

    gui_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    was_left_clicked = False
    hovering = False

    path_surface_size = (WIDTH, HEIGHT)
    path_surface = pygame.Surface(path_surface_size, pygame.SRCALPHA)

    k = 0

    # System to check if a key was just pressed
    last_key_state = pygame.key.get_pressed()

    last_draw_time = time.perf_counter()

    tracked_keys = {
        pygame.K_x: False,
    }

    running = True
    while running:

        focus_position = get_focus_position()
        
        if not settings['paused']:
            
            for body in universe.objects:

                body.update_acceleration(universe, const.G)
                body.update_velocity(settings['delta_time'], settings['TARGET_SIM_FPS'])

                body.old_position = body.position.copy()
                body.update_position(settings['delta_time'], settings['TARGET_SIM_FPS'])
                body.new_position = body.position.copy()
            
            removed_bodies = []

            for body in universe.objects:

                if body in removed_bodies:
                    continue

                for body2 in universe.objects:

                    if body2 in removed_bodies or body == body2:
                        continue

                    dist = body2.position - body.position
                    dist_norm = math.sqrt(sum((dim**2 for dim in dist))+universe.softening**2)

                    if dist_norm < body.radius + body2.radius and ((body.name not in removed_bodies) and (body2.name not in removed_bodies)):
                        smaller, larger = sorted((body, body2), key=lambda x: x.mass)

                        print(f"{smaller.name} collided with {larger.name}")

                        larger.mass += smaller.mass
                        removed_bodies.append(smaller.name)

                        larger.velocity = (larger.mass*larger.velocity + smaller.mass*smaller.velocity) / larger.mass
            
            purge_dict(universe.object_dict, removed_bodies)

            k += 1
            for body in universe.objects:
                
                if visual_settings['render_paths']:
                    draw_path_line(body, path_surface, screen_position(body.old_position), screen_position(body.new_position))

                if not k % 20:
                    body.path_points.append(body.new_position)
                    while len(body.path_points) > 500*15/math.sqrt(len(universe.objects)):
                        del body.path_points[0]

            universe.time += settings['delta_time'] / settings['TARGET_SIM_FPS']

        clock.tick(settings['TARGET_SIM_FPS'])

        if (fps := clock.get_fps()):
            settings['TRUE_FPS'] = fps

        current_draw_time = time.perf_counter()
        if current_draw_time-last_draw_time < 1/visual_settings['FPS']:
            continue
        last_draw_time = current_draw_time
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_state = pygame.mouse.get_pressed()
        current_key_state = pygame.key.get_pressed()

        for key in tracked_keys.keys():
            if last_key_state[key]:
                # Pressed last frame
                tracked_keys[key] = False
            elif current_key_state[key]:
                # Pressed this and not last frame.
                tracked_keys[key] = True

        last_key_state = current_key_state
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
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
                
                elif event.key == pygame.K_p:
                    visual_settings['render_paths'] = not visual_settings['render_paths']

                elif event.key == pygame.K_v:
                    contents = cfg.read_line(input("Manually redefine a variable: "))
                    if contents == 'stop':
                        running = False
                    elif contents == None:
                        pass
                    elif len(contents) == 2:
                        key, value = contents
                        cfg.update_dictionaries({key: value}, [settings, visual_settings, COLORS, globals()])
                    
            elif event.type == pygame.MOUSEWHEEL:
                
                if event.y == 1:
                    # Zoom in
                    
                    visual_settings['scale'] /= visual_settings['zoom_increment_factor']
                    
                    offset = (np.array(true_position(mouse_pos)[0:2], dtype=np.float64)/visual_settings['scale']*(1-visual_settings['zoom_increment_factor']))
                    camera_offset += offset

                    if visual_settings['render_paths']:
                        path_surface.fill(COLORS['EMPTY'])
                        for body in universe.objects:
                            redraw_path(body, path_surface, [screen_position(pos) for pos in body.path_points])

                elif event.y == -1:
                    # Zoom out
                    
                    visual_settings['scale'] *= visual_settings['zoom_increment_factor']
                    
                    offset = (np.array(true_position(mouse_pos)[0:2], dtype=np.float64)/visual_settings['scale']*(1-1/visual_settings['zoom_increment_factor']))
                    camera_offset += offset

                    if visual_settings['render_paths']:
                        path_surface.fill(COLORS['EMPTY'])
                        for body in universe.objects:
                            redraw_path(body, path_surface, [screen_position(pos) for pos in body.path_points])

        mouse_relative_position = pygame.mouse.get_rel()
        
        if mouse_state[2]:
            camera_offset += np.array(mouse_relative_position)
            path_surface = offset_surface(path_surface, mouse_relative_position)

        if current_key_state[pygame.K_UP]:
            settings['delta_time'] *= 1.02
        if current_key_state[pygame.K_DOWN]:
            settings['delta_time'] /= 1.02
        
        screen.fill(COLORS['BACKGROUND'])

        if visual_settings['render_paths']:
            screen.blit(path_surface, (0,0))

        gui_surface.fill(COLORS['EMPTY'])

        # Need seperate because they're running at different paces
        removed_bodies = []
        new_bodies = {}
        
        # Mouse-body events

        already_hovering = False
        for body in sorted(universe.objects, key=lambda x: x.mass, reverse=True):
                
            body_screen_position = screen_position(body.position)
            body_screen_size = body.size(visual_settings['scale'], visual_settings['rescale_factor'])

            mouse_distance = math.sqrt((mouse_pos[0]-body_screen_position[0])**2+(mouse_pos[1]-body_screen_position[1])**2)

            if mouse_distance > body_screen_size+1000:
                continue
            
            if mouse_distance < body_screen_size+12 and not already_hovering:
                already_hovering = True
                hovering = body.mouse_hovering = True

                if mouse_state[0] and not was_left_clicked:
                    body.selected = not body.selected
                    was_left_clicked = True
                elif not mouse_state[0] and was_left_clicked:
                    was_left_clicked = False
                    
                if tracked_keys[pygame.K_x]:
                    body.shatter(settings['fragments'], removed_bodies, new_bodies)
                    tracked_keys[pygame.K_x] = False
                    continue
                
            else:
                body.mouse_hovering = False

        purge_dict(universe.object_dict, removed_bodies)

        universe.object_dict.update(new_bodies)

        # Draw bodies with low mass first to prioritize planets over moons.
        for body in sorted(universe.objects, key=lambda x: x.mass):
            draw_body(body, screen, screen_position(body.position))
            draw_body_info(body, gui_surface, Consolas, Consolas_small, screen_position(body.position))

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
            simulation_date = f"{int(1970+universe.time/60/60/24/365.25)}"

        speed = settings['delta_time']*settings['TRUE_FPS']/settings['TARGET_SIM_FPS']

        info = [
            (f"Date: {simulation_date}", COLORS['TEXT']),
            (f"{round(speed,2)} seconds per second", COLORS['TEXT']),
            (f"{round(speed/60/60/24,2)} days per second", COLORS['TEXT']),
            (f"{round(speed/60/60/24/365.25,3)} years per second", COLORS['TEXT']),
            (f"{round(visual_settings['scale']/10**(int(math.log10(visual_settings['scale']))),3)}e{int(math.log10(visual_settings['scale']))} meters per pixel", COLORS['TEXT']),
            #(f"Total mass: {round(universe.mass/10**(int(math.log10(universe.mass))),6)}e{int(math.log10(universe.mass))} kg", COLORS['TEXT']),
            (f"Number of bodies: {len(universe.objects)}", COLORS['TEXT']),
            (f"FPS: {round(settings['TRUE_FPS'],3)}", COLORS['TEXT']),
        ]
        
        for n, i in enumerate(info):
            gui_surface.blit(Courier_New.render(i[0], True, i[1]), (24, 20*n+16))
            
        screen.blit(gui_surface, (0,0))

        pygame.display.update()

if __name__ == '__main__':
    main()

pygame.quit()
