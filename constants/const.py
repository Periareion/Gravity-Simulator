from astropy.constants import G, au

import sys, os
sys.path.insert(0, os.path.abspath('../modules'))
sys.path.insert(0, os.path.abspath('./modules'))

import configurator as cfg

dir = os.path.dirname(__file__)

CONSTS = {
    'G': G.value,
    'AU': au.value,
}

updated_settings = cfg.readConfig(dir + '/../config.cfg')

cfg.update_dictionaries(updated_settings, [CONSTS])

globals().update(CONSTS)
