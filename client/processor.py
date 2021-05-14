import logging
from multiprocessing import Process, Queue
from os import environ
import re

logging.basicConfig(level=logging.DEBUG if environ.get('DEBUG', 'false').lower() == 'true' else logging.INFO,
                    format='%(processName)s[%(process)d] %(levelname)s %(message)s')
log = logging.getLogger()


class Worker(Process):

    def __init__(self, inbound: Queue = None, outbound: Queue = None, **kwargs):
        super().__init__(name='Worker', **kwargs)

        self.inbound = inbound
        self.outbound = outbound

    def run(self) -> None:
        while True:
            message = self.inbound.get()

            if message is None:
                log.debug('Queue empty, waiting for messages')
                continue

            log.info(f"Processing message: {message}")

            # Do some magic
            match = re.match(r'^say good night (?P<raquel>\w+)', message['data']['text'], re.I)
            if match:
                response = {
                    'type': 'message',
                    'data': {
                        'author': 'worker',
                        'text': f"Good night {match.group('raquel')}"
                    }
                }
                log.debug(f"Passing reply into outbound queue")
                self.outbound.put(response)
