# MQTT2Postgres
#
# Copyright 2019 Bert Melis
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Using GracefulKiller Jul 2016, Mayank Jaiswal
# https://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully
#

import signal
from threading import Timer
import time
import paho.mqtt.client as mqtt
import postgres
from messagehandler import messagehandler


class gracefullkiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


class repeatedtimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()


    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)


    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True


    def stop(self):
        self._timer.cancel()
        self.is_running = False


def on_connect(client, userdata, flags, rc):
    print('Mqtt connected')
    client.subscribe('basetopic/#', 1)

def on_disconnect(client, userdata, rc=0):
    print('Mqtt disconnected')


def on_message(client, userdata, msg):
    message_handler.onmessage(msg.topic, msg.payload)


if __name__ == '__main__':
    print('starting MQTT2Postgres')

    graceful_killer = gracefullkiller()

    mqttclient = mqtt.Client(client_id="MQTT2Postgres", clean_session=True)
    mqttclient.on_connect = on_connect
    mqttclient.on_disconnect = on_disconnect
    mqttclient.on_message = on_message
    mqttclient.connect_async('mqtt.local', 1883, 5)

    database = postgres.postgres()
    rt = repeatedtimer(5, database.check)

    message_handler = messagehandler()
    message_handler.setdatabase(database)

    # Wait for postgres to connect MQTT.
    # Otherwise retained messages will be processed before the database is
    # ready. Hence we will not be able to store the messages.
    while database is None:
        time.sleep(30)
    mqttclient.loop_start()

    while True:
        if graceful_killer.kill_now:
            break
        time.sleep(1)

    mqttclient.loop_stop()
    rt.stop()
    mqttclient.disconnect()
    print('MQTT2Postgres stopped')
