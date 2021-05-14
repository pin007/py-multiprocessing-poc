import json
import logging
from multiprocessing import Process, Queue
from os import environ
from threading import Thread

import websocket
from websocket import ABNF

logging.basicConfig(level=logging.DEBUG if environ.get('DEBUG', 'false').lower() == 'true' else logging.INFO,
                    format='%(processName)s[%(process)d] %(levelname)s %(message)s')
log = logging.getLogger()


class WSClient(Process):

    def __init__(self, inbound: Queue = None, outbound: Queue = None, **kwargs):
        super().__init__(name='WSClient', **kwargs)

        self.url = environ.get('SERVER_URL', 'ws://127.0.0.0:3000')
        self.ping_interval = int(environ.get('PING_INTERVAL', '0'))
        self.ping_timeout = int(environ.get('PING_TIMEOUT', '0'))

        self.inbound = inbound
        self.outbound = outbound
        self.connected = False

        self.client = websocket.WebSocketApp(
            self.url,
            on_close=self.on_close,
            on_error=self.on_error,
            on_message=self.on_message,
            on_open=self.on_open,
            on_ping=self.on_ping,
            on_pong=self.on_pong,
            **kwargs)

    def run(self) -> None:
        def outbound_consumer(client: WSClient):
            while True:
                if client.connected:
                    message = client.outbound.get()
                    client.send_message(message)
        Thread(target=outbound_consumer, args=(self,)).start()

        self.client.run_forever(ping_interval=self.ping_interval, ping_timeout=self.ping_timeout)

    def close(self) -> None:
        self.connected = False
        self.client.close()
        super(self).close()

    def on_close(self, ws, code, reason) -> None:
        log.info(f"Connection closed: [{code}] {reason}")
        self.close()

    def on_error(self, ws, error: BaseException) -> None:
        log.exception(f"Error occurred {error}", exc_info=error)

    def on_message(self, ws, payload: str) -> None:
        message = json.loads(payload)
        log.info(f"Received message: {message}")

        if self.inbound and message['type'] == 'message':
            log.debug('Passing message into inbound queue')
            self.inbound.put(message)

    def on_open(self, ws) -> None:
        log.info('Connection opened')
        self.connected = True

    def on_ping(self, ws, data) -> None:
        log.debug('Ping received')
        self.client.send(data, ABNF.OPCODE_PONG)

    def on_pong(self, ws, data) -> None:
        log.debug('Pong received')

    def send_message(self, message: object) -> None:
        payload = json.dumps(message)
        self.client.send(payload, ABNF.OPCODE_TEXT)
