# TCP/UDP server and client applications in Python.

## Description

This is a simple distributed systems application that utilizes two programs: (1) a multi-threaded TCP/UDP server, and (2) a TCP/UDP client application, both written in Python. The server and client can each be started in either TCP or UDP mode.

The server maintains a thread-safe FIFO queue of messages that were sent to it by clients. If the client is started in "send" mode, a filename must be supplied, and the contents will be sent by the client to the server and stored in the server's queue. If the client is started in "receive" mode, the server will send the client the message that has been stored in the server queue the longest; if nothing is in the server's queue, the server will send the client an error message indicating there are no messages.

## Installation

Requirements: Python 3.8 or higher (tested with Python 3.8.10).

## Usage

**Server:**

_Overview:_

```bash
$ python3 server.py [PORT] [TCP|UDP]
```

_Getting help:_

```bash
$ python3 server.py -h

usage: server.py [-h] port socktype

Server socket arguments.

positional arguments:
  port        The port to connect to.
  socktype    The type of socket to use. "TCP" or "UDP".

optional arguments:
  -h, --help  show this help message and exit
```

**Server examples:**

_Starting TCP server:_

```bash
$ python3 server.py 55556 TCP

2024-08-29 17:37:53,230 [INFO] [MainThread] Server started on 127.0.0.1:55556
```

_Starting UDP server:_

```bash
$ python3 server.py 55556 UDP

2024-08-29 17:37:53,230 [INFO] [MainThread] Server started on 127.0.0.1:55556
```

**Client:**

_Overview:_

```bash
$ python3 client.py [SERVER_HOST] [SERVER_PORT] [TCP|UDP] [SEND|RECEIVE] [FILENAME]
```

_Getting help:_

```bash
$ python3 client.py -h

usage: client.py [-h] host port socktype mode [filename]

Client socket arguments.

positional arguments:
  host        The host to connect to.
  port        The port to connect to.
  socktype    The type of socket to use. "TCP" or "UDP".
  mode        The mode to use. "send" or "receive".
  filename    If mode is "send", the file to send.

optional arguments:
  -h, --help  show this help message and exit
```

**Client examples:**

_Start in Send mode:_

```bash
$ python3 client.py 127.0.0.1 55556 TCP send data/message1.txt

2024-08-29 17:38:01,779 [INFO] [MainThread] Sent: 41 bytes
```

_Start in Receive mode:_

```bash
$ python3 client.py 127.0.0.1 55556 TCP receive

2024-08-29 17:38:25,215 [INFO] [MainThread] Received: 
 This is message one. I am 41 characters.
```

## Assumptions

* No messages are longer than 3000 bytes. This requirement was supplied. The client is capable of sending more than 3000 bytes, but both server and client reception buffers are limited to 3000.
* No failures, and the server is persistent. The queue does not need to persist between executions of the server.
* No messages begin with the cstring ``<<GET>>``. This is a header used by the server to determine if the client is requesting a message from the server, which helps account for 0 byte message files, which are considered valid.

## Design

* Server:
    - Python's built-in socketserver module and threaded-mixins are used to create a multi-threaded TCP or UDP server based on the user's input parameter.
    - Python's built-in thread-safe queue (`queue.Queue`) is used for the FIFO queue.
    - Upon connecting to a client socket, the server parses the client's supplied message data. If the message begins with `<<GET>>`, the server acknowledges the request as a desire from the client to receive a message, gets the first value from the queue (if available), and sends it to the client. If no messages are available in the queue an error message noting the lack of messages is sent to the client.
    - The server remains up and listening until a KeyboardInterrupt is supplied.

* Client:
    - Python's built-in socket module is used to create either a UDP or TCP socket based on the user's input parameter.
    - Python's built-in argparse module is used to parse the user's command line inputs.
    - If the user supplied "send" as mode, the code attempts to open the supplied filename, and sends it as bytes over the socket of the type the user specified. If the user supplied "receive" as mode, the client waits for a response from the server.

## How to test

1. **Launch the server** in either TCP or UDP mode

```bash
$ python3 server.py 55556 TCP

2024-08-29 17:37:53,230 [INFO] [MainThread] Server started on 127.0.0.1:55556
```

2. **Verify message sending capability.** In new terminal(s), launch clients of the same socket type in "send" mode. Sample messages are included in the data directory.

```bash
$ python3 client.py localhost 55556 TCP send data/message1.txt

2024-08-29 17:54:03,467 [INFO] [MainThread] Sent: 41 bytes
```

```bash
$ python3 client.py localhost 55556 TCP send data/message2.txt

2024-08-29 17:54:06,145 [INFO] [MainThread] Sent: 3000 bytes
```

```bash
$ python3 client.py localhost 55556 TCP send data/message3.txt

2024-08-29 17:54:06,145 [INFO] [MainThread] Sent: 3000 bytes
```

3. **Verify message receipt capability.** In new terminal(s), launch clients of the same socket type in "receive" mode. Verify no two clients receive the same return message, and that error notice arrives when queue is empty.

```bash
$ python3 client.py localhost 55556 TCP receive

2024-08-29 17:58:04,518 [INFO] [MainThread] Received: 
 This is message one. I am 41 characters.
```

```bash
$ python3 client.py localhost 55556 TCP receive

2024-08-29 17:58:17,496 [INFO] [MainThread] Received: 
 Hello server, this is message two... I am exactly 3000 characters <truncated>...
```

```bash
$ python3 client.py localhost 55556 TCP receive

2024-08-29 17:58:46,360 [INFO] [MainThread] Received: 
 Hello server, this is message three... I am over 3000 characters <truncated>...
```

```bash
$ python3 client.py localhost 55556 TCP receive

2024-08-29 17:59:09,613 [INFO] [MainThread] Received: 
 Error - no messages in queue.
```

## Testing completed

* Functional tests were conducted on Debian 12 using Python 3.8.10.
* Server:
    - Tested in both TCP and UDP modes.
    - Tested with multiple clients sending messages to the server, each receiving a thread.
* Client:
    - Tested in both TCP and UDP modes.
    - Tested in both send and receive modes.
* Messages:
    - Length of 0 was tested (data/message0.txt).
    - Length of 3000 was tested (data/message2.txt).
    - Length of (0, 3000) was tested (data/message1.txt).
    - Length of >3000 was tested to ensure stability (data/message3.txt).
    - Messages were confirmed to be sent and received in the order they were sent.
