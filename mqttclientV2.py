
__app__ = "MQTT interface"
__VERSION__ = "2.0"
__DATE__ = "18.03.2023"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2021 Markus Schiesser"
__license__ = 'GPL v3'

import os
import time
import uuid
import logging
import paho.mqtt.client as mqtt


class mqttclient(object):

    def __init__(self,logger):

        _libName = str(__name__.rsplit('.', 1)[-1])
        self._log = logging.getLogger(logger + '.' + _libName + '.' + self.__class__.__name__)

        self._log.debug('Create MQTT mqttclient Object')

        self._mqttc = None

        self._state = 'INITIAL'

    def connect(self,host,port=1883,**options):
        self._log.debug('Methode: connect with options(%s, %s, %s)' % (host,port,options))

        #if options.get('clientId',False):
         #   _clientId = str(uuid.uuid4())

        #else:
         #   _clientId = options.get('clientId')
         #   clean_session = False
        #print(_clientId)

        _clientId = options.get('clientId',str(uuid.uuid4()))

        print(_clientId)

        #self._mqttc = mqtt.Client(options.get("clientId",None),clean_session=False)
        self._mqttc = mqtt.Client(_clientId, clean_session= False)

        if options.get("username") and options.get("password"):
            self._mqttc.username_pw_set(options.get("username"),options.get("password"))

        self._mqttc.on_message = self.on_message
        self._mqttc.on_connect = self.on_connect
        self._mqttc.on_publish = self.on_publish
        self._mqttc.on_subscribe = self.on_subscribe
        self._mqttc.on_disconnect = self.on_disconnect
        self._mqttc.on_log =  self.on_log()

        try:
            self._mqttc.connect(host,int(port),options.get("keepalive",60))
            self._mqttc.loop_start()
            self._log.info('Connected to mqtt with ClientID(%s, %s)' % (host, _clientId))
            return True
        except OSError:
            self._log.error('Methode: connect Failed')

            return False


    def subscribe(self,topic,callback=None):
        if callback:
            print('add callback')
            self._mqttc.message_callback_add(topic,callback)

        (_result, _mid) = self._mqttc.subscribe(topic)

    def publish(self,topic,payload,retain=False):
        self._log.debug('Methode: publish(%s, %s, %s)' % (topic,payload,retain))

        (_result,_mid) = self._mqttc.publish(topic,payload,qos=0,retain=retain)

        if _result == mqtt.MQTT_ERR_SUCCESS:
            self._log.debug("Message {} queued successfully.".format(_mid))
          #  if _mid.wait_for_publish():
           #     self._log.debug("Message {} queued successfully.".format(_mid))
           # else:
            #    self._log.error("Failed to publish message. Error: {}".format(_result))
        else:
            self._log.error("Failed to publish message. Error: {}".format(_result))

        return False

    def on_message(self,client,userdata,message):
        self._log.debug('Methode: on_message(%s, %s, %s)' % (client, userdata, message))
        #    print("Received message '" + str(message.payload) + "' on topic '"
        #         + message.topic + "' with QoS " + str(message.qos))
        #self._log.debug('Received message Topic: {}'.format(message.topic))
        return message

    def on_connect(self,client,userdata,flags,rc):
        self._log.debug('Methode: on_connect(%s, %s, %s , %s' % (client, userdata, flags, rc))

        if rc == mqtt.CONNACK_ACCEPTED:
            self._log.debug('MQTT connected')
           # if self._state == 'DISCONNECTED':
            #    self._log.debug('RECONNECT')
              #  self._state = 'CONNECTED'
             #   self._mqttc.reconnect()
            #else:
             #   self._state = 'CONNECTED'
         #   self._mqttc.reconnect()
          #  self._state['CONNECTED'] = True
        else:
            self._log.error('MQTT failed to connect: {}'.format(rc))
         #   self._state['CONNECTED'] = False):

    def on_publish(self, client, userdata, mid):
        self._log.debug('Methode: on_publish(%s, %s, %s)' % (client, userdata, mid))
      #  self._state['PUBLISHED'] =mid
        return True

    def on_subscribe(self,mqttc,obj,mid,granted_qos):
        print('Methode: on_subscribe(%s, %s, %s, %s)' % (mqttc, obj, mid, granted_qos))
        return True

    def disconnect(self):
        self._log.debug('Methode: disconnect()')
        #   self._mqttc.wait_for_publish()
        self._mqttc.disconnect()
        return True

    def on_disconnect(self, client, userdata, rc):
        self._log.debug('Methode: on_dissconnect(%s, %s, %s)' % (client, userdata, rc))
        if rc != 0:
            self._log.error('Unexpected disconnection.')
            #self._state = 'DISCONNECTED'
        return True

    def on_log(self):
        pass


class callmeback(object):

    def callback1(self, client, userdata, msg):
        print('callmeback1', client, userdata, msg)
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    def callback2(self, client, userdata, msg):
        print('callmeback2', client, userdata, msg)
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        _type = msg.topic.split('/')[-1]
        print(_type)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('mqttclient')

    callme = callmeback()

    mqttc = mqttclient('xx')

    _host = '192.168.2.20'
    _port =1883

    _state = False
    while not _state:
        _state = mqttc.connect(_host,_port)
        print(_state)
        if not _state:
            print('Failed to connect to broker: %s', _host)
            time.sleep(5)

    if not mqttc.connect('192.168.2.20',clientId='wwwer'):
        print('Failed to conneft')
        exit(1)
   # time.sleep(10)
    mqttc.subscribe('TEST1/#')
    mqttc.publish('/TEST3/T','ddddd',True)
    time.sleep(20)
    mqttc.subscribe('TEST2/#',callme.callback2)
    x = 0
    while True:
       # print(x)
        mqttc.publish('/TEST3/TE',x,True)
        x = x+1
        time.sleep(5)
        #pass