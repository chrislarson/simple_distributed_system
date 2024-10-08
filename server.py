import socketserver
import argparse
import queue
import logging
import sys
import socket

MAX_MESSAGE_LENGTH = 3000


# ThreadedTCPServer
# * Uses Python's built-in threading mixin to create a multithreaded TCP server.
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


# ThreadedTCPRequestHandler
# * Handles incoming TCP requests by parsing the first bytes of the message for a <<GET>> header.
# * If <<GET>> header present, return message from queue or empty queue notification. Else, store message.
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        host, port = self.request.getpeername()
        logging.info("Handling incoming request [TCP] from {}:{}".format(host, port))
        data = str(self.request.recv(MAX_MESSAGE_LENGTH), "ascii")
        if data.startswith("<<GET>>"):
            logging.info("-> Client is requesting message from queue (current size: {})".format(message_queue.qsize()))
            response = ""
            try:
                response = message_queue.get(block=False)
            except queue.Empty:
                response = "Error - no messages in queue."
            response = bytes(response, "ascii")
            self.request.sendall(response)
        else:
            logging.info("-> Client sent message to be added to queue")
            message_queue.put(data)
            logging.info("-> Added message to queue (new size: {})".format(message_queue.qsize()))


# ThreadedUDPServer
# * Uses Python's built-in threading mixin to create a multithreaded UDP server.
class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


# ThreadedUDPRequestHandler
# * Handles incoming UDP requests by parsing the first bytes of the message for a <<GET>> header.
# * If <<GET>> header present, return message from queue or empty queue notification. Else, store message.
class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        socket = self.request[1]
        host, port = self.client_address[0], self.client_address[1]
        logging.info("Handling incoming request [UDP] from {}:{}".format(host, port))
        data = str(self.request[0], "ascii")
        if data.startswith("<<GET>>"):
            logging.info("-> Client is requesting message from queue (current size: {})".format(message_queue.qsize()))
            response = ""
            try:
                response = message_queue.get(block=False)
            except queue.Empty:
                response = "Error: No messages."
            response = bytes(response, "ascii")
            socket.sendto(response, self.client_address)
        else:
            logging.info("-> Client sent message to be added to queue")
            message_queue.put(data)
            logging.info("-> Added message to queue (new size: {})".format(message_queue.qsize()))


if __name__ == "__main__":
    # Logging configuration.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s",
        handlers=[logging.FileHandler("server.log"), logging.StreamHandler()],
    )

    # Command line argument configuration.
    parser = argparse.ArgumentParser(description="Server socket arguments.")
    parser.add_argument("port", nargs=1, type=int, help="The port to connect to.")
    parser.add_argument("socktype", nargs=1, type=str, help='The type of socket to use. "tcp" or "udp".')
    args = parser.parse_args()

    PORT = args.port[0]
    SOCKTYPE = args.socktype[0]
    HOST = socket.gethostname()
    logging.info("Server socket type: {}".format(SOCKTYPE))
    logging.info("Server hostname: {}".format(HOST))
    logging.info("Server port: {}".format(PORT))

    # Thread-safe queue.
    message_queue = queue.Queue()

    # Create the and bind the server - UDP or TCP based on command line argument supplied.
    server = (
        ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
        if SOCKTYPE.lower() == "tcp"
        else ThreadedUDPServer((HOST, PORT), ThreadedUDPRequestHandler)
    )

    # Run server until keyboard interrupt.
    with server:
        try:
            ip, port = server.server_address
            logging.info("Server started on {}:{}".format(ip, port))
            server.serve_forever()
        except KeyboardInterrupt:
            logging.info("Shutting down server")
            server.shutdown()
            server.server_close()
            sys.exit(0)
