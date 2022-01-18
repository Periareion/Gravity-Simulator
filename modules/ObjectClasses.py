import math

import pygame
import numpy as np

try:
    import const
except ModuleNotFoundError:
    from modules import const

class RawObject:

    def __init__(
            self,
            name,
            color='#1ecaee',
            mass=1,
            radius=1,
            a=None,
            e=None,
            i=None,
            lon_AN=None,
            lon_Pe=None,
            ML=None,
            Epoch=None,
            tags=None,
        ):

        self.name = name
        self.color = color
        self.tags = tags
        
        self.mass = mass
        self.radius = radius

        self.volume = 4*math.pi*self.radius**3/3
        self.density = self.mass/self.volume
        
        self.semi_major_axis = self.a = a
        self.eccentricity = self.e = e
        self.inclination = self.i = i
        self.longitude_ascending_node = self.lon_AN = lon_AN
        self.longitude_periapsis = self.lon_Pe = lon_Pe
        self.mean_longitude = self.ML = ML

        if Epoch == 'J2000' or Epoch == None:
            self.Epoch = 30*365.25*24*60*60
        else:
            self.Epoch = (Epoch-1970)*365.25*24*60*60

class Body:

    def __init__(
            self,
            name='Conway',
            color=pygame.Color(200,0,0),
            mass=10**6,
            radius=0.1,
            position=None,
            velocity=None,
            tags=[],
            ):

        self.name = name
        self.color = pygame.Color(color)
        self.mass = mass
        self.radius = radius
        self.tags = tags.copy()

        self.position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.acceleration = np.array([0,0,0], dtype=np.float64)

        self.path_points = [self.position.copy(), self.position.copy()]
        
        self.darker_color = pygame.Color(*(int(0.5*x) for x in [self.color.r, self.color.g, self.color.b]))
        self.mouse_hovering = False
        self.selected = False

    def size(self, scale, rescale_factor):
        # meters / meters per pixel = pixels
        size = self.radius/scale
        
        if 'planet' in self.tags:
            size *= rescale_factor
            
        if size < 1:
            size = 1
            
        return size

    def update_acceleration(self, universe, G):
        
        self.acceleration = np.array([0,0,0], dtype=np.float64)
        
        for other in universe.objects:

            if self == other:
                continue

            dist = other.position - self.position
            dist_norm = math.sqrt(sum((dim**2 for dim in dist))+universe.softening**2)
            
            self.acceleration += G * other.mass * dist / dist_norm**3

    def update_velocity(self, delta_time, fps):
        
        self.velocity = self.velocity + self.acceleration * delta_time / fps

    def update_position(self, delta_time, fps):

        self.position = self.position + self.velocity * delta_time / fps #= self.position + self.velocity * delta_time / fps + self.acceleration*(0.5*(delta_time/fps)**2)
        
    def shatter(self, n, removed_bodies, new_body_dict):
        angle_increment = 2*math.pi/n
        internal_angle = math.pi-2*math.pi/n
        mass = self.mass/n

        removed_bodies.append(self.name)
        fragment_radius = self.radius*0.4
        distance_from_center = fragment_radius/math.cos(internal_angle/2)

        for k in range(n):
            
            angle = angle_increment*k
            normalized_direction = np.array([math.cos(angle), math.sin(angle), 0])
            name = f"{self.name} {k}"
            new_body_dict[name] = Body(
                name=name,
                color=self.color,
                mass=mass,
                radius=fragment_radius,
                position=self.position+normalized_direction*distance_from_center,
                velocity=self.velocity+(normalized_direction)*50000*math.sqrt(const.G*(n/2-1)*mass**0.6/distance_from_center),
            )