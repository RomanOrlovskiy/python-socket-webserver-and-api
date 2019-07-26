import sys
import signal
from web_server import WebServer


def shutdownServer(sig, unused):
    """
    Shutsdown server from a SIGINT recieved signal
    """
    server.shutdown()
    sys.exit(1)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdownServer)
    server = WebServer("localhost", 8080)
    server.start()
    print("Press Ctrl+C to shut down server.")