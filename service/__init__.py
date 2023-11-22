import logging
from os.path import pardir, join
from json import load

CONFIG_NAME = ('configs', 'config_decode.json')
CONFIG_NAME = join(
    pardir, CONFIG_NAME[0], CONFIG_NAME[1]
)

with open(CONFIG_NAME, 'r') as file:
    CONFIG = load(file)
    print()



LOG_FILE = ('logs', 'log.txt')
LOG_FILE = join(
    pardir, LOG_FILE[0], LOG_FILE[1]
)
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "__%(name)s__: %(asctime)s __%(levelname)s__   \n%(message)s"

logging.basicConfig(
    level=LOG_LEVEL,
    filename=LOG_FILE,
    filemode='a',
    format=LOG_FORMAT
)

log_app = logging.getLogger('app')
