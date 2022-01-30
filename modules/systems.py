from importlib.util import module_for_loader
import math

try:
    import const
    from systems_core import System
    from ObjectClasses import RawObject as Object
    from objects import *
except ModuleNotFoundError:
    from modules import const
    from modules.systems_core import System
    from modules.ObjectClasses import RawObject as Object
    from modules.objects import *

test_system = System(
    'Test',

    Sun,

    [
        System(
            'Planet with moon',
            
            Object(
                'Planet',
                '#cc0000',
                10**25,
                10**7,

                1*const.AU,
                0,
                0,
                0,
                0,
                0,
            ),
            
            [
                Object(
                    'Moon',
                    '#0066dd',
                    10**23,
                    10**6,
                    
                    2*10**8,
                    0,
                    0,
                    0,
                    0,
                    0,
                )
            ]
        )
    ]
)

earth_system = System(
    'Earth System',

    Earth,

    [
        Moon
        #System(
        #    'Lunar System',
#
        #    Moon,
#
        #    [
        #        #LRO
        #    ]
        #)
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

saturn_system = System(
    'Saturn System',

    Saturn,

    [
        Rhea,

        Titan,

        Iapetus,
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

        saturn_system,

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
