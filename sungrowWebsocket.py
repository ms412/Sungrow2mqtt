__app__ = "Sungrow Webscoket"
__VERSION__ = "0.2"
__DATE__ = "07.05.2023"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2023 Markus Schiesser"
__license__ = 'GPL v3'

import time
import logging
import websocket
import json




class SungrowWS(object):

    def __init__(self, host: str, logger: str, port: int = 8082, locale: str = "en_US" ):

        _libName = str(__name__.rsplit('.', 1)[-1])
        self._log = logging.getLogger(logger + '.' + _libName + '.' + self.__class__.__name__)

        self._log.debug('Create MQTT mqttclient Object')

        self._host = host
        self._port = port

        self._locale = locale
        self.timeout = '5'
        self._websocket = None
        self._token = ''
        self._data = {}

        self.ws_endpoint = "ws://" + str(self._host) + ":" + str(self._port) + "/ws/home/overview"

    def connect(self):

        self._websocket = websocket.WebSocket()
        self._websocket.connect(self.ws_endpoint)
        self._websocket.send(
            json.dumps(
                {
                    "lang": "en_us",
                    "token": self._token,
                    "service": "connect"
                }
            )
        )
        _data = json.loads(self._websocket.recv())

        if _data['result_msg'] == 'success':
            self._token = _data['result_data']['token']
        else:
            self._log.error('Failed to get a tocken from inverter: ', self._host)
            return False

        return True

    def getData(self):

        self._websocket.send(
            json.dumps(
                {
                    "lang": self._locale,
                    "token": self._token,
                    "service": "devicelist",
                    "type": "0",
                    "is_check_token": "0",
                }
            )
        )
        _data = json.loads(self._websocket.recv())

        if _data['result_msg'] == 'success':
            _dev_id = str(_data['result_data']['list'][0]['dev_id'])
            self._data['INVENTAR'] = _data['result_data']['list']
        else:
            self._log.error('Failed to query inventor data from inverter: ', self._host)
            return False


        self._websocket.send(
            json.dumps(
                {
                    "lang": self._locale,
                    "token": self._token,
                    "service": "direct",
                    "dev_id": _dev_id,
                }
            )
        )
        _data = json.loads(self._websocket.recv())
        if  _data["result_msg"] == "success":
            #print('3',_data)
            self._data['DIRECT'] = _data['result_data']['list']
            _directData = {}
            for item in _data['result_data']['list']:
                _value = [('voltage',item['voltage']),('current',item['current'])]
                _key = item['name']
                _directData[_key] = dict(_value)

            self._data['DIRECT'] = _directData
        else:
            self._log.error('Failed to query DC data from inverter: ', self._host)
            return False

        self._websocket.send(
            json.dumps(
                {
                    "lang": self._locale,
                    "token": self._token,
                    "service": "real",
                    "dev_id": _dev_id,
                }
            )
        )

        _data = json.loads(self._websocket.recv())
        if  _data["result_msg"] == "success":
            _realData = {}
            for item in _data['result_data']['list']:
                _value = [('data_value',item['data_value']),('data_unit',item['data_unit'])]
                _key = item['data_name']
                _realData[_key] = dict(_value)
            self._data['REAL'] = _realData
           # print('4', _realData)
        else:
            self._log.error('Failed to query AC data from inverter: ', self._host)
            return False

        return self._data
