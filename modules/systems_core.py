
import math

if __name__ == '__main__':
    import const
    import spacemath
    from ObjectClasses import Body
else:
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

        parent_body = Body(
            parent.name,
            parent.color,
            parent.mass,
            parent.radius,
            parent_position,
            parent_velocity,
        )

    environment.object_dict[system.parent.name] = parent_body

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

            body = Body(
                planet.name,
                planet.color,
                planet.mass,
                planet.radius,

                body_position + parent_position,
                body_velocity + parent_velocity
            )
            environment.object_dict[planet.name] = body


