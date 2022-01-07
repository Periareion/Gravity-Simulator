import math

import pygame
import numpy as np

class Body:

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

        self.path_points = [self.position]
        
        self.darker_color = pygame.Color(*(int(0.5*x) for x in [self.color.r, self.color.g, self.color.b]))
        self.mouse_hovering = False
        self.selected = False

    def size(self, scale, rescale_factor):
        # meters / meters per pixel = pixels
        size = self.radius/scale
        
        size *= rescale_factor

        #size = (self.mass)**(1/20)*200000000/visual_settings['scale']
            
        if size < 1:
            size = 1
            
        return size

    def update_position(self, delta_time, fps):

        self.new_position = self.position + self.velocity * delta_time / fps + self.acceleration*(0.5*(delta_time/fps)**2)

    def update_acceleration(self, universe_objects, G, softening):
        
        self.new_acceleration = np.array([0,0,0], dtype=np.float64)
        
        for other in universe_objects:
            dist = other.position - self.new_position
            dist_norm = math.sqrt(sum((dim**2 for dim in dist))+softening**2)
            
            if self == other or dist_norm < self.radius + other.radius:
                continue
            
            self.new_acceleration += G * other.mass * dist / dist_norm**3

    def update_velocity(self, delta_time, fps):
        
        self.new_velocity = self.velocity + (self.new_acceleration + self.acceleration) * 0.5 * delta_time / fps