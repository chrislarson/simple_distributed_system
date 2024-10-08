import socket
import sys
import argparse
import logging


MAX_MESSAGE_LENGTH = 3000

if __name__ == "__main__":
    # Logging configuration.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s",
        handlers=[logging.FileHandler("client.log"), logging.StreamHandler()],
    )

    # Command line argument configuration.
    parser = argparse.ArgumentParser(description="Client socket arguments.")
    parser.add_argument("host", nargs=1, type=str, help="The host to connect to.")
    parser.add_argument("port", nargs=1, type=int, help="The port to connect to.")
    parser.add_argument("socktype", nargs=1, type=str, help='The type of socket to use. "tcp" or "udp".')
    parser.add_argument("mode", nargs=1, type=str, help='The mode to use. "send" or "receive".')
    parser.add_argument("filename", nargs="?", type=str, help='If mode is "send", the file to send.')
    args = parser.parse_args()

    HOST = args.host[0]
    PORT = args.port[0]
    SOCKTYPE = args.socktype[0]
    MODE = args.mode[0]
    FILENAME = args.filename

    if MODE.lower() == "send" and FILENAME is None:
        logging.warning("Filename must be supplied in 'send' mode. Exiting")
        sys.exit(1)

    # Create the client socket - UDP or TCP based on command line argument supplied.
    socket_type = socket.SOCK_STREAM if SOCKTYPE.lower() == "tcp" else socket.SOCK_DGRAM
    with socket.socket(socket.AF_INET, socket_type) as sock:

        # Connect to server.
        sock.connect((HOST, PORT))

        # If mode is "send", read the file contents and send them to the server.
        if MODE.lower() == "send":
            data = ""
            with open(FILENAME, "r") as f:
                data = f.read()
            sock.sendall(bytes(data + "\n", "utf-8"))
            logging.info("Sent: {} bytes".format(len(data)))

        # If mode is "receive", poll server for message and wait for response.
        elif MODE.lower() == "receive":
            # Send request to get message from server.
            sock.sendall(bytes("<<GET>>", "utf-8"))
            # Wait for response from server.
            received = str(sock.recv(MAX_MESSAGE_LENGTH), "utf-8")
            logging.info("Received: \n {}".format(received))

        # Else, invalid mode specified.
        else:
            logging.error("Invalid mode '{}' specified. Exiting".format(MODE))
            sys.exit(1)
