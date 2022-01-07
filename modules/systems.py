
import math

if __name__ == '__main__':
    import const
    import spacemath
    from Body import Body
else:
    from modules import const
    from modules import spacemath
    from modules.Body import Body

class Object:

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


earth_system = System(

    'Earth System',

    Object(
        'Earth',
        '#336eee',
        5.972*10**24,
        6.371*10**6,

        1.00000011*const.AU,
        0.01671022,
        0.00005,
        -11.26064,
        102.94719,
        100.46435,

        tags=['planet'],
    ),
    
    [
        Object(
            'Moon',
            '#b0c0f0',
            7.346*10**22,
            1.7374*10**6,

            3.844*10**8,
            0.0549,
            5.145,
            0,
            0,
            0,

            tags=['moon'],
        )
    ]
)

mars_system = System(

    'Mars System',

    Object(
        'Mars',
        '#dd6030',
        6.4171*10**23,
        3.3895*10**6,

        1.52366231*const.AU,
        0.09341233,
        1.85061,
        49.57854,
        336.04084,
        355.45332,
    ),

    [
        Object(
            'Phobos',
            '#998f88',
            1.06*10**16,
            1.30*10**4,

            9.378*10**6,
            0.0151,
            1.08,
            0,
            0,
            0,

            tags=['moon']
        ),

        Object(
            'Deimos',
            '#aa9988',
            2.4*10**15,
            7.8*10**3,

            2.3459*10**7,
            0.0005,
            1.79,
            0,
            0,
            0,

            tags=['moon']
        ),
    ],
)

jupiter_system = System(

    'Jupiter System',

    Object(
        'Jupiter',
        '#cfac80',
        1.89813*10**27,
        7.1492*10**7,

        5.20336301*const.AU,
        0.04839266,
        1.30530,
        100.55615,
        14.75385,
        34.40438,

        tags=['planet', 'gas'],
    ),

    [
        Object(
            'Io',
            '#ccc240',
            8.93*10**22,
            3.643*10**6/2,

            4.22*10**8,
            0.004,
            0.04,
            0,
            0,
            0,
            
            tags=['moon'],
        ),

        Object(
            'Europa',
            '#81582c',
            4.80*10**22,
            3.122*10**6/2,

            6.71*10**8,
            0.009,
            0.47,
            0,
            0,
            0,

            tags=['moon']
        ),

        Object(
            'Ganymede',
            '#92837a',
            1.482*10**23,
            5.262*10**6/2,

            1.070*10**9,
            0.001,
            0.18,
            0,
            0,
            0,

            tags=['moon']
        ),

        Object(
            'Callisto',
            '#3e5460',
            1.076*10**23,
            4.821*10**6/2,
            
            1.883*10**9,
            0.007,
            0.19,
            0,
            0,
            0,

            tags=['moon']
        ),
    ]
)

solar_system = System(

    "Solar System",
    
    Object(
        'Sun',
        '#eeff55',
        1.98847*10**30,
        6.9634*10**8,
        
        tags=['star'],
    ),

    [

        Object(
            'Mercury',
            '#666666',
            3.3011*10**23,
            2.4397*10**6,

            0.38709893*const.AU,
            0.20563069,
            7.00487,
            48.33167,
            77.45645,
            252.25084,

            tags=['planet'],
        ),

        Object(
            'Venus',
            '#eebb55',
            4.8675*10**24,
            6.0518*10**6,

            0.72333199*const.AU,
            0.00677323,
            3.39471,
            76.68069,
            131.53298,
            181.97973,

            tags=['planet'],
        ),
        
        earth_system,

        # Ignore Mars' moons (Only take the parent, and leave two orphans in idle limbo)
        mars_system.parent,

        jupiter_system,

        Object(
            'Saturn',
            '#eecc76',
            5.6832*10**26,
            6.268*10**7,

            9.53707032*const.AU,
            0.05415060,
            2.48446,
            113.71504,
            92.43194,
            49.94434,
        ),

        Object(
            'Uranus',
            '#88bbee',
            8.6811*10**25,
            2.5559*10**7,

            19.19126393*const.AU,
            0.04716771,
            0.76986,
            74.22988,
            170.96424,
            313.23218,
        ),

        Object(
            'Neptune',
            '#4455dd',
            1.02409*10**26,
            2.4764*10**7,

            30.06896348*const.AU,
            0.00858587,
            1.76917,
            131.72169,
            44.97135,
            304.88003,
        ),
    ]
    
)

as_to_m = lambda arc_s: arc_s*math.pi*8178/6480000*3.08609*10**16

sagittarius = System(

    "Sagittarius A* Cluster",

    Object(
        'Sagittarius A*',
        '#ff9900',
        8.2601*10**36,
        2.2*10**8,
    ),

    [
        Object(
            'S1',
            '#bb00ff',
            10**30,
            10**8,

            as_to_m(0.5950),
            0.5560,
            119.14,
            342.04,
            122.30,
            342.04+122.30,
            2001.800,
        ),

        Object(
            'S2',
            '#ff0000',
            10**30,
            10**8,

            as_to_m(0.1251),
            0.8843,
            133.91,
            228.07,
            66.25,
            228.07+66.25,
            2018.379
        ),

        Object(
            'S8',
            '#ffdd00',
            10**30,
            10**8,

            as_to_m(0.4047),
            0.8031,
            74.37,
            315.43,
            346.70,
            315.43+346.70,
            1983.640
        ),

    ]

)
