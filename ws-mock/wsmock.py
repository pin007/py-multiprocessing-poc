import asyncio
import json
import logging
from os import environ
import random
import signal
import websockets

logging.basicConfig(level=logging.DEBUG if environ.get('DEBUG', 'false').lower() == 'true' else logging.INFO,
                    format='%(processName)s[%(process)d] %(levelname)s %(message)s')
log = logging.getLogger()


class MockServer(object):

    def __init__(self):
        self.bind = environ.get('BIND', '0.0.0.0')
        self.port = environ.get('PORT', '3000')
        self.clients = set()

    async def ehlo(self, websocket):
        while True:
            log.info(f"Sending ehlo message to {websocket.remote_address}")
            await websocket.send(json.dumps({'type': 'ehlo'}))
            await asyncio.sleep(random.random() * 10)

    async def echo(self, websocket):
        async for payload in websocket:
            message = json.loads(payload)
            log.info(f"Received message from {websocket.remote_address}: {message}")
            if message['type'] == 'message':
                log.info('Broadcasting message to known clients')
                for client in self.clients:
                    await client.send(
                        json.dumps({
                            'type': 'message',
                            'data': {
                                'author': message['data']['author'] if 'author' in message['data'] else websocket.remote_address,
                                'text': message['data']['text']}}))

    async def handler(self, websocket, path):
        self.clients.add(websocket)
        try:
            log.info(f"Connected new client on {websocket.remote_address}")
            ping_task = asyncio.ensure_future(self.ehlo(websocket))
            echo_tasks = asyncio.ensure_future(self.echo(websocket))
            done, pending = await asyncio.wait([ping_task, echo_tasks], return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()
        finally:
            self.clients.remove(websocket)
            log.info(f"Client on {websocket.remote_address} disconnected")

    async def run(self, stop):
        log.info(f"Starting Websocket Mock server on {self.bind}:{self.port}")
        async with websockets.serve(self.handler, self.bind, self.port):
            await stop


if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    stop_event = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop_event.set_result, None)

    mock = MockServer()
    asyncio.get_event_loop().run_until_complete(mock.run(stop_event))
