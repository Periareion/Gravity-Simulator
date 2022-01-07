from astropy.constants import G, au

import os

if __name__ == '__main__':
    import configurator as cfg
else:
    from modules import configurator as cfg

os.path.abspath(os.path.join('..', os.getcwd()))

CONSTS = {
    'G': G.value,
    'AU': au.value,
}

updated_settings = cfg.read_config('config.cfg')

cfg.update_dictionaries(updated_settings, [CONSTS])

globals().update(CONSTS)
