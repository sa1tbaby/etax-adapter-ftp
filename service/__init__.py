import logging
from json import load
from os.path import pardir, join, abspath

try:
    PROJECT_DIR = abspath(pardir)
    config_file = ('configs', 'config.json')
    config_file = join(PROJECT_DIR, config_file[0], config_file[1])

    log_app = logging.getLogger('app')

    with open(config_file, 'r') as file:
        CONFIG = load(file)

    logger_settings = CONFIG.get('logger_setting')
    ftp_connection = CONFIG.get('ftp_connection')
    route = CONFIG.get('route')
    settings = CONFIG.get('settings')

except:
    log_app.critical('Caught exception wile try to read config',
                     exc_info=True)
    exit(-1073741510)

try:
    logger_filename = logger_settings.get('filename')
    logger_filename = join(PROJECT_DIR, logger_filename[0], logger_filename[1])

    logging.basicConfig(
        level=logger_settings.get('level'),
        filename=logger_filename,
        filemode=logger_settings.get('filemode'),
        format=logger_settings.get('format'),
        encoding='utf-8'

    )

    del logger_filename, CONFIG, config_file

except:
    log_app.critical('Caught exception wile try to set up logging settings',
                     exc_info=True)
    exit(-1073741510)








