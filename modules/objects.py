
try:
    import const
    from ObjectClasses import RawObject
except ModuleNotFoundError:
    from modules import const
    from modules.ObjectClasses import RawObject

Object = RawObject

Sun = Object(
    'Sun',
    '#eeff55',
    1.98847*10**30,
    6.9634*10**8,
    
    tags=['star'],
)

Mercury = Object(
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

    tags=[],
)

Venus = Object(
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

    tags=['atmosphere'],
)

Earth = Object(
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

    tags=['atmosphere'],
)

Moon = Object(
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

LRO = Object(
    'Lunar Reconnaissance Orbiter',
    '#ffb040',
    1000,
    1,

    1.825*10**6,
    0.0397,
    0,
    0,
    0,
    0,

    tags=['probe'],
)

Mars = Object(
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

    tags=['atmosphere'],
)

Phobos = Object(
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

    tags=['moon'],
)

Deimos = Object(
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

    tags=['moon'],
)

Jupiter = Object(
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

    tags=['gas'],
)

Io = Object(
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
)

Europa = Object(
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

    tags=['moon'],
)

Ganymede = Object(
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

    tags=['moon'],
)

Callisto = Object(
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

    tags=['moon'],
)

Saturn = Object(
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

    tags=['gas'],
)

Rhea = Object(
    'Rhea',
    '#999999',
    2.31*10**21,
    7.63*10**5,

    5.2704*10**8,
    0.0010,
    0.35,
    0,
    0,
    0,

    tags=['moon']
)

Titan = Object(
    'Titan',
    '#aa8f59',
    1.3455*10**23,
    2.575*10**6,

    1.22183*10**9,
    0.0292,
    0.33,
    0,
    0,
    0,

    tags=['moon', 'atmosphere'],
)

Iapetus = Object(
    'Iapetus',
    '#dddacc',
    1.81*10**21,
    7.46*10**5,

    3.5613*10**9,
    0.0283,
    14.72,
    0,
    0,
    0,

    tags=['moon']
)

Uranus = Object(
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

    tags=['gas'],
)

Neptune = Object(
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

    tags=['gas'],
)