from ServiceClasses import ServiceSender

import os
import logging
from multiprocessing import Queue
from json import load


if not os.path.exists(setting_configuration['logs_path']):
    print(os.path.abspath(setting_configuration['logs_path']))
    os.mkdir(setting_configuration['logs_path'])

log_file = os.path.join(
    setting_configuration['logs_path'],
    setting_configuration['logs_file']
)

logging.basicConfig(
    level=logging.DEBUG,
    filename=log_file,
    filemode='a',
    format="__%(name)s__: %(asctime)s __%(levelname)s__   \n%(message)s"
)


