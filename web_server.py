import socket
import sys
import time
import threading
from rest_api import RestAPI

# Test DB
DATABASE = {
    "users": [
        {
          "name": "Adam",
          "owes": {
            "Bob": 12.0,
            "Chuck": 4.0,
            "Dan": 9.5
          },
          "owed_by": {
            "Bob": 6.5,
            "Dan": 2.75,
          },
          "balance": -15.25
        },
        {
          "name": "Chuck",
          "owes": {
            "Bob": 12.0,
            "Dan": 9.5
          },
          "owed_by": {
            "Bob": 6.5,
            "Dan": 2.75,
          },
          "balance": -10.75 #"<(total owed by other users) - (total owed to other users)>"
        }
    ]
}


class WebServer(object):
    """
    Class for describing simple HTTP server objects
    """

    def __init__(self, host="localhost", port=8080):
        self.host = host
        self.port = port

    def start(self):
        """
        Attempts to create and bind a socket to launch the server
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            print(f"Starting server on {self.host}:{self.port}")
            self.socket.bind((self.host, self.port))
            print(f"Server started on port {self.port}.")

        except Exception as e:
            print(f"Error: Could not bind to port {self.port}")
            self.shutdown()
            sys.exit(1)

        self._listen() # Start listening for connections

    def shutdown(self):
        """
        Shuts down the server
        """
        try:
            print("Shutting down server")
            self.socket.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            pass # Pass if socket is already closed

    def _generate_headers(self, response_code):
        """
        Generate HTTP response headers.
        Parameters:
            - response_code: HTTP response code to add to the header. 200 and 404 supported
        Returns:
            A formatted HTTP header for the given response_code
        """
        header = ''
        if response_code == 200:
            header += 'HTTP/1.1 200 OK\n'
        elif response_code == 404:
            header += 'HTTP/1.1 404 Not Found\n'

        time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        header += f'Date: {time_now}\n'
        header += 'Server: Simple-Python-Server\n'
        header += 'Connection: close\n\n' # Signal that connection will be closed after completing the request
        return header

    def _listen(self):
        """
        Listens on self.port for any incoming connections
        """
        self.socket.listen(5)
        while True:
            (client, address) = self.socket.accept()
            client.settimeout(3)
            print(f"Received connection from {address}")
            threading.Thread(target=self._handle_client, args=(client, address)).start()

    def _handle_client(self, client, address):
        """
        Main loop for handling connecting clients and serving files from content_dir
        Parameters:
            - client: socket client from accept()
            - address: socket address from accept()
        """
        packet_size = 1024
        while True:
            print("CLIENT", client)
            data = client.recv(packet_size).decode()  # Receive data packet from client and decode

            if not data: break

            request = data.split(' ')
            request_method = request[0]  # GET
            endpoint = request[1]  # /users

            (req_headers, req_body) = data.split("\r\n\r\n")

            fields = req_headers.split("\r\n")
            fields = fields[1:]  # ignore the first line which was already checked: GET / HTTP/1.1

            headers = {}
            for field in fields:
                key, value = field.split(': ')  # split each line by http field name and value
                headers[key] = value

            print(f"Request:\n{[request_method, endpoint]}\nHeaders:\n{headers}\nBody:\n{req_body}\n------\n")

            if request_method == "GET" or request_method == "POST":
                api = RestAPI(DATABASE)
                try:
                    if request_method == "GET" and endpoint == "/users":
                        response_header = self._generate_headers(200)
                        response = response_header.encode()
                        response += api.get(endpoint, req_body)

                    elif request_method == "POST" and data and endpoint in ["/add", "/iou"]:
                        response_header = self._generate_headers(200)
                        response = response_header.encode()
                        response += api.post(endpoint, req_body)

                except Exception as e:
                    print(e)
                    response_header = self._generate_headers(404)
                    response = response_header.encode()
                    if request_method == "GET" or request_method == "POST":  # General error
                        response_data = f"<html><body><center><h1>Something went wrong</h1></center><p>Error message: {e}</p></body></html>"
                        response += response_data.encode()

                client.send(response)
                client.close()
                break

            else:
                print(f"Unknown HTTP request method: {request_method}")