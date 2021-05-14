# py-multiprocessing-poc

PoC of Python multiprocessing library that simulates several processes, which are communicating using queues.

`wsmock` is WebSocket server that is used as source of data for `wsclient`. Inbound messages are queued for worker
to process. Worker `processor` manages inbound messages and if they match special format it replies through outbound queue. 

Run PoC using docker compose: 
```shell
docker-compose up
```

Force rebuild of docker images
```shell
docker-compose up --build
```

For interaction with worker use web based client `ws-mock/index.html` and use message `Say good night <your name here>`.
