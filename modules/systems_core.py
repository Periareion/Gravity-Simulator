
import math

import numpy as np

try:
    import const
    import spacemath
    from ObjectClasses import Body
except ModuleNotFoundError:
    from modules import const
    from modules import spacemath
    from modules.ObjectClasses import Body

class System:

    def __init__(self, name, parent, planets):
        self.name = name
        self.parent = parent
        self.planets = planets

def load_system(environment, system, grandparent_position, grandparent_velocity, grandparent=None):
    print(f"Loading {system.name}")
    parent = system.parent

    if grandparent == None:
        parent_position = grandparent_position
        parent_velocity = grandparent_velocity

        parent_body = Body(
            parent.name,
            parent.color,
            parent.mass,
            parent.radius,
            parent_position,
            parent_velocity,
        )

    else:
        parent_position, parent_velocity = spacemath.kep_to_cart(
            const.G*grandparent.mass,
            parent.a,
            parent.e,
            math.radians(parent.i),
            math.radians(parent.lon_AN),
            math.radians(parent.lon_AN),
            math.radians(parent.ML),
            environment.time,
            parent.Epoch,
        )

        parent_position += grandparent_position
        parent_velocity += grandparent_velocity

    momentum_sum = np.array([0,0,0], dtype=np.float64)

    bodies = []

    for planet in system.planets:
        if isinstance(planet, System):
            # Sub-system
            sub_system = planet
            load_system(environment, sub_system, parent_position, parent_velocity, parent)

        else:
            # Planet
            body_position, body_velocity = spacemath.kep_to_cart(
                const.G*parent.mass,
                planet.a,
                planet.e,
                math.radians(planet.i),
                math.radians(planet.lon_AN),
                math.radians(planet.lon_Pe),
                math.radians(planet.ML),
                environment.time,
                planet.Epoch,
            )

            #if 'moon' in planet.tags:
            #    planet.mass = 1
            
            body = Body(
                planet.name,
                planet.color,
                planet.mass,
                planet.radius,

                body_position + parent_position,
                body_velocity + parent_velocity,
                
                planet.tags,
            )

            momentum_sum = momentum_sum + planet.mass*np.array(body_velocity, dtype=np.float64)

            environment.object_dict[body.name] = body
        
    parent_body = Body(
            parent.name,
            parent.color,
            parent.mass,
            parent.radius,
            parent_position,
            parent_velocity - momentum_sum/parent.mass,
        )
    print(parent.name, momentum_sum/parent.mass)

    environment.object_dict[system.parent.name] = parent_body
