from . import weather_clf

from flask import request
from flask import current_app

from .classify import SeaStateCLF
from .utils.config import return_dict

from flask_httpauth import HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@weather_clf.route('/classify', methods=['GET'])
def classify():
    if request.method == "GET":
        current_app.logger.error("clf Error msg----1")
        current_app.logger.error("clf Error msg----2")
        current_app.logger.error("clf Error msg----3")
        current_app.logger.info('INFO: classify GET.')
        wind_speed = float(request.args.get('wind_speed'))
        wave_height = float(request.args.get('wave_height'))
        current_app.logger.info(f'INFO: classify GET wind_speed={wind_speed} & wave_height={wave_height}.')

        est = SeaStateCLF(
                wind_speed=wind_speed,
                wave_height=wave_height
            )
        level = est.clf()
        return_dict['success']['data'] = {'level': level}
        return return_dict['success']

    return 'classify'
