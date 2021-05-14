import logging
from multiprocessing import Queue
from os import environ
from time import sleep
from wsclient import WSClient
from processor import Worker


logging.basicConfig(level=logging.DEBUG if environ.get('DEBUG', 'false').lower() == 'true' else logging.INFO,
                    format='%(processName)s[%(process)d] %(levelname)s %(message)s')
log = logging.getLogger()


if __name__ == '__main__':

    inbound = Queue()
    outbound = Queue()

    client_process = WSClient(inbound=inbound, outbound=outbound)
    client_process.start()

    worker_process = Worker(inbound=inbound, outbound=outbound)
    worker_process.start()

    client_process.join()
    worker_process.join()
