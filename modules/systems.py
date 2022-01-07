import math

if __name__ == '__main__':
    import const
    from systems_core import System
    from ObjectClasses import RawObject as Object
    from objects import *
else:
    from modules import const
    from modules.systems_core import System
    from modules.ObjectClasses import RawObject as Object
    from modules.objects import *

earth_system = System(
    'Earth System',

    Earth,

    [
        System(
            'Lunar System',

            Moon,

            [
                #LRO
            ]
        )
    ]
)

mars_system = System(
    'Mars System',

    Mars,

    [
        Phobos,

        Deimos,
    ]
)

jupiter_system = System(
    'Jupiter System',

    Jupiter,

    [
        Io,

        Europa,

        Ganymede,

        Callisto,
    ]
)

solar_system = System(
    'Solar System',

    Sun,

    [
        Mercury,

        Venus,

        earth_system,

        mars_system.parent,

        jupiter_system,

        Saturn,

        Uranus,

        Neptune,
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
