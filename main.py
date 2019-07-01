import json
import logging
import os

from controller import Controller


def get_token(name):
    config_file_name = 'config.json'
    try:
        if os.path.isfile(config_file_name):
            with open(config_file_name) as config_file:
                config = json.load(config_file)
            if config.__contains__(name):
                return config[name]
            else:
                print('CRITICAL: cannot get token in config file ' + name)
                logging.critical('Cannot get token in config file ' + name)
        else:
            if os.environ.__contains__(name):
                return os.environ[name]
            else:
                print('CRITICAL: cannot get token in OS environment ' + name)
                logging.critical('Cannot get token in OS environment ' + name)
    except Exception as error:
        print('CRITICAL: cannot get token, reason: ' + error.__str__())
        logging.critical('Cannot get token, reason: ' + error.__str__())


logging.basicConfig(filename='logs.log', level=logging.INFO,
                    format='%(asctime)s %(name)-30s %(levelname)-8s %(message)s')


if __name__ == '__main__':
    controller = Controller(get_token('CLARIFAI_TOKEN'), get_token('TELEGRAM_BOT_TOKEN'))
    controller.start()
