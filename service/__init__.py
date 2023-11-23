import logging
from json import load
from os.path import pardir, join, abspath

log_app = logging.getLogger('app')

PROJECT_DIR = abspath(pardir)
CONFIG_FILE = ('configs', 'config_decode.json')
CONFIG_FILE = join(PROJECT_DIR, CONFIG_FILE[0], CONFIG_FILE[1])

try:
    log_app = logging.getLogger('app')

    with open(CONFIG_FILE, 'r') as file:
        CONFIG = load(file)

    LOGGER_SETTINGS = CONFIG.get('logger_setting')


except:
    log_app.critical('Caught exception wile try to read config',
                     exc_info=True)
    exit(-1073741510)

try:

    logging.basicConfig(
        level=LOGGER_SETTINGS.get('level'),
        filename=join(pardir, LOGGER_SETTINGS.get('filename')[0], LOGGER_SETTINGS.get('filename')[1]),
        filemode=LOGGER_SETTINGS.get('filemode'),
        format=LOGGER_SETTINGS.get('format')
    )

except:
    log_app.critical('Caught exception wile try to set up logging settings',
                     exc_info=True)
    exit(-1073741510)





