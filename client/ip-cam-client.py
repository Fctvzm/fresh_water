import json
import logging
import threading
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
from twisted.internet.protocol import ReconnectingClientFactory

import configs
import utils

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename=configs.LOGGING_FILE, level=logging.DEBUG)


class StreamConnection:
    def run(self, socket_protocol):
        thread = threading.Thread(target=utils.use_mjpg_con, args=(socket_protocol, configs.MJPG_IP_CAM_URL,
                                                                   configs.MJPG_USERNAME, configs.MJPG_PASSWORD))
        thread.daemon = True  # Daemonize thread
        thread.start()


class AppProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        logging.info("Connected to the server")
        self.factory.resetDelay()

        stream_conn = StreamConnection()
        stream_conn.run(self)

    def onOpen(self):
        logging.info("Connection is open.")

    def onMessage(self, payload, isBinary):
        if (isBinary):
            logging.info("Got Binary message {0} bytes".format(len(payload)))
        else:
            data = payload.decode('utf8')
            msg_data = json.loads(data)
            if msg_data['type'] == 'RECOGNIZED' and msg_data['name'] != configs.NOT_RECOGNIZED:
                logging.info("Got Text message from the server {0}".format(data))

    def onClose(self, wasClean, code, reason):
        logging.info("Connect closed {0}".format(reason))


class AppFactory(WebSocketClientFactory, ReconnectingClientFactory):
    protocol = AppProtocol

    def clientConnectionFailed(self, connector, reason):
        logging.info("Unable connect to the server {0}".format(reason))
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        logging.info("Lost connection and retrying... {0}".format(reason))
        self.retry(connector)


if __name__ == '__main__':
    import sys
    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)
    factory = AppFactory(configs.SOCKET_URL)
    reactor.connectTCP(configs.SOCKET_SERVER, configs.SOCKET_PORT, factory)
    reactor.run()
