import logging
from json import load
from os.path import pardir, join, abspath
from utils.Models import LoggerSettings
from os import stat

log_app = logging.getLogger('__init__')

try:
    PROJECT_DIR = abspath(pardir)
    config_file = ('configs', 'config.json')
    config_file = join(PROJECT_DIR, config_file[0], config_file[1])

    with open(config_file, 'r') as file:
        CONFIG = load(file)

    LOGGER_SETTINGS = CONFIG.get('logger_setting')
    LOGGER_SETTINGS = LoggerSettings(**LOGGER_SETTINGS)
    ftp_connection = CONFIG.get('ftp_connection')
    route = CONFIG.get('route')
    settings = CONFIG.get('settings')

except:
    log_app.critical('Caught exception wile try to read config',
                     exc_info=True)
    exit(-1073741510)

try:

    logging.basicConfig(
        level=LOGGER_SETTINGS.level,
        filename=LOGGER_SETTINGS.filename,
        filemode=LOGGER_SETTINGS.filemode,
        format=LOGGER_SETTINGS.format,
        encoding='utf-8'

    )

    CR_DATE = stat(LOGGER_SETTINGS.filename).st_ctime

    log_app.info(f'Main process has been init, log_file create date was {CR_DATE}')

    del CONFIG, config_file

except:
    log_app.critical('Caught exception wile try to set up logging settings',
                     exc_info=True)
    exit(-1073741510)
